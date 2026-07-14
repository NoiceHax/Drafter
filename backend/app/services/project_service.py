"""Project CRUD, scoped to the authenticated user (owner)."""
from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.errors import NotFoundError
from app.models.models import ContentProject, User
from app.models.enums import KeywordStatus
from app.models.models import Keyword
from app.schemas.api import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user

    def _detail_options(self):
        return (
            selectinload(ContentProject.keywords),
            selectinload(ContentProject.keyword_recommendations),
            selectinload(ContentProject.angles),
            selectinload(ContentProject.hooks),
            selectinload(ContentProject.research_sources),
            selectinload(ContentProject.outline),
            selectinload(ContentProject.script),
        )

    def create(self, data: ProjectCreate) -> ContentProject:
        project = ContentProject(
            user_id=self.user.id,
            title=data.title,
            idea=data.idea,
            platform=data.platform,
            target_duration_seconds=data.target_duration_seconds,
            tone=data.tone,
            custom_tone=data.custom_tone,
        )
        self.db.add(project)
        self.db.flush()

        for kw in data.initial_keywords:
            kw = kw.strip()
            if not kw:
                continue
            self.db.add(
                Keyword(
                    project_id=project.id,
                    text=kw,
                    status=KeywordStatus.original,
                    selected=True,
                )
            )
        self.db.commit()
        self.db.refresh(project)
        return project

    def list(self) -> list[ContentProject]:
        return list(
            self.db.execute(
                select(ContentProject)
                .where(ContentProject.user_id == self.user.id)
                .order_by(ContentProject.updated_at.desc())
            ).scalars()
        )

    def get(self, project_id: uuid.UUID, *, detail: bool = False) -> ContentProject:
        stmt = select(ContentProject).where(ContentProject.id == project_id)
        if detail:
            stmt = stmt.options(*self._detail_options())
        project = self.db.execute(stmt).scalar_one_or_none()
        # Return 404 (not 403) for another user's project so we don't leak existence.
        if project is None or project.user_id != self.user.id:
            raise NotFoundError("Project not found.")
        return project

    def update(self, project_id: uuid.UUID, data: ProjectUpdate) -> ContentProject:
        project = self.get(project_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(project, field, value)
        self.db.commit()
        self.db.refresh(project)
        return project

    def delete(self, project_id: uuid.UUID) -> None:
        project = self.get(project_id)
        self.db.delete(project)
        self.db.commit()
