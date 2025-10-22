"""introduce rbac tables and seed defaults

Revision ID: 6d5fe9b0b3f1
Revises: fa110bc90883
Create Date: 2025-08-20 12:00:00.000000

"""
from __future__ import annotations

from datetime import datetime, UTC
from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6d5fe9b0b3f1"
down_revision: Union[str, Sequence[str], None] = "fa110bc90883"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    
    op.create_table(
        "roles",
        sa.Column("id", sa.Uuid(), nullable=False, primary_key=True),
        sa.Column("slug", sa.String(length=64), nullable=False, unique=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_table(
        "permissions",
        sa.Column("id", sa.Uuid(), nullable=False, primary_key=True),
        sa.Column("slug", sa.String(length=128), nullable=False, unique=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.Uuid(), nullable=False),
        sa.Column("permission_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["permission_id"], ["permissions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("role_id", "permission_id"),
        sa.UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )

    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("role_id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "role_id"),
        sa.UniqueConstraint("user_id", "role_id", name="uq_user_role"),
    )
    op.create_index("ix_user_roles_role_id", "user_roles", ["role_id"])

    op.add_column(
        "users",
        sa.Column(
            "auth_version",
            sa.Integer(),
            nullable=False,
            server_default="1",
        ),
    )

    roles_table = sa.table(
        "roles",
        sa.column("id", sa.Uuid()),
        sa.column("slug", sa.String()),
        sa.column("name", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("created_at", sa.DateTime(timezone=True)),
    )
    permissions_table = sa.table(
        "permissions",
        sa.column("id", sa.Uuid()),
        sa.column("slug", sa.String()),
        sa.column("name", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("created_at", sa.DateTime(timezone=True)),
    )
    role_permissions_table = sa.table(
        "role_permissions",
        sa.column("role_id", sa.Uuid()),
        sa.column("permission_id", sa.Uuid()),
    )

    member_role_id = uuid4()
    admin_role_id = uuid4()

    op.bulk_insert(
        roles_table,
        [
            {
                "id": member_role_id,
                "slug": "member",
                "name": "Member",
                "description": "Default role for registered users",
            },
            {
                "id": admin_role_id,
                "slug": "admin",
                "name": "Administrator",
                "description": "Full administrative access",
            },
        ],
    )

    permissions_seed = {
        "users.read": uuid4(),
        "users.ban": uuid4(),
        "users.manage_roles": uuid4(),
    }

    op.bulk_insert(
        permissions_table,
        [
            {
                "id": permissions_seed["users.read"],
                "slug": "users.read",
                "name": "Read users",
                "description": "Access to list and view user accounts",
            },
            {
                "id": permissions_seed["users.ban"],
                "slug": "users.ban",
                "name": "Ban users",
                "description": "Ability to ban or unban user accounts",
            },
            {
                "id": permissions_seed["users.manage_roles"],
                "slug": "users.manage_roles",
                "name": "Manage user roles",
                "description": "Assign or revoke user roles",
            },
        ],
    )

    op.bulk_insert(
        role_permissions_table,
        [
            {
                "role_id": admin_role_id,
                "permission_id": permissions_seed["users.read"],
            },
            {
                "role_id": admin_role_id,
                "permission_id": permissions_seed["users.ban"],
            },
            {
                "role_id": admin_role_id,
                "permission_id": permissions_seed["users.manage_roles"],
            },
        ],
    )

    conn.execute(
        sa.text(
            "INSERT INTO user_roles (user_id, role_id) "
            "SELECT id, :member_role_id FROM users"
        ),
        {"member_role_id": str(member_role_id)}
    )

    conn.execute(
        sa.text(
            "INSERT INTO user_roles (user_id, role_id) "
            "SELECT id, :admin_role_id FROM users WHERE is_admin = TRUE"
        ),
        {"admin_role_id": str(admin_role_id)}
    )

    op.drop_column("users", "is_admin")


def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "is_admin",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )

    op.execute(
        sa.text(
            "UPDATE users SET is_admin = TRUE "
            "WHERE id IN ("
            "    SELECT user_id FROM user_roles ur "
            "    JOIN roles r ON r.id = ur.role_id "
            "    WHERE r.slug = 'admin'"
            ")"
        )
    )

    op.drop_column("users", "auth_version")

    op.drop_index("ix_user_roles_role_id", table_name="user_roles")
    op.drop_table("user_roles")
    op.drop_table("role_permissions")
    op.drop_table("permissions")
    op.drop_table("roles")
