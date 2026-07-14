"""add 'idea' to revisiontarget enum

Revision ID: 0003_revisiontarget_idea
Revises: 0002_more_hook_archetypes
Create Date: 2026-07-14
"""
from typing import Sequence, Union

from alembic import op

from app.core.config import settings

revision: str = "0003_revisiontarget_idea"
down_revision: Union[str, None] = "0002_more_hook_archetypes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = settings.db_schema


def upgrade() -> None:
    op.execute(f'SET search_path TO "{SCHEMA}", public')
    op.execute("ALTER TYPE revisiontarget ADD VALUE IF NOT EXISTS 'idea'")


def downgrade() -> None:
    # Postgres cannot drop enum values without recreating the type; no-op.
    pass
