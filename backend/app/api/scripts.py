"""Script-level endpoints: edit hook / CTA / title."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api import deps
from app.core.errors import NotFoundError
from app.db.session import get_db
from app.models.models import Script, User
from app.schemas.api import ScriptEditRequest, ScriptOut
from app.services.project_service import ProjectService
from app.services.script_service import ScriptService

router = APIRouter(prefix="/api/scripts", tags=["scripts"])


@router.patch("/{script_id}", response_model=ScriptOut)
def edit_script(
    script_id: uuid.UUID,
    body: ScriptEditRequest,
    db: Session = Depends(get_db),
    user: User = Depends(deps.current_user),
    svc: ScriptService = Depends(deps.script_service),
):
    script = db.execute(
        select(Script)
        .where(Script.id == script_id)
        .options(selectinload(Script.scenes))
    ).scalar_one_or_none()
    if script is None:
        raise NotFoundError("Script not found.")
    # Enforce ownership: raises 404 if the script's project isn't the user's.
    ProjectService(db, user).get(script.project_id)
    return svc.edit_script(
        script,
        title=body.title,
        hook_text=body.hook_text,
        cta_text=body.cta_text,
    )
