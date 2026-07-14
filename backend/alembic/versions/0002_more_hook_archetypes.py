"""add more hook archetypes

Revision ID: 0002_more_hook_archetypes
Revises: 0001_initial
Create Date: 2026-07-14
"""
from typing import Sequence, Union

from alembic import op

from app.core.config import settings

revision: str = "0002_more_hook_archetypes"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = settings.db_schema
NEW_VALUES = [
    "statistic",
    "story_open",
    "direct_question",
    "comparison",
    "pattern_interrupt",
]


def upgrade() -> None:
    # Postgres enums: ADD VALUE is transactional-DDL sensitive; use IF NOT EXISTS.
    op.execute(f'SET search_path TO "{SCHEMA}", public')
    for val in NEW_VALUES:
        op.execute(f"ALTER TYPE hookarchetype ADD VALUE IF NOT EXISTS '{val}'")


def downgrade() -> None:
    # Postgres cannot drop enum values without recreating the type; the extra
    # values are harmless, so downgrade is a no-op.
    pass
