"""SQLAlchemy 2.x ORM models for the content-creation copilot.

Relationship map:
    User
     └── ContentProject
          ├── Keyword
          ├── KeywordRecommendation
          ├── ContentAngle
          ├── Hook
          ├── ResearchSource
          ├── StoryOutline
          └── Script
               └── ScriptScene
                    ├── VisualRecommendation
                    └── VisualAsset
    Revision  (audit trail, references a project + optional entity)
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.db.base import Base, TimestampMixin, uuid_pk
from app.models.enums import (
    HookArchetype,
    KeywordCategory,
    KeywordStatus,
    Platform,
    ProjectStage,
    RevisionTarget,
    Tone,
    VisualPriority,
    VisualType,
)


_SCHEMA = settings.db_schema


def _q(target: str) -> str:
    """Schema-qualify a ``table.column`` foreign-key target."""
    return f"{_SCHEMA}.{target}"


def _fk(target: str) -> Mapped[uuid.UUID]:
    return mapped_column(
        PG_UUID(as_uuid=True), ForeignKey(_q(target), ondelete="CASCADE"), nullable=False
    )


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = uuid_pk()
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    # Nullable: alpha-allowlist users authenticate without a password.
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_alpha: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Creator preference scaffolding (populated over time; no ML yet).
    preferred_tone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    preferred_platforms: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    preferences: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Optional per-user API keys; when set they override the server env keys.
    nvidia_api_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    nvidia_model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    tavily_api_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pexels_api_key: Mapped[str | None] = mapped_column(String(255), nullable=True)

    projects: Mapped[list[ContentProject]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class ContentProject(Base, TimestampMixin):
    __tablename__ = "content_projects"

    id: Mapped[uuid.UUID] = uuid_pk()
    user_id: Mapped[uuid.UUID] = _fk("users.id")

    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    idea: Mapped[str] = mapped_column(Text, nullable=False, default="")
    platform: Mapped[Platform] = mapped_column(default=Platform.generic, nullable=False)
    target_duration_seconds: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    tone: Mapped[Tone] = mapped_column(default=Tone.conversational, nullable=False)
    custom_tone: Mapped[str | None] = mapped_column(String(80), nullable=True)

    current_stage: Mapped[ProjectStage] = mapped_column(
        default=ProjectStage.idea, nullable=False
    )
    selected_angle_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    selected_hook_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)

    user: Mapped[User] = relationship(back_populates="projects")
    keywords: Mapped[list[Keyword]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    keyword_recommendations: Mapped[list[KeywordRecommendation]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    angles: Mapped[list[ContentAngle]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    hooks: Mapped[list[Hook]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    research_sources: Mapped[list[ResearchSource]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    outline: Mapped[StoryOutline | None] = relationship(
        back_populates="project", cascade="all, delete-orphan", uselist=False
    )
    script: Mapped[Script | None] = relationship(
        back_populates="project", cascade="all, delete-orphan", uselist=False
    )
    revisions: Mapped[list[Revision]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class Keyword(Base, TimestampMixin):
    """A keyword associated with a project, tracked through its lifecycle."""

    __tablename__ = "keywords"
    __table_args__ = (UniqueConstraint("project_id", "text", name="uq_keyword_project_text"),)

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = _fk("content_projects.id")
    text: Mapped[str] = mapped_column(String(160), nullable=False)
    status: Mapped[KeywordStatus] = mapped_column(nullable=False)
    category: Mapped[KeywordCategory | None] = mapped_column(nullable=True)
    selected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    project: Mapped[ContentProject] = relationship(back_populates="keywords")


class KeywordRecommendation(Base, TimestampMixin):
    """A single LLM keyword suggestion (immutable record for interaction history)."""

    __tablename__ = "keyword_recommendations"

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = _fk("content_projects.id")
    keyword: Mapped[str] = mapped_column(String(160), nullable=False)
    category: Mapped[KeywordCategory] = mapped_column(nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    relevance_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    # Whether the creator accepted (selected) or rejected this recommendation.
    accepted: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    project: Mapped[ContentProject] = relationship(back_populates="keyword_recommendations")


class ContentAngle(Base, TimestampMixin):
    __tablename__ = "content_angles"

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = _fk("content_projects.id")
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    style: Mapped[str] = mapped_column(String(60), nullable=False)
    why_it_works: Mapped[str] = mapped_column(Text, nullable=False)
    estimated_audience_interest: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    selected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    project: Mapped[ContentProject] = relationship(back_populates="angles")


class Hook(Base, TimestampMixin):
    __tablename__ = "hooks"

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = _fk("content_projects.id")
    text: Mapped[str] = mapped_column(Text, nullable=False)
    archetype: Mapped[HookArchetype] = mapped_column(nullable=False)
    suitability_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    estimated_duration_seconds: Mapped[int] = mapped_column(Integer, default=6, nullable=False)
    unanswered_question: Mapped[str | None] = mapped_column(Text, nullable=True)
    story_payoff: Mapped[str | None] = mapped_column(Text, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    selected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    # Per-archetype suitability analysis snapshot from the generation call.
    analysis: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    project: Mapped[ContentProject] = relationship(back_populates="hooks")


class ResearchSource(Base, TimestampMixin):
    __tablename__ = "research_sources"

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = _fk("content_projects.id")
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    publisher: Mapped[str | None] = mapped_column(String(200), nullable=True)
    published_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    summary: Mapped[str] = mapped_column(Text, nullable=False, default="")
    key_facts: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    # Whether this source is included when building the story/script context.
    selected: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    project: Mapped[ContentProject] = relationship(back_populates="research_sources")


class StoryOutline(Base, TimestampMixin):
    __tablename__ = "story_outlines"

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey(_q("content_projects.id"), ondelete="CASCADE"),
        unique=True, nullable=False,
    )
    narrative_structure: Mapped[str] = mapped_column(String(120), nullable=False)
    estimated_duration_seconds: Mapped[int] = mapped_column(Integer, default=60, nullable=False)
    # List of {type, purpose, summary, estimated_duration_seconds}.
    sections: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    project: Mapped[ContentProject] = relationship(back_populates="outline")


class Script(Base, TimestampMixin):
    __tablename__ = "scripts"

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey(_q("content_projects.id"), ondelete="CASCADE"),
        unique=True, nullable=False,
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    platform: Mapped[Platform] = mapped_column(nullable=False)
    target_duration_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    estimated_duration_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    hook_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    hook_duration_seconds: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    cta_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    cta_duration_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    project: Mapped[ContentProject] = relationship(back_populates="script")
    scenes: Mapped[list[ScriptScene]] = relationship(
        back_populates="script",
        cascade="all, delete-orphan",
        order_by="ScriptScene.scene_number",
    )


class ScriptScene(Base, TimestampMixin):
    __tablename__ = "script_scenes"

    id: Mapped[uuid.UUID] = uuid_pk()
    script_id: Mapped[uuid.UUID] = _fk("scripts.id")
    scene_number: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    end_time: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    section_type: Mapped[str] = mapped_column(String(60), nullable=False)
    narration: Mapped[str] = mapped_column(Text, nullable=False, default="")
    on_screen_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    visual_direction: Mapped[str | None] = mapped_column(Text, nullable=True)

    script: Mapped[Script] = relationship(back_populates="scenes")
    visual_recommendations: Mapped[list[VisualRecommendation]] = relationship(
        back_populates="scene", cascade="all, delete-orphan"
    )
    visual_assets: Mapped[list[VisualAsset]] = relationship(
        back_populates="scene", cascade="all, delete-orphan"
    )


class VisualRecommendation(Base, TimestampMixin):
    """An AI *recommendation* for a visual, NOT a discovered asset."""

    __tablename__ = "visual_recommendations"

    id: Mapped[uuid.UUID] = uuid_pk()
    scene_id: Mapped[uuid.UUID] = _fk("script_scenes.id")
    type: Mapped[VisualType] = mapped_column(nullable=False)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[VisualPriority] = mapped_column(default=VisualPriority.medium, nullable=False)

    scene: Mapped[ScriptScene] = relationship(back_populates="visual_recommendations")


class VisualAsset(Base, TimestampMixin):
    """A concrete asset *discovered* by an image search provider."""

    __tablename__ = "visual_assets"

    id: Mapped[uuid.UUID] = uuid_pk()
    scene_id: Mapped[uuid.UUID] = _fk("script_scenes.id")
    recommendation_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey(_q("visual_recommendations.id"), ondelete="SET NULL"),
        nullable=True,
    )
    url: Mapped[str] = mapped_column(Text, nullable=False)
    thumbnail_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    provider: Mapped[str] = mapped_column(String(60), nullable=False)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    creator: Mapped[str | None] = mapped_column(String(300), nullable=True)
    license: Mapped[str | None] = mapped_column(String(200), nullable=True)

    scene: Mapped[ScriptScene] = relationship(back_populates="visual_assets")


class Revision(Base, TimestampMixin):
    """Audit trail of regeneration/edit actions, for traceability and future personalization."""

    __tablename__ = "revisions"

    id: Mapped[uuid.UUID] = uuid_pk()
    project_id: Mapped[uuid.UUID] = _fk("content_projects.id")
    target: Mapped[RevisionTarget] = mapped_column(nullable=False)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    instruction: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Snapshot of the value before/after the operation for auditability.
    before: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    after: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    project: Mapped[ContentProject] = relationship(back_populates="revisions")
