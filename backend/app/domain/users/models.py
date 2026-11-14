from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from app.domain.common.unset import UNSET, Unset


class Role(StrEnum):
    MEMBER = "member"
    ADMIN = "admin"


class Permission(StrEnum):
    USERS_READ = "users:read"
    USERS_BAN = "users:ban"
    USERS_MANAGE_ROLES = "users:manage_roles"
    STATS_READ = "stats:read"


# Roles are code, not data: a role is a named set of permissions, checked without a DB query.
ROLE_PERMISSIONS: Mapping[Role, frozenset[Permission]] = {
    Role.MEMBER: frozenset(),
    Role.ADMIN: frozenset(Permission),
}


@dataclass(frozen=True, slots=True)
class CurrentUser:
    """Who is calling. The only user object the API layer ever sees."""

    id: UUID
    role: Role
    session_id: UUID

    def can(self, permission: Permission) -> bool:
        return permission in ROLE_PERMISSIONS[self.role]


@dataclass(frozen=True, slots=True)
class UserProfile:
    id: UUID
    email: str
    username: str | None
    bio: str | None
    avatar_key: str | None
    avatar_url: str | None
    role: Role
    is_onboarded: bool
    is_banned: bool
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class ProfileChanges:
    username: str | Unset | None = UNSET
    bio: str | Unset | None = UNSET


@dataclass(frozen=True, slots=True)
class UserQuery:
    search: str | None = None
    role: Role | None = None
    banned: bool | None = None
    limit: int = 50
    cursor: str | None = None
