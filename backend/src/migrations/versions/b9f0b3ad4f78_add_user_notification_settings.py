"""add user notification settings

Revision ID: b9f0b3ad4f78
Revises: a629654c84b7
Create Date: 2026-03-12 23:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b9f0b3ad4f78"
down_revision: Union[str, Sequence[str], None] = "a629654c84b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("notify_email", sa.Boolean(), server_default="true", nullable=False),
    )
    op.add_column(
        "users",
        sa.Column("notify_telegram", sa.Boolean(), server_default="false", nullable=False),
    )
    op.add_column("users", sa.Column("telegram_chat_id", sa.String(length=64), nullable=True))
    op.add_column(
        "users",
        sa.Column("telegram_username", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("telegram_link_token", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("telegram_link_expires_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_unique_constraint(
        "uq_users_telegram_link_token",
        "users",
        ["telegram_link_token"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_users_telegram_link_token", "users", type_="unique")
    op.drop_column("users", "telegram_link_expires_at")
    op.drop_column("users", "telegram_link_token")
    op.drop_column("users", "telegram_username")
    op.drop_column("users", "telegram_chat_id")
    op.drop_column("users", "notify_telegram")
    op.drop_column("users", "notify_email")
