"""Project + pipeline-stage endpoints."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status

from app.api import deps
from app.core.errors import NotFoundError
from app.schemas.api import (
    AngleOut,
    AssetSearchRequest,
    GenerateRequest,
    HookGenerationResponse,
    HookOut,
    HookRegenerateRequest,
    IdeaRefineRequest,
    IdeaRefinementResponse,
    KeywordAddRequest,
    KeywordOut,
    KeywordRecommendationOut,
    KeywordRecommendRequest,
    KeywordSelectRequest,
    ProjectCreate,
    ProjectDetailOut,
    ProjectOut,
    ProjectUpdate,
    ResearchResponse,
    ResearchSelectRequest,
    ResearchSourceOut,
    StoryOutlineOut,
    ScriptOut,
)
from app.services.angle_service import AngleService
from app.services.hook_service import HookService
from app.services.idea_service import IdeaService
from app.services.keyword_service import KeywordService
from app.services.project_service import ProjectService
from app.services.research_service import ResearchService
from app.services.script_service import ScriptService
from app.services.story_service import StoryService

router = APIRouter(prefix="/api/projects", tags=["projects"])


# ── CRUD ──────────────────────────────────────────────────────────────────
@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(body: ProjectCreate, svc: ProjectService = Depends(deps.project_service)):
    return svc.create(body)


@router.get("", response_model=list[ProjectOut])
def list_projects(svc: ProjectService = Depends(deps.project_service)):
    return svc.list()


@router.get("/{project_id}", response_model=ProjectDetailOut)
def get_project(
    project_id: uuid.UUID,
    svc: ProjectService = Depends(deps.project_service),
    research: ResearchService = Depends(deps.research_service),
):
    project = svc.get(project_id, detail=True)

    # Derive convenience fields for the client.
    recs = [KeywordRecommendationOut.model_validate(r) for r in project.keyword_recommendations]
    hooks = [HookOut.model_validate(h) for h in project.hooks]
    hook_analysis = []
    recommended_hook_id = None
    if project.hooks and project.hooks[0].analysis:
        from app.schemas.api import HookAnalysisItem

        hook_analysis = [HookAnalysisItem.model_validate(a) for a in project.hooks[0].analysis]
    # The recommended hook is the currently selected one, if any.
    for h in project.hooks:
        if h.selected:
            recommended_hook_id = h.id
            break

    detail = ProjectDetailOut.model_validate(project)
    # These are derived (not ORM attributes); set them after validation.
    detail.recommendations = recs
    detail.keyword_recommendations = recs
    detail.hooks = hooks
    detail.hook_analysis = hook_analysis
    detail.recommended_hook_id = recommended_hook_id
    detail.research_enabled = research.enabled
    return detail


@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: uuid.UUID,
    body: ProjectUpdate,
    svc: ProjectService = Depends(deps.project_service),
):
    return svc.update(project_id, body)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: uuid.UUID, svc: ProjectService = Depends(deps.project_service)):
    svc.delete(project_id)


# ── idea refinement ───────────────────────────────────────────────────────
@router.post("/{project_id}/idea/refine", response_model=IdeaRefinementResponse)
def refine_idea(
    project_id: uuid.UUID,
    body: IdeaRefineRequest,
    projects: ProjectService = Depends(deps.project_service),
    svc: IdeaService = Depends(deps.idea_service),
):
    project = projects.get(project_id)
    result = svc.refine(
        project,
        rough_idea=body.rough_idea,
        instruction=body.instruction,
        answers=body.answers,
    )
    return IdeaRefinementResponse.model_validate(result.model_dump())


# ── keywords ────────────────────────────────────────────────────────────────
@router.post("/{project_id}/keywords/recommend", response_model=list[KeywordRecommendationOut])
def recommend_keywords(
    project_id: uuid.UUID,
    body: KeywordRecommendRequest,
    projects: ProjectService = Depends(deps.project_service),
    svc: KeywordService = Depends(deps.keyword_service),
):
    project = projects.get(project_id, detail=True)
    return svc.recommend(project, instruction=body.instruction, category=body.category)


@router.post("/{project_id}/keywords/select", response_model=KeywordOut)
def select_keyword(
    project_id: uuid.UUID,
    body: KeywordSelectRequest,
    projects: ProjectService = Depends(deps.project_service),
    svc: KeywordService = Depends(deps.keyword_service),
):
    project = projects.get(project_id, detail=True)
    return svc.set_selection(
        project, keyword=body.keyword, category=body.category, selected=body.selected
    )


@router.post("/{project_id}/keywords", response_model=KeywordOut, status_code=201)
def add_keyword(
    project_id: uuid.UUID,
    body: KeywordAddRequest,
    projects: ProjectService = Depends(deps.project_service),
    svc: KeywordService = Depends(deps.keyword_service),
):
    project = projects.get(project_id, detail=True)
    return svc.add_custom(project, body.text)


@router.delete("/{project_id}/keywords/{keyword_id}", status_code=204)
def delete_keyword(
    project_id: uuid.UUID,
    keyword_id: uuid.UUID,
    projects: ProjectService = Depends(deps.project_service),
    svc: KeywordService = Depends(deps.keyword_service),
):
    project = projects.get(project_id, detail=True)
    svc.remove(project, keyword_id)


# ── angles ──────────────────────────────────────────────────────────────────
@router.post("/{project_id}/angles/generate", response_model=list[AngleOut])
def generate_angles(
    project_id: uuid.UUID,
    body: GenerateRequest,
    projects: ProjectService = Depends(deps.project_service),
    svc: AngleService = Depends(deps.angle_service),
):
    project = projects.get(project_id, detail=True)
    return svc.generate(project, instruction=body.instruction)


@router.post("/{project_id}/angles/{angle_id}/select", response_model=AngleOut)
def select_angle(
    project_id: uuid.UUID,
    angle_id: uuid.UUID,
    projects: ProjectService = Depends(deps.project_service),
    svc: AngleService = Depends(deps.angle_service),
):
    project = projects.get(project_id, detail=True)
    return svc.select(project, angle_id)


# ── hooks ───────────────────────────────────────────────────────────────────
@router.post("/{project_id}/hooks/generate", response_model=HookGenerationResponse)
def generate_hooks(
    project_id: uuid.UUID,
    body: GenerateRequest,
    projects: ProjectService = Depends(deps.project_service),
    svc: HookService = Depends(deps.hook_service),
):
    project = projects.get(project_id, detail=True)
    analysis, hooks, recommended_id = svc.generate(project, instruction=body.instruction)
    return HookGenerationResponse(
        analysis=analysis,
        hooks=[HookOut.model_validate(h) for h in hooks],
        recommended_hook_id=recommended_id,
    )


@router.post("/{project_id}/hooks/{hook_id}/select", response_model=HookOut)
def select_hook(
    project_id: uuid.UUID,
    hook_id: uuid.UUID,
    projects: ProjectService = Depends(deps.project_service),
    svc: HookService = Depends(deps.hook_service),
):
    project = projects.get(project_id, detail=True)
    return svc.select(project, hook_id)


@router.post("/{project_id}/hooks/{hook_id}/regenerate", response_model=HookOut)
def regenerate_hook(
    project_id: uuid.UUID,
    hook_id: uuid.UUID,
    body: HookRegenerateRequest,
    projects: ProjectService = Depends(deps.project_service),
    svc: HookService = Depends(deps.hook_service),
):
    project = projects.get(project_id, detail=True)
    return svc.regenerate(
        project, hook_id, instruction=body.instruction, archetype=body.archetype
    )


# ── research ────────────────────────────────────────────────────────────────
@router.post("/{project_id}/research", response_model=ResearchResponse)
def run_research(
    project_id: uuid.UUID,
    body: GenerateRequest,
    projects: ProjectService = Depends(deps.project_service),
    svc: ResearchService = Depends(deps.research_service),
):
    project = projects.get(project_id, detail=True)
    enabled, sources, message = svc.run(project, instruction=body.instruction)
    return ResearchResponse(
        research_enabled=enabled,
        mode="researched" if enabled else "non_researched",
        sources=[ResearchSourceOut.model_validate(s) for s in sources],
        message=message,
    )


@router.post("/{project_id}/research/{source_id}/select", response_model=ResearchSourceOut)
def select_research_source(
    project_id: uuid.UUID,
    source_id: uuid.UUID,
    body: ResearchSelectRequest,
    projects: ProjectService = Depends(deps.project_service),
    svc: ResearchService = Depends(deps.research_service),
):
    project = projects.get(project_id, detail=True)
    return svc.set_selected(project, source_id, body.selected)


# ── outline ─────────────────────────────────────────────────────────────────
@router.post("/{project_id}/outline/generate", response_model=StoryOutlineOut)
def generate_outline(
    project_id: uuid.UUID,
    body: GenerateRequest,
    projects: ProjectService = Depends(deps.project_service),
    svc: StoryService = Depends(deps.story_service),
):
    project = projects.get(project_id, detail=True)
    return svc.generate_outline(project, instruction=body.instruction)


# ── script ──────────────────────────────────────────────────────────────────
@router.post("/{project_id}/script/generate", response_model=ScriptOut)
def generate_script(
    project_id: uuid.UUID,
    body: GenerateRequest,
    projects: ProjectService = Depends(deps.project_service),
    svc: ScriptService = Depends(deps.script_service),
):
    project = projects.get(project_id, detail=True)
    return svc.generate(project, instruction=body.instruction)
