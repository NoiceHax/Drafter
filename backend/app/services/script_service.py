"""ScriptService → LLMProvider (full script + single-scene regeneration)."""
from __future__ import annotations

import json
import uuid

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AppError, NotFoundError
from app.models.enums import ProjectStage, RevisionTarget
from app.models.models import ContentProject, Script, ScriptScene
from app.prompts import scene_regeneration, script_generation
from app.providers.llm import ChatMessage, LLMProvider
from app.schemas.llm import ScriptOut, SceneOut
from app.services.base import build_context, log_revision
from app.services.duration import estimate_duration_seconds


class ScriptService:
    def __init__(self, db: Session, llm: LLMProvider):
        self.db = db
        self.llm = llm
        self.wpm = settings.words_per_minute

    def generate(
        self, project: ContentProject, *, instruction: str | None = None
    ) -> Script:
        if project.outline is None:
            raise AppError("Generate a story outline before the script.", code="outline_required")

        outline_text = json.dumps(
            {
                "narrative_structure": project.outline.narrative_structure,
                "estimated_duration_seconds": project.outline.estimated_duration_seconds,
                "sections": project.outline.sections,
            },
            indent=2,
        )
        prompt = script_generation.build(
            context=build_context(project),
            outline=outline_text,
            words_per_minute=self.wpm,
            instruction=instruction,
        )
        result = self.llm.generate_structured(
            [ChatMessage(role="user", content=prompt)], ScriptOut, max_tokens=2800
        )

        # Recreate the script and its scenes.
        if project.script is not None:
            self.db.delete(project.script)
            self.db.flush()

        script = Script(
            project_id=project.id,
            title=result.title,
            platform=project.platform,
            target_duration_seconds=project.target_duration_seconds,
            hook_text=result.hook.text,
            hook_duration_seconds=result.hook.duration_seconds
            or estimate_duration_seconds(result.hook.text, self.wpm),
            cta_text=result.cta.text if result.cta else None,
            cta_duration_seconds=(
                result.cta.duration_seconds
                or estimate_duration_seconds(result.cta.text, self.wpm)
            )
            if result.cta
            else 0,
        )
        self.db.add(script)
        self.db.flush()

        self._materialize_scenes(script, result.scenes)
        # Ensure the scenes relationship reflects the just-added rows before we
        # compute the timeline-based duration estimate.
        self.db.flush()
        self.db.refresh(script)
        script.estimated_duration_seconds = self._recompute_estimate(script)

        project.current_stage = ProjectStage.script
        log_revision(
            self.db,
            project_id=project.id,
            target=RevisionTarget.script,
            instruction=instruction,
            after={"title": script.title, "scenes": len(script.scenes)},
        )
        self.db.commit()
        self.db.refresh(script)
        return script

    def regenerate_scene(
        self,
        scene: ScriptScene,
        project: ContentProject,
        *,
        field: str = "all",
        instruction: str | None = None,
    ) -> ScriptScene:
        before = {
            "narration": scene.narration,
            "visual_direction": scene.visual_direction,
            "on_screen_text": scene.on_screen_text,
        }
        scene_json = json.dumps(
            {
                "scene_number": scene.scene_number,
                "start_time": scene.start_time,
                "end_time": scene.end_time,
                "section_type": scene.section_type,
                "narration": scene.narration,
                "on_screen_text": scene.on_screen_text,
                "visual_direction": scene.visual_direction,
            },
            indent=2,
        )
        prompt = scene_regeneration.build(
            context=build_context(project),
            scene_json=scene_json,
            field=field,
            words_per_minute=self.wpm,
            instruction=instruction,
        )
        new = self.llm.generate_structured(
            [ChatMessage(role="user", content=prompt)], SceneOut
        )

        if field in ("narration", "all"):
            scene.narration = new.narration
        if field in ("visual_direction", "all"):
            scene.visual_direction = new.visual_direction
        if field == "all" and new.on_screen_text is not None:
            scene.on_screen_text = new.on_screen_text

        # Refresh script duration estimate.
        if scene.script:
            scene.script.estimated_duration_seconds = self._recompute_estimate(scene.script)

        target = (
            RevisionTarget.scene_visual_direction
            if field == "visual_direction"
            else RevisionTarget.scene_narration
        )
        log_revision(
            self.db,
            project_id=project.id,
            target=target,
            entity_id=scene.id,
            instruction=instruction,
            before=before,
            after={
                "narration": scene.narration,
                "visual_direction": scene.visual_direction,
                "on_screen_text": scene.on_screen_text,
            },
        )
        self.db.commit()
        self.db.refresh(scene)
        return scene

    def edit_scene(
        self,
        scene: ScriptScene,
        *,
        narration: str | None = None,
        on_screen_text: str | None = None,
        visual_direction: str | None = None,
    ) -> ScriptScene:
        if narration is not None:
            scene.narration = narration
        if on_screen_text is not None:
            scene.on_screen_text = on_screen_text
        if visual_direction is not None:
            scene.visual_direction = visual_direction
        if scene.script:
            scene.script.estimated_duration_seconds = self._recompute_estimate(scene.script)
        self.db.commit()
        self.db.refresh(scene)
        return scene

    def edit_script(
        self,
        script: Script,
        *,
        title: str | None = None,
        hook_text: str | None = None,
        cta_text: str | None = None,
    ) -> Script:
        """Edit script-level fields (title, hook, CTA) that live on the Script,
        not on an individual scene. Re-estimates duration when the hook/CTA
        wording changes since that affects narration length."""
        if title is not None:
            script.title = title
        if hook_text is not None:
            script.hook_text = hook_text
            script.hook_duration_seconds = estimate_duration_seconds(hook_text, self.wpm)
        if cta_text is not None:
            script.cta_text = cta_text
            script.cta_duration_seconds = estimate_duration_seconds(cta_text, self.wpm)
        script.estimated_duration_seconds = self._recompute_estimate(script)
        self.db.commit()
        self.db.refresh(script)
        return script

    # ── helpers ─────────────────────────────────────────────────────────────
    def _materialize_scenes(self, script: Script, scenes: list[SceneOut]) -> None:
        cursor = script.hook_duration_seconds
        for s in scenes:
            duration = max(1, (s.end_time - s.start_time)) if s.end_time > s.start_time else (
                estimate_duration_seconds(s.narration, self.wpm)
            )
            start = s.start_time if s.end_time > s.start_time else cursor
            end = s.end_time if s.end_time > s.start_time else start + duration
            cursor = end
            self.db.add(
                ScriptScene(
                    script_id=script.id,
                    scene_number=s.scene_number,
                    start_time=start,
                    end_time=end,
                    section_type=s.section_type,
                    narration=s.narration,
                    on_screen_text=s.on_screen_text,
                    visual_direction=s.visual_direction,
                )
            )

    def _recompute_estimate(self, script: Script) -> int:
        """Estimate total duration.

        Prefer the explicit scene timeline (last scene end_time) when the model
        provided coherent timings, otherwise fall back to summing narration at
        the configured words-per-minute. Whichever is larger wins, so a script
        whose narration is terse but whose timeline is paced still reflects the
        intended runtime.
        """
        wpm_total = script.hook_duration_seconds + (script.cta_duration_seconds or 0)
        for scene in script.scenes:
            wpm_total += estimate_duration_seconds(scene.narration, self.wpm)

        timeline_end = 0
        for scene in script.scenes:
            timeline_end = max(timeline_end, scene.end_time)
        timeline_total = timeline_end + (script.cta_duration_seconds or 0)

        return max(wpm_total, timeline_total)
