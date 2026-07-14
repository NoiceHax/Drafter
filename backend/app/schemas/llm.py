"""Pydantic schemas that the LLM must produce (structured outputs).

These are intentionally permissive on scores (clamped later) but strict on shape.
"""
from __future__ import annotations

from pydantic import BaseModel, Field

from app.models.enums import HookArchetype, KeywordCategory, VisualPriority, VisualType


# ── idea refinement ───────────────────────────────────────────────────────
class IdeaDirectionOut(BaseModel):
    title: str
    idea: str  # a full refined idea statement for this direction


class IdeaRefinementOut(BaseModel):
    refined_idea: str  # the single best refined idea statement
    interpretation: str  # what the model understood + assumptions it made
    directions: list[IdeaDirectionOut] = Field(default_factory=list)
    clarifying_questions: list[str] = Field(default_factory=list)


# ── keywords ────────────────────────────────────────────────────────────────
class KeywordRecOut(BaseModel):
    keyword: str
    category: KeywordCategory
    reason: str
    relevance_score: float = Field(0.0, ge=0.0, le=1.0)


class KeywordRecListOut(BaseModel):
    recommendations: list[KeywordRecOut]


# ── angles ──────────────────────────────────────────────────────────────────
class AngleOut(BaseModel):
    title: str
    summary: str
    style: str
    why_it_works: str
    estimated_audience_interest: float = Field(0.0, ge=0.0, le=1.0)


class AngleListOut(BaseModel):
    angles: list[AngleOut]


# ── hooks ───────────────────────────────────────────────────────────────────
class HookAnalysisOut(BaseModel):
    archetype: HookArchetype
    suitability_score: float = Field(0.0, ge=0.0, le=1.0)
    reason: str


class HookOut(BaseModel):
    text: str
    archetype: HookArchetype
    suitability_score: float = Field(0.0, ge=0.0, le=1.0)
    estimated_duration_seconds: int = 6
    unanswered_question: str | None = None
    story_payoff: str | None = None
    reason: str | None = None


class HookGenerationOut(BaseModel):
    analysis: list[HookAnalysisOut]
    hooks: list[HookOut]
    recommended_index: int = 0


# ── research ────────────────────────────────────────────────────────────────
class ResearchSourceOut(BaseModel):
    title: str
    url: str
    publisher: str | None = None
    published_at: str | None = None
    summary: str = ""
    key_facts: list[str] = Field(default_factory=list)


class ResearchOut(BaseModel):
    sources: list[ResearchSourceOut]


# ── outline ─────────────────────────────────────────────────────────────────
class OutlineSectionOut(BaseModel):
    type: str
    purpose: str
    summary: str
    estimated_duration_seconds: int = 0


class OutlineOut(BaseModel):
    narrative_structure: str
    estimated_duration_seconds: int = 60
    sections: list[OutlineSectionOut]


# ── script ──────────────────────────────────────────────────────────────────
class ScriptPartOut(BaseModel):
    text: str
    duration_seconds: int = 0


class SceneOut(BaseModel):
    scene_number: int
    start_time: int = 0
    end_time: int = 0
    section_type: str
    narration: str
    on_screen_text: str | None = None
    visual_direction: str | None = None


class ScriptOut(BaseModel):
    title: str
    estimated_duration_seconds: int = 0
    hook: ScriptPartOut
    scenes: list[SceneOut]
    cta: ScriptPartOut | None = None


# ── visuals ─────────────────────────────────────────────────────────────────
class VisualRecOut(BaseModel):
    type: VisualType
    query: str
    description: str
    reason: str | None = None
    priority: VisualPriority = VisualPriority.medium


class VisualRecListOut(BaseModel):
    recommendations: list[VisualRecOut]
