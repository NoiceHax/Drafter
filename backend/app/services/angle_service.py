"""AngleService → LLMProvider."""
from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.models.enums import ProjectStage, RevisionTarget
from app.models.models import ContentAngle, ContentProject
from app.prompts import angle_generation
from app.providers.llm import ChatMessage, LLMProvider
from app.schemas.llm import AngleListOut
from app.services.base import build_context, log_revision


class AngleService:
    def __init__(self, db: Session, llm: LLMProvider):
        self.db = db
        self.llm = llm

    def generate(
        self, project: ContentProject, *, instruction: str | None = None
    ) -> list[ContentAngle]:
        prompt = angle_generation.build(
            context=build_context(project, include_angle=False, include_hook=False),
            instruction=instruction,
        )
        result = self.llm.generate_structured(
            [ChatMessage(role="user", content=prompt)], AngleListOut
        )

        # Regeneration replaces the previous (unselected) angle set.
        for a in list(project.angles):
            self.db.delete(a)
        self.db.flush()

        created: list[ContentAngle] = []
        for angle in result.angles:
            row = ContentAngle(
                project_id=project.id,
                title=angle.title,
                summary=angle.summary,
                style=angle.style,
                why_it_works=angle.why_it_works,
                estimated_audience_interest=max(0.0, min(1.0, angle.estimated_audience_interest)),
            )
            self.db.add(row)
            created.append(row)

        project.selected_angle_id = None
        if project.current_stage in (ProjectStage.idea, ProjectStage.keywords):
            project.current_stage = ProjectStage.angles
        log_revision(
            self.db,
            project_id=project.id,
            target=RevisionTarget.angles,
            instruction=instruction,
            after={"count": len(created)},
        )
        self.db.commit()
        for row in created:
            self.db.refresh(row)
        return created

    def select(self, project: ContentProject, angle_id: uuid.UUID) -> ContentAngle:
        chosen = None
        for a in project.angles:
            a.selected = a.id == angle_id
            if a.selected:
                chosen = a
        if chosen is None:
            raise NotFoundError("Angle not found in this project.")
        project.selected_angle_id = angle_id
        if project.current_stage == ProjectStage.angles:
            project.current_stage = ProjectStage.hooks
        self.db.commit()
        self.db.refresh(chosen)
        return chosen
