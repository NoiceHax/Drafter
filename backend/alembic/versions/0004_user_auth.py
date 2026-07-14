"""add auth columns to users

Revision ID: 0004_user_auth
Revises: 0003_revisiontarget_idea
Create Date: 2026-07-14
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

from app.core.config import settings

revision: str = "0004_user_auth"
down_revision: Union[str, None] = "0003_revisiontarget_idea"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SCHEMA = settings.db_schema


def upgrade() -> None:
    op.execute(f'SET search_path TO "{SCHEMA}", public')
    op.add_column(
        "users",
        sa.Column("password_hash", sa.String(255), nullable=True),
        schema=SCHEMA,
    )
    op.add_column(
        "users",
        sa.Column("is_alpha", sa.Boolean(), nullable=False, server_default=sa.false()),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.execute(f'SET search_path TO "{SCHEMA}", public')
    op.drop_column("users", "is_alpha", schema=SCHEMA)
    op.drop_column("users", "password_hash", schema=SCHEMA)
