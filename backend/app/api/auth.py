"""Authentication endpoints: email-first login with an alpha allowlist."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from fastapi import Depends
from sqlalchemy.orm import Session

from app.api import deps
from app.db.session import get_db
from app.models.models import User
from app.schemas.api import (
    AuthResponse,
    EmailCheckRequest,
    EmailCheckResponse,
    LoginRequest,
    UserKeysStatus,
    UserKeysUpdate,
    UserOut,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _keys_status(user: User) -> UserKeysStatus:
    return UserKeysStatus(
        nvidia_api_key_set=bool(user.nvidia_api_key),
        nvidia_model=user.nvidia_model,
        tavily_api_key_set=bool(user.tavily_api_key),
        pexels_api_key_set=bool(user.pexels_api_key),
    )


@router.post("/check-email", response_model=EmailCheckResponse)
def check_email(body: EmailCheckRequest, svc: AuthService = Depends(deps.auth_service)):
    return EmailCheckResponse(mode=svc.check_email(body.email))


@router.post("/login", response_model=AuthResponse)
def login(body: LoginRequest, svc: AuthService = Depends(deps.auth_service)):
    token, user = svc.login(body.email, body.password)
    return AuthResponse(token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(deps.current_user)):
    return UserOut.model_validate(user)


@router.get("/keys", response_model=UserKeysStatus)
def get_keys(user: User = Depends(deps.current_user)):
    return _keys_status(user)


@router.patch("/keys", response_model=UserKeysStatus)
def update_keys(
    body: UserKeysUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(deps.current_user),
):
    # null leaves a field unchanged; empty string clears it.
    if body.nvidia_api_key is not None:
        user.nvidia_api_key = body.nvidia_api_key.strip() or None
    if body.nvidia_model is not None:
        user.nvidia_model = body.nvidia_model.strip() or None
    if body.tavily_api_key is not None:
        user.tavily_api_key = body.tavily_api_key.strip() or None
    if body.pexels_api_key is not None:
        user.pexels_api_key = body.pexels_api_key.strip() or None
    db.add(user)
    db.commit()
    db.refresh(user)
    return _keys_status(user)
