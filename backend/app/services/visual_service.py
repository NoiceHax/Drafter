"""VisualService → LLMProvider (recommendations) + ImageSearchProvider (assets)."""
from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.models.enums import ProjectStage, RevisionTarget
from app.models.models import (
    ContentProject,
    ScriptScene,
    VisualAsset,
    VisualRecommendation,
)
from app.prompts import visual_recommendations
from app.providers.images import ImageSearchProvider
from app.providers.llm import ChatMessage, LLMProvider
from app.schemas.llm import VisualRecListOut
from app.services.base import build_context, log_revision


class VisualService:
    def __init__(self, db: Session, llm: LLMProvider, images: ImageSearchProvider):
        self.db = db
        self.llm = llm
        self.images = images

    def generate_recommendations(
        self, scene: ScriptScene, project: ContentProject, *, instruction: str | None = None
    ) -> list[VisualRecommendation]:
        scene_json = json.dumps(
            {
                "section_type": scene.section_type,
                "narration": scene.narration,
                "on_screen_text": scene.on_screen_text,
                "visual_direction": scene.visual_direction,
            },
            indent=2,
        )
        prompt = visual_recommendations.build(
            context=build_context(project),
            scene_json=scene_json,
            instruction=instruction,
        )
        result = self.llm.generate_structured(
            [ChatMessage(role="user", content=prompt)], VisualRecListOut
        )

        for rec in list(scene.visual_recommendations):
            self.db.delete(rec)
        self.db.flush()

        created: list[VisualRecommendation] = []
        for rec in result.recommendations:
            row = VisualRecommendation(
                scene_id=scene.id,
                type=rec.type,
                query=rec.query,
                description=rec.description,
                reason=rec.reason,
                priority=rec.priority,
            )
            self.db.add(row)
            created.append(row)

        if project.current_stage in (ProjectStage.script, ProjectStage.visuals):
            project.current_stage = ProjectStage.visuals
        log_revision(
            self.db,
            project_id=project.id,
            target=RevisionTarget.scene_visuals,
            entity_id=scene.id,
            instruction=instruction,
            after={"count": len(created)},
        )
        self.db.commit()
        for row in created:
            self.db.refresh(row)
        return created

    def search_assets(
        self, scene: ScriptScene, *, query: str | None = None
    ) -> list[VisualAsset]:
        # Determine which queries to run: explicit override, else the scene's
        # high-priority recommendation queries.
        queries: list[tuple[str, VisualRecommendation | None]] = []
        if query:
            queries.append((query, None))
        else:
            recs = sorted(
                scene.visual_recommendations,
                key=lambda r: {"high": 0, "medium": 1, "low": 2}.get(r.priority.value, 3),
            )
            for r in recs[:2]:
                queries.append((r.query, r))
        if not queries:
            return []

        # Clear prior discovered assets for this scene to avoid duplicates.
        for a in list(scene.visual_assets):
            self.db.delete(a)
        self.db.flush()

        created: list[VisualAsset] = []
        for q, rec in queries:
            for asset in self.images.search_images(q, limit=4):
                row = VisualAsset(
                    scene_id=scene.id,
                    recommendation_id=rec.id if rec else None,
                    url=asset.url,
                    thumbnail_url=asset.thumbnail_url,
                    source_url=asset.source_url,
                    provider=asset.provider,
                    title=asset.title,
                    creator=asset.creator,
                    license=asset.license,
                )
                self.db.add(row)
                created.append(row)

        self.db.commit()
        for row in created:
            self.db.refresh(row)
        return created
