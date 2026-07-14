"""IdeaService → LLMProvider (refine a rough idea into a clear direction)."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.enums import RevisionTarget
from app.models.models import ContentProject
from app.prompts import idea_refinement
from app.prompts.common import tone_label
from app.providers.llm import ChatMessage, LLMProvider
from app.schemas.llm import IdeaRefinementOut
from app.services.base import log_revision


class IdeaService:
    def __init__(self, db: Session, llm: LLMProvider):
        self.db = db
        self.llm = llm

    def refine(
        self,
        project: ContentProject,
        *,
        rough_idea: str | None = None,
        instruction: str | None = None,
        answers: str | None = None,
    ) -> IdeaRefinementOut:
        """Propose a refined idea. Does NOT persist; the creator confirms first."""
        prompt = idea_refinement.build(
            rough_idea=rough_idea if rough_idea is not None else project.idea,
            platform=project.platform.value,
            tone=tone_label(project.tone, project.custom_tone),
            target_duration_seconds=project.target_duration_seconds,
            instruction=instruction,
            answers=answers,
        )
        result = self.llm.generate_structured(
            [ChatMessage(role="user", content=prompt)], IdeaRefinementOut
        )
        # Record that a refinement was proposed (audit / future personalization).
        log_revision(
            self.db,
            project_id=project.id,
            target=RevisionTarget.idea,
            instruction=instruction,
            before={"idea": project.idea},
            after={"refined_idea": result.refined_idea},
        )
        self.db.commit()
        return result
