"""normalize user notifications

Revision ID: 5f3a1a7c2d6f
Revises: b9f0b3ad4f78
Create Date: 2026-03-13 00:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5f3a1a7c2d6f"
down_revision: Union[str, Sequence[str], None] = "b9f0b3ad4f78"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_notification_settings",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("email_enabled", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("telegram_enabled", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
    )

    op.create_table(
        "user_telegram_accounts",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("chat_id", sa.String(length=64), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("chat_id"),
    )

    op.create_table(
        "user_telegram_link_tokens",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id"),
        sa.UniqueConstraint("token_hash"),
    )

    op.execute(
        """
        INSERT INTO user_notification_settings (
            user_id,
            email_enabled,
            telegram_enabled,
            updated_at,
            created_at
        )
        SELECT
            id,
            COALESCE(notify_email, true),
            COALESCE(notify_telegram, false),
            NOW(),
            NOW()
        FROM users
        """,
    )

    op.execute(
        """
        INSERT INTO user_telegram_accounts (
            user_id,
            chat_id,
            username,
            updated_at,
            created_at
        )
        SELECT
            id,
            telegram_chat_id,
            telegram_username,
            NOW(),
            NOW()
        FROM users
        WHERE telegram_chat_id IS NOT NULL
        """,
    )

    op.drop_constraint("uq_users_telegram_link_token", "users", type_="unique")
    op.drop_column("users", "telegram_link_expires_at")
    op.drop_column("users", "telegram_link_token")
    op.drop_column("users", "telegram_username")
    op.drop_column("users", "telegram_chat_id")
    op.drop_column("users", "notify_telegram")
    op.drop_column("users", "notify_email")


def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column("notify_email", sa.Boolean(), server_default="true", nullable=False),
    )
    op.add_column(
        "users",
        sa.Column("notify_telegram", sa.Boolean(), server_default="false", nullable=False),
    )
    op.add_column("users", sa.Column("telegram_chat_id", sa.String(length=64), nullable=True))
    op.add_column("users", sa.Column("telegram_username", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("telegram_link_token", sa.String(length=64), nullable=True))
    op.add_column(
        "users",
        sa.Column("telegram_link_expires_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_unique_constraint("uq_users_telegram_link_token", "users", ["telegram_link_token"])

    op.execute(
        """
        UPDATE users AS u
        SET
            notify_email = s.email_enabled,
            notify_telegram = s.telegram_enabled
        FROM user_notification_settings AS s
        WHERE s.user_id = u.id
        """,
    )
    op.execute(
        """
        UPDATE users AS u
        SET
            telegram_chat_id = t.chat_id,
            telegram_username = t.username
        FROM user_telegram_accounts AS t
        WHERE t.user_id = u.id
        """,
    )

    op.drop_table("user_telegram_link_tokens")
    op.drop_table("user_telegram_accounts")
    op.drop_table("user_notification_settings")
