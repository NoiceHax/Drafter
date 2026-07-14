"""FastAPI application entrypoint."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.projects import router as projects_router
from app.api.scenes import router as scenes_router
from app.api.scripts import router as scripts_router
from app.api.stream_routes import router as stream_router
from app.core.config import settings
from app.core.errors import register_error_handlers

# Refuse to start with an insecure JWT secret in production (opt out for dev).
settings.require_secure_secret()

app = FastAPI(
    title="AI Content Creation Copilot",
    version="1.0.0",
    description="Pre-production workspace: idea → keywords → angle → hook → research → story → script → visuals.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)
app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(stream_router)
app.include_router(scenes_router)
app.include_router(scripts_router)


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {
        "status": "ok",
        "llm_configured": settings.llm_configured,
        "research_enabled": settings.research_enabled,
        "image_provider": settings.image_search_provider,
        "model": settings.nvidia_model,
    }
