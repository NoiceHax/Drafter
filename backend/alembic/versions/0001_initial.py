"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-07-13
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from app.core.config import settings

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = settings.db_schema

UUID = postgresql.UUID(as_uuid=True)
JSONB = postgresql.JSONB(astext_type=sa.Text())


PLATFORM = sa.Enum(
    "instagram_reels", "youtube_shorts", "tiktok", "youtube_long", "generic",
    name="platform",
)
TONE = sa.Enum(
    "educational", "dramatic", "conversational", "documentary", "humorous",
    "investigative", "custom", name="tone",
)
STAGE = sa.Enum(
    "idea", "keywords", "angles", "hooks", "research", "outline", "script", "visuals",
    name="projectstage",
)
KW_CATEGORY = sa.Enum("semantic", "story", "discovery", name="keywordcategory")
KW_STATUS = sa.Enum(
    "original", "recommended", "selected", "rejected", "custom", name="keywordstatus"
)
HOOK_ARCHETYPE = sa.Enum(
    "mystery_curiosity", "threat", "cold_open", "contrarian", "problem",
    name="hookarchetype",
)
VISUAL_TYPE = sa.Enum(
    "real_image", "historical_photo", "person", "event", "location", "product",
    "news_headline", "map", "chart", "screenshot", "b_roll", "generated_image",
    "text_animation", name="visualtype",
)
VISUAL_PRIORITY = sa.Enum("high", "medium", "low", name="visualpriority")
REVISION_TARGET = sa.Enum(
    "keyword_recommendations", "angles", "angle", "hooks", "hook", "research",
    "outline", "script", "scene_narration", "scene_visual_direction", "scene_visuals",
    name="revisiontarget",
)


