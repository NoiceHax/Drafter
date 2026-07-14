"""StoryService → LLMProvider (story outline)."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.enums import ProjectStage, RevisionTarget
from app.models.models import ContentProject, StoryOutline
from app.prompts import story_outline
from app.providers.llm import ChatMessage, LLMProvider
from app.schemas.llm import OutlineOut
from app.services.base import build_context, log_revision


class StoryService:
    def __init__(self, db: Session, llm: LLMProvider):
        self.db = db
        self.llm = llm

    def generate_outline(
        self, project: ContentProject, *, instruction: str | None = None
    ) -> StoryOutline:
        prompt = story_outline.build(
            context=build_context(project), instruction=instruction
        )
        result = self.llm.generate_structured(
            [ChatMessage(role="user", content=prompt)], OutlineOut
        )

        sections = [s.model_dump(mode="json") for s in result.sections]
        outline = project.outline
        before = None
        if outline is None:
            outline = StoryOutline(project_id=project.id)
            self.db.add(outline)
        else:
            before = {"narrative_structure": outline.narrative_structure}
        outline.narrative_structure = result.narrative_structure
        outline.estimated_duration_seconds = result.estimated_duration_seconds
        outline.sections = sections

        if project.current_stage in (ProjectStage.research, ProjectStage.hooks, ProjectStage.outline):
            project.current_stage = ProjectStage.outline
        log_revision(
            self.db,
            project_id=project.id,
            target=RevisionTarget.outline,
            entity_id=None,
            instruction=instruction,
            before=before,
            after={"narrative_structure": result.narrative_structure, "sections": len(sections)},
        )
        self.db.commit()
        self.db.refresh(outline)
        return outline
