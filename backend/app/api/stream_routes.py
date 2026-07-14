"""Streaming (SSE) endpoints for the heavier generation stages.

These mirror the JSON endpoints in ``projects.py`` but stream progress events so
the UI shows live activity + elapsed time. The final ``done`` event contains the
same payload the JSON endpoint would return. Clients that don't use streaming
can keep calling the plain JSON endpoints.
"""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api import deps
from app.api.streaming import stream_stage
from app.db.session import get_db
from app.models.models import User
from app.providers.resolve import llm_for
from app.schemas.api import (
    GenerateRequest,
    HookGenerationResponse,
    HookOut,
    ScriptOut,
    StoryOutlineOut,
)
from app.services.hook_service import HookService
from app.services.project_service import ProjectService
from app.services.script_service import ScriptService
from app.services.story_service import StoryService

router = APIRouter(prefix="/api/projects", tags=["streaming"])

_SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",  # disable proxy buffering
}


@router.post("/{project_id}/hooks/generate/stream")
def stream_hooks(
    project_id: uuid.UUID,
    body: GenerateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(deps.current_user),
):
    def work(phase):
        projects = ProjectService(db, user)
        project = projects.get(project_id, detail=True)
        phase("analyzing", "Analyzing narrative archetypes…")
        svc = HookService(db, llm_for(user))
        phase("calling_model", "Generating hooks…")
        analysis, hooks, recommended_id = svc.generate(project, instruction=body.instruction)
        phase("validating", "Finalizing…")
        return HookGenerationResponse(
            analysis=analysis,
            hooks=[HookOut.model_validate(h) for h in hooks],
            recommended_hook_id=recommended_id,
        ).model_dump(mode="json")

    return StreamingResponse(
        stream_stage(work), media_type="text/event-stream", headers=_SSE_HEADERS
    )


@router.post("/{project_id}/outline/generate/stream")
def stream_outline(
    project_id: uuid.UUID,
    body: GenerateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(deps.current_user),
):
    def work(phase):
        project = ProjectService(db, user).get(project_id, detail=True)
        phase("calling_model", "Building the story outline…")
        outline = StoryService(db, llm_for(user)).generate_outline(
            project, instruction=body.instruction
        )
        phase("validating", "Finalizing…")
        return StoryOutlineOut.model_validate(outline).model_dump(mode="json")

    return StreamingResponse(
        stream_stage(work), media_type="text/event-stream", headers=_SSE_HEADERS
    )


@router.post("/{project_id}/script/generate/stream")
def stream_script(
    project_id: uuid.UUID,
    body: GenerateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(deps.current_user),
):
    def work(phase):
        project = ProjectService(db, user).get(project_id, detail=True)
        phase("calling_model", "Writing the full script, scene by scene…")
        script = ScriptService(db, llm_for(user)).generate(
            project, instruction=body.instruction
        )
        phase("validating", "Timing scenes and finalizing…")
        return ScriptOut.model_validate(script).model_dump(mode="json")

    return StreamingResponse(
        stream_stage(work), media_type="text/event-stream", headers=_SSE_HEADERS
    )