def _stamp():
    return (
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def upgrade() -> None:
    op.execute(f'CREATE SCHEMA IF NOT EXISTS "{SCHEMA}"')
    op.execute(f'SET search_path TO "{SCHEMA}", public')

    op.create_table(
        "users",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("display_name", sa.String(120), nullable=True),
        sa.Column("preferred_tone", sa.String(40), nullable=True),
        sa.Column("preferred_platforms", JSONB, nullable=True),
        sa.Column("preferences", JSONB, nullable=True),
        *_stamp(),
    )

    op.create_table(
        "content_projects",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("user_id", UUID, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(200), nullable=True),
        sa.Column("idea", sa.Text(), nullable=False),
        sa.Column("platform", PLATFORM, nullable=False),
        sa.Column("target_duration_seconds", sa.Integer(), nullable=False),
        sa.Column("tone", TONE, nullable=False),
        sa.Column("custom_tone", sa.String(80), nullable=True),
        sa.Column("current_stage", STAGE, nullable=False),
        sa.Column("selected_angle_id", UUID, nullable=True),
        sa.Column("selected_hook_id", UUID, nullable=True),
        *_stamp(),
    )

    op.create_table(
        "keywords",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("project_id", UUID, sa.ForeignKey("content_projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("text", sa.String(160), nullable=False),
        sa.Column("status", KW_STATUS, nullable=False),
        sa.Column("category", KW_CATEGORY, nullable=True),
        sa.Column("selected", sa.Boolean(), nullable=False, server_default=sa.false()),
        *_stamp(),
        sa.UniqueConstraint("project_id", "text", name="uq_keyword_project_text"),
    )

    op.create_table(
        "keyword_recommendations",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("project_id", UUID, sa.ForeignKey("content_projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("keyword", sa.String(160), nullable=False),
        sa.Column("category", KW_CATEGORY, nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("relevance_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("accepted", sa.Boolean(), nullable=True),
        *_stamp(),
    )

    op.create_table(
        "content_angles",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("project_id", UUID, sa.ForeignKey("content_projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("style", sa.String(60), nullable=False),
        sa.Column("why_it_works", sa.Text(), nullable=False),
        sa.Column("estimated_audience_interest", sa.Float(), nullable=False, server_default="0"),
        sa.Column("selected", sa.Boolean(), nullable=False, server_default=sa.false()),
        *_stamp(),
    )

    op.create_table(
        "hooks",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("project_id", UUID, sa.ForeignKey("content_projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("archetype", HOOK_ARCHETYPE, nullable=False),
        sa.Column("suitability_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("estimated_duration_seconds", sa.Integer(), nullable=False, server_default="6"),
        sa.Column("unanswered_question", sa.Text(), nullable=True),
        sa.Column("story_payoff", sa.Text(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("selected", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("analysis", JSONB, nullable=True),
        *_stamp(),
    )

    op.create_table(
        "research_sources",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("project_id", UUID, sa.ForeignKey("content_projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("publisher", sa.String(200), nullable=True),
        sa.Column("published_at", sa.String(40), nullable=True),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("key_facts", JSONB, nullable=True),
        *_stamp(),
    )

    op.create_table(
        "story_outlines",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("project_id", UUID, sa.ForeignKey("content_projects.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("narrative_structure", sa.String(120), nullable=False),
        sa.Column("estimated_duration_seconds", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("sections", JSONB, nullable=False),
        *_stamp(),
    )

    op.create_table(
        "scripts",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("project_id", UUID, sa.ForeignKey("content_projects.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("platform", PLATFORM, nullable=False),
        sa.Column("target_duration_seconds", sa.Integer(), nullable=False),
        sa.Column("estimated_duration_seconds", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("hook_text", sa.Text(), nullable=False),
        sa.Column("hook_duration_seconds", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("cta_text", sa.Text(), nullable=True),
        sa.Column("cta_duration_seconds", sa.Integer(), nullable=False, server_default="0"),
        *_stamp(),
    )

    op.create_table(
        "script_scenes",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("script_id", UUID, sa.ForeignKey("scripts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scene_number", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("end_time", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("section_type", sa.String(60), nullable=False),
        sa.Column("narration", sa.Text(), nullable=False),
        sa.Column("on_screen_text", sa.Text(), nullable=True),
        sa.Column("visual_direction", sa.Text(), nullable=True),
        *_stamp(),
    )

    op.create_table(
        "visual_recommendations",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("scene_id", UUID, sa.ForeignKey("script_scenes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", VISUAL_TYPE, nullable=False),
        sa.Column("query", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("priority", VISUAL_PRIORITY, nullable=False),
        *_stamp(),
    )

    op.create_table(
        "visual_assets",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("scene_id", UUID, sa.ForeignKey("script_scenes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recommendation_id", UUID, sa.ForeignKey("visual_recommendations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("url", sa.Text(), nullable=False),
        sa.Column("thumbnail_url", sa.Text(), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("provider", sa.String(60), nullable=False),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("creator", sa.String(300), nullable=True),
        sa.Column("license", sa.String(200), nullable=True),
        *_stamp(),
    )

    op.create_table(
        "revisions",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("project_id", UUID, sa.ForeignKey("content_projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target", REVISION_TARGET, nullable=False),
        sa.Column("entity_id", UUID, nullable=True),
        sa.Column("instruction", sa.Text(), nullable=True),
        sa.Column("before", JSONB, nullable=True),
        sa.Column("after", JSONB, nullable=True),
        *_stamp(),
    )


def downgrade() -> None:
    op.execute(f'SET search_path TO "{SCHEMA}", public')
    for tbl in [
        "revisions", "visual_assets", "visual_recommendations", "script_scenes",
        "scripts", "story_outlines", "research_sources", "hooks", "content_angles",
        "keyword_recommendations", "keywords", "content_projects", "users",
    ]:
        op.drop_table(tbl)
    for enum in [
        REVISION_TARGET, VISUAL_PRIORITY, VISUAL_TYPE, HOOK_ARCHETYPE, KW_STATUS,
        KW_CATEGORY, STAGE, TONE, PLATFORM,
    ]:
        enum.drop(op.get_bind(), checkfirst=True)
