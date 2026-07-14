"""FastAPI dependencies wiring services to providers."""
from __future__ import annotations

from fastapi import Depends, Header
from sqlalchemy.orm import Session

from app.core.errors import UnauthorizedError
from app.db.session import get_db
from app.models.models import User
from app.providers.resolve import images_for, llm_for, search_for
from app.services.angle_service import AngleService
from app.services.auth_service import AuthService
from app.services.idea_service import IdeaService
from app.services.hook_service import HookService
from app.services.keyword_service import KeywordService
from app.services.project_service import ProjectService
from app.services.research_service import ResearchService
from app.services.script_service import ScriptService
from app.services.story_service import StoryService
from app.services.visual_service import VisualService


def auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


def current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the authenticated user from a Bearer token."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise UnauthorizedError("Sign in to continue.")
    token = authorization.split(" ", 1)[1].strip()
    return AuthService(db).user_from_token(token)


def project_service(
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
) -> ProjectService:
    return ProjectService(db, user)


def idea_service(
    db: Session = Depends(get_db), user: User = Depends(current_user)
) -> IdeaService:
    return IdeaService(db, llm_for(user))


def keyword_service(
    db: Session = Depends(get_db), user: User = Depends(current_user)
) -> KeywordService:
    return KeywordService(db, llm_for(user))


def angle_service(
    db: Session = Depends(get_db), user: User = Depends(current_user)
) -> AngleService:
    return AngleService(db, llm_for(user))


def hook_service(
    db: Session = Depends(get_db), user: User = Depends(current_user)
) -> HookService:
    return HookService(db, llm_for(user))


def research_service(
    db: Session = Depends(get_db), user: User = Depends(current_user)
) -> ResearchService:
    return ResearchService(db, llm_for(user), search_for(user))


def story_service(
    db: Session = Depends(get_db), user: User = Depends(current_user)
) -> StoryService:
    return StoryService(db, llm_for(user))


def script_service(
    db: Session = Depends(get_db), user: User = Depends(current_user)
) -> ScriptService:
    return ScriptService(db, llm_for(user))


def visual_service(
    db: Session = Depends(get_db), user: User = Depends(current_user)
) -> VisualService:
    return VisualService(db, llm_for(user), images_for(user))
