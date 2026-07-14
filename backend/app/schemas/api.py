"""API request and response schemas (never expose ORM models directly)."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import (
    HookArchetype,
    KeywordCategory,
    KeywordStatus,
    Platform,
    ProjectStage,
    Tone,
    VisualPriority,
    VisualType,
)


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ── auth ──────────────────────────────────────────────────────────────────
class UserOut(ORMModel):
    id: uuid.UUID
    email: str
    display_name: str | None = None


class EmailCheckRequest(BaseModel):
    email: str


class EmailCheckResponse(BaseModel):
    # mode drives the two-step login UI:
    #   "alpha"    -> skip password, show "Continue as <email>"
    #   "password" -> show password field
    #   "unknown"  -> email not on the invite list
    mode: str


class LoginRequest(BaseModel):
    email: str
    password: str | None = None


class AuthResponse(BaseModel):
    token: str
    user: UserOut


class UserKeysStatus(BaseModel):
    """Whether each per-user key is set (never returns the secret values)."""

    nvidia_api_key_set: bool
    nvidia_model: str | None = None
    tavily_api_key_set: bool
    pexels_api_key_set: bool


class UserKeysUpdate(BaseModel):
    """Update per-user keys. null = leave unchanged; "" = clear."""

    nvidia_api_key: str | None = None
    nvidia_model: str | None = None
    tavily_api_key: str | None = None
    pexels_api_key: str | None = None


# ── projects ────────────────────────────────────────────────────────────────
class ProjectCreate(BaseModel):
    title: str | None = None
    idea: str = ""
    initial_keywords: list[str] = Field(default_factory=list)
    platform: Platform = Platform.generic
    target_duration_seconds: int = 60
    tone: Tone = Tone.conversational
    custom_tone: str | None = None


class ProjectUpdate(BaseModel):
    title: str | None = None
    idea: str | None = None
    platform: Platform | None = None
    target_duration_seconds: int | None = None
    tone: Tone | None = None
    custom_tone: str | None = None


class ProjectOut(ORMModel):
    id: uuid.UUID
    title: str | None
    idea: str
    platform: Platform
    target_duration_seconds: int
    tone: Tone
    custom_tone: str | None
    current_stage: ProjectStage
    selected_angle_id: uuid.UUID | None
    selected_hook_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime


# ── keywords ────────────────────────────────────────────────────────────────
class KeywordOut(ORMModel):
    id: uuid.UUID
    text: str
    status: KeywordStatus
    category: KeywordCategory | None
    selected: bool


class KeywordRecommendationOut(ORMModel):
    id: uuid.UUID
    keyword: str
    category: KeywordCategory
    reason: str
    relevance_score: float
    accepted: bool | None


class KeywordRecommendRequest(BaseModel):
    instruction: str | None = None
    category: KeywordCategory | None = None


class KeywordSelectRequest(BaseModel):
    keyword: str
    category: KeywordCategory | None = None
    selected: bool = True


class KeywordAddRequest(BaseModel):
    text: str


# ── angles ──────────────────────────────────────────────────────────────────
class AngleOut(ORMModel):
    id: uuid.UUID
    title: str
    summary: str
    style: str
    why_it_works: str
    estimated_audience_interest: float
    selected: bool


class GenerateRequest(BaseModel):
    """Generic body for generate/regenerate calls that accept a refinement instruction."""

    instruction: str | None = None


# ── idea refinement ───────────────────────────────────────────────────────
class IdeaRefineRequest(BaseModel):
    # Optional: the raw text to refine (defaults to the project's current idea).
    rough_idea: str | None = None
    instruction: str | None = None
    answers: str | None = None


class IdeaDirection(BaseModel):
    title: str
    idea: str


class IdeaRefinementResponse(BaseModel):
    refined_idea: str
    interpretation: str
    directions: list[IdeaDirection] = Field(default_factory=list)
    clarifying_questions: list[str] = Field(default_factory=list)


# ── hooks ───────────────────────────────────────────────────────────────────
class HookAnalysisItem(BaseModel):
    archetype: HookArchetype
    suitability_score: float
    reason: str


class HookOut(ORMModel):
    id: uuid.UUID
    text: str
    archetype: HookArchetype
    suitability_score: float
    estimated_duration_seconds: int
    unanswered_question: str | None
    story_payoff: str | None
    reason: str | None
    selected: bool


class HookGenerationResponse(BaseModel):
    analysis: list[HookAnalysisItem]
    hooks: list[HookOut]
    recommended_hook_id: uuid.UUID | None


class HookRegenerateRequest(BaseModel):
    instruction: str | None = None
    archetype: HookArchetype | None = None


# ── research ────────────────────────────────────────────────────────────────
class ResearchSourceOut(ORMModel):
    id: uuid.UUID
    title: str
    url: str
    publisher: str | None
    published_at: str | None
    summary: str
    key_facts: list[str] | None
    selected: bool = True


class ResearchSelectRequest(BaseModel):
    selected: bool


class ResearchResponse(BaseModel):
    research_enabled: bool
    mode: str  # "researched" | "non_researched"
    sources: list[ResearchSourceOut]
    message: str | None = None


# ── outline ─────────────────────────────────────────────────────────────────
class OutlineSection(BaseModel):
    type: str
    purpose: str
    summary: str
    estimated_duration_seconds: int


class StoryOutlineOut(ORMModel):
    id: uuid.UUID
    narrative_structure: str
    estimated_duration_seconds: int
    sections: list[OutlineSection]


# ── visuals ─────────────────────────────────────────────────────────────────
class VisualRecommendationOut(ORMModel):
    id: uuid.UUID
    type: VisualType
    query: str
    description: str
    reason: str | None
    priority: VisualPriority


class VisualAssetOut(ORMModel):
    id: uuid.UUID
    url: str
    thumbnail_url: str | None
    source_url: str | None
    provider: str
    title: str | None
    creator: str | None
    license: str | None


class AssetSearchRequest(BaseModel):
    query: str | None = None


# ── scenes ──────────────────────────────────────────────────────────────────
class SceneOut(ORMModel):
    id: uuid.UUID
    scene_number: int
    start_time: int
    end_time: int
    section_type: str
    narration: str
    on_screen_text: str | None
    visual_direction: str | None
    visual_recommendations: list[VisualRecommendationOut] = Field(default_factory=list)
    visual_assets: list[VisualAssetOut] = Field(default_factory=list)


class SceneRegenerateRequest(BaseModel):
    instruction: str | None = None
    field: str = "all"  # "narration" | "visual_direction" | "all"


class SceneEditRequest(BaseModel):
    narration: str | None = None
    on_screen_text: str | None = None
    visual_direction: str | None = None


# ── script ──────────────────────────────────────────────────────────────────
class ScriptEditRequest(BaseModel):
    title: str | None = None
    hook_text: str | None = None
    cta_text: str | None = None


class ScriptOut(ORMModel):
    id: uuid.UUID
    title: str
    platform: Platform
    target_duration_seconds: int
    estimated_duration_seconds: int
    hook_text: str
    hook_duration_seconds: int
    cta_text: str | None
    cta_duration_seconds: int
    scenes: list[SceneOut] = Field(default_factory=list)


# ── project detail (aggregate) ───────────────────────────────────────────────
class ProjectDetailOut(ProjectOut):
    keywords: list[KeywordOut] = Field(default_factory=list)
    # Exposed under both names for client convenience.
    keyword_recommendations: list[KeywordRecommendationOut] = Field(default_factory=list)
    recommendations: list[KeywordRecommendationOut] = Field(default_factory=list)
    angles: list[AngleOut] = Field(default_factory=list)
    hooks: list[HookOut] = Field(default_factory=list)
    hook_analysis: list[HookAnalysisItem] = Field(default_factory=list)
    recommended_hook_id: uuid.UUID | None = None
    research_sources: list[ResearchSourceOut] = Field(default_factory=list)
    research_enabled: bool = False
    outline: StoryOutlineOut | None = None
    script: ScriptOut | None = None
