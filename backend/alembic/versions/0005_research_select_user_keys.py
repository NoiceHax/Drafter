"""research source selection + per-user API keys

Revision ID: 0005_research_select_user_keys
Revises: 0004_user_auth
Create Date: 2026-07-14
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.core.config import settings

revision: str = "0005_research_select_user_keys"
down_revision: Union[str, None] = "0004_user_auth"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = settings.db_schema


def upgrade() -> None:
    op.execute(f'SET search_path TO "{SCHEMA}", public')
    op.add_column(
        "research_sources",
        sa.Column("selected", sa.Boolean(), nullable=False, server_default=sa.true()),
        schema=SCHEMA,
    )
    for col in ("nvidia_api_key", "nvidia_model", "tavily_api_key", "pexels_api_key"):
        size = 120 if col == "nvidia_model" else 255
        op.add_column(
            "users",
            sa.Column(col, sa.String(size), nullable=True),
            schema=SCHEMA,
        )


def downgrade() -> None:
    op.execute(f'SET search_path TO "{SCHEMA}", public')
    for col in ("pexels_api_key", "tavily_api_key", "nvidia_model", "nvidia_api_key"):
        op.drop_column("users", col, schema=SCHEMA)
    op.drop_column("research_sources", "selected", schema=SCHEMA)
