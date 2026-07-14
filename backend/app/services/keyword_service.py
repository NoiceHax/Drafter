"""KeywordService → LLMProvider."""
from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.models.enums import KeywordCategory, KeywordStatus, ProjectStage, RevisionTarget
from app.models.models import ContentProject, Keyword, KeywordRecommendation
from app.prompts import keyword_expansion
from app.providers.llm import ChatMessage, LLMProvider
from app.schemas.llm import KeywordRecListOut
from app.services.base import log_revision, selected_keywords


class KeywordService:
    def __init__(self, db: Session, llm: LLMProvider):
        self.db = db
        self.llm = llm

    def recommend(
        self,
        project: ContentProject,
        *,
        instruction: str | None = None,
        category: KeywordCategory | None = None,
    ) -> list[KeywordRecommendation]:
        base_keywords = [k.text for k in project.keywords] or selected_keywords(project)
        prompt = keyword_expansion.build(
            idea=project.idea,
            keywords=[k.text for k in project.keywords] if project.keywords else base_keywords,
            instruction=instruction,
            category=category.value if category else None,
        )
        result = self.llm.generate_structured(
            [ChatMessage(role="user", content=prompt)],
            KeywordRecListOut,
        )

        # When regenerating a specific category, only replace that category.
        existing = {(r.keyword.lower(), r.category) for r in project.keyword_recommendations}
        created: list[KeywordRecommendation] = []
        for rec in result.recommendations:
            if category and rec.category != category:
                continue
            key = (rec.keyword.lower(), rec.category)
            if key in existing:
                continue
            existing.add(key)
            row = KeywordRecommendation(
                project_id=project.id,
                keyword=rec.keyword,
                category=rec.category,
                reason=rec.reason,
                relevance_score=max(0.0, min(1.0, rec.relevance_score)),
            )
            self.db.add(row)
            created.append(row)

        if project.current_stage == ProjectStage.idea:
            project.current_stage = ProjectStage.keywords
        log_revision(
            self.db,
            project_id=project.id,
            target=RevisionTarget.keyword_recommendations,
            instruction=instruction,
            after={"count": len(created), "category": category.value if category else None},
        )
        self.db.commit()
        for row in created:
            self.db.refresh(row)
        return created

    # ── selection / editing (also records interaction history) ──────────────
    def set_selection(
        self,
        project: ContentProject,
        *,
        keyword: str,
        category: KeywordCategory | None,
        selected: bool,
    ) -> Keyword:
        existing = self._find_keyword(project, keyword)
        if existing:
            existing.selected = selected
            existing.status = KeywordStatus.selected if selected else KeywordStatus.rejected
        else:
            existing = Keyword(
                project_id=project.id,
                text=keyword,
                category=category,
                selected=selected,
                status=KeywordStatus.selected if selected else KeywordStatus.rejected,
            )
            self.db.add(existing)

        # Update the recommendation's accepted flag for future intelligence.
        for rec in project.keyword_recommendations:
            if rec.keyword.lower() == keyword.lower():
                rec.accepted = selected
        self.db.commit()
        self.db.refresh(existing)
        return existing

    def add_custom(self, project: ContentProject, text: str) -> Keyword:
        existing = self._find_keyword(project, text)
        if existing:
            existing.selected = True
            existing.status = KeywordStatus.custom
            self.db.commit()
            self.db.refresh(existing)
            return existing
        row = Keyword(
            project_id=project.id,
            text=text,
            selected=True,
            status=KeywordStatus.custom,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def remove(self, project: ContentProject, keyword_id: uuid.UUID) -> None:
        for k in project.keywords:
            if k.id == keyword_id:
                self.db.delete(k)
                self.db.commit()
                return

    @staticmethod
    def _find_keyword(project: ContentProject, text: str) -> Keyword | None:
        for k in project.keywords:
            if k.text.lower() == text.lower():
                return k
        return None
