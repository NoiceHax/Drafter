"""HookService → LLMProvider."""
from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.models.enums import HookArchetype, ProjectStage, RevisionTarget
from app.models.models import ContentProject, Hook
from app.prompts import hook_generation, hook_regeneration
from app.providers.llm import ChatMessage, LLMProvider
from app.schemas.llm import HookGenerationOut, HookOut
from app.services.base import build_context, log_revision


class HookService:
    def __init__(self, db: Session, llm: LLMProvider):
        self.db = db
        self.llm = llm

    def generate(
        self, project: ContentProject, *, instruction: str | None = None
    ) -> tuple[list[dict], list[Hook], uuid.UUID | None]:
        prompt = hook_generation.build(
            context=build_context(project, include_hook=False),
            instruction=instruction,
        )
        result = self.llm.generate_structured(
            [ChatMessage(role="user", content=prompt)], HookGenerationOut
        )

        analysis = [a.model_dump(mode="json") for a in result.analysis]

        for h in list(project.hooks):
            self.db.delete(h)
        self.db.flush()

        created: list[Hook] = []
        for hook in result.hooks:
            row = Hook(
                project_id=project.id,
                text=hook.text,
                archetype=hook.archetype,
                suitability_score=max(0.0, min(1.0, hook.suitability_score)),
                estimated_duration_seconds=hook.estimated_duration_seconds or 6,
                unanswered_question=hook.unanswered_question,
                story_payoff=hook.story_payoff,
                reason=hook.reason,
                analysis=analysis,
            )
            self.db.add(row)
            created.append(row)
        self.db.flush()

        recommended_id: uuid.UUID | None = None
        if created:
            idx = result.recommended_index if 0 <= result.recommended_index < len(created) else 0
            recommended_id = created[idx].id

        project.selected_hook_id = None
        if project.current_stage in (ProjectStage.angles, ProjectStage.hooks):
            project.current_stage = ProjectStage.hooks
        log_revision(
            self.db,
            project_id=project.id,
            target=RevisionTarget.hooks,
            instruction=instruction,
            after={"count": len(created)},
        )
        self.db.commit()
        for row in created:
            self.db.refresh(row)
        return analysis, created, recommended_id

    def select(self, project: ContentProject, hook_id: uuid.UUID) -> Hook:
        chosen = None
        for h in project.hooks:
            h.selected = h.id == hook_id
            if h.selected:
                chosen = h
        if chosen is None:
            raise NotFoundError("Hook not found in this project.")
        project.selected_hook_id = hook_id
        if project.current_stage == ProjectStage.hooks:
            project.current_stage = ProjectStage.research
        self.db.commit()
        self.db.refresh(chosen)
        return chosen

    def regenerate(
        self,
        project: ContentProject,
        hook_id: uuid.UUID,
        *,
        instruction: str | None = None,
        archetype: HookArchetype | None = None,
    ) -> Hook:
        hook = next((h for h in project.hooks if h.id == hook_id), None)
        if hook is None:
            raise NotFoundError("Hook not found in this project.")

        before = {"text": hook.text, "archetype": hook.archetype.value}
        target_archetype = archetype or hook.archetype
        prompt = hook_regeneration.build(
            context=build_context(project, include_hook=False),
            current_hook_text=hook.text,
            archetype=target_archetype.value,
            instruction=instruction,
        )
        new = self.llm.generate_structured(
            [ChatMessage(role="user", content=prompt)], HookOut
        )

        hook.text = new.text
        hook.archetype = new.archetype if archetype else target_archetype
        hook.suitability_score = max(0.0, min(1.0, new.suitability_score))
        hook.estimated_duration_seconds = new.estimated_duration_seconds or hook.estimated_duration_seconds
        hook.unanswered_question = new.unanswered_question
        hook.story_payoff = new.story_payoff
        hook.reason = new.reason

        log_revision(
            self.db,
            project_id=project.id,
            target=RevisionTarget.hook,
            entity_id=hook.id,
            instruction=instruction,
            before=before,
            after={"text": hook.text, "archetype": hook.archetype.value},
        )
        self.db.commit()
        self.db.refresh(hook)
        return hook
