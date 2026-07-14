"""Scene-level endpoints: regenerate, edit, visuals, asset search."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api import deps
from app.core.errors import NotFoundError
from app.db.session import get_db
from app.models.models import ContentProject, Script, ScriptScene, User
from app.schemas.api import (
    AssetSearchRequest,
    SceneEditRequest,
    SceneOut,
    SceneRegenerateRequest,
    VisualAssetOut,
    VisualRecommendationOut,
    GenerateRequest,
)
from app.services.project_service import ProjectService
from app.services.script_service import ScriptService
from app.services.visual_service import VisualService

router = APIRouter(prefix="/api/scenes", tags=["scenes"])


def _load_scene(
    db: Session, scene_id: uuid.UUID, user: User
) -> tuple[ScriptScene, ContentProject]:
    scene = db.execute(
        select(ScriptScene)
        .where(ScriptScene.id == scene_id)
        .options(
            selectinload(ScriptScene.visual_recommendations),
            selectinload(ScriptScene.visual_assets),
            selectinload(ScriptScene.script),
        )
    ).scalar_one_or_none()
    if scene is None:
        raise NotFoundError("Scene not found.")
    # ProjectService.get enforces that the scene's project is owned by `user`.
    project = ProjectService(db, user).get(scene.script.project_id, detail=True)
    return scene, project


@router.post("/{scene_id}/regenerate", response_model=SceneOut)
def regenerate_scene(
    scene_id: uuid.UUID,
    body: SceneRegenerateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(deps.current_user),
    svc: ScriptService = Depends(deps.script_service),
):
    scene, project = _load_scene(db, scene_id, user)
    return svc.regenerate_scene(scene, project, field=body.field, instruction=body.instruction)


@router.patch("/{scene_id}", response_model=SceneOut)
def edit_scene(
    scene_id: uuid.UUID,
    body: SceneEditRequest,
    db: Session = Depends(get_db),
    user: User = Depends(deps.current_user),
    svc: ScriptService = Depends(deps.script_service),
):
    scene, _ = _load_scene(db, scene_id, user)
    return svc.edit_scene(
        scene,
        narration=body.narration,
        on_screen_text=body.on_screen_text,
        visual_direction=body.visual_direction,
    )


@router.post("/{scene_id}/visuals/generate", response_model=list[VisualRecommendationOut])
def generate_visuals(
    scene_id: uuid.UUID,
    body: GenerateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(deps.current_user),
    svc: VisualService = Depends(deps.visual_service),
):
    scene, project = _load_scene(db, scene_id, user)
    return svc.generate_recommendations(scene, project, instruction=body.instruction)


@router.post("/{scene_id}/assets/search", response_model=list[VisualAssetOut])
def search_assets(
    scene_id: uuid.UUID,
    body: AssetSearchRequest,
    db: Session = Depends(get_db),
    user: User = Depends(deps.current_user),
    svc: VisualService = Depends(deps.visual_service),
):
    scene, _ = _load_scene(db, scene_id, user)
    return svc.search_assets(scene, query=body.query)
