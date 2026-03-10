"""add language_code to users

Revision ID: 8f4c8b7d1a2e
Revises: a629654c84b7
Create Date: 2026-03-10 22:36:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8f4c8b7d1a2e"
down_revision: Union[str, Sequence[str], None] = "a629654c84b7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("language_code", sa.String(length=2), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "language_code")
