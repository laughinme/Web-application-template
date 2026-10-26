from datetime import UTC, datetime, timedelta
from uuid import UUID

from app.db.models import User
from app.db.uow import UnitOfWork
from app.domain.pagination import Cursor, Page
from app.domain.stats import DailyCount, UsersSummary
from app.domain.users import (
    CurrentUser,
    Role,
    UserNotFoundError,
    UserProfile,
    UserQuery,
    ensure_can_ban,
    ensure_can_change_role,
)
from app.service.mappers import to_profile
from app.service.ports import PublicUrls


class AdminUserService:
    def __init__(self, uow: UnitOfWork, urls: PublicUrls, actor: CurrentUser) -> None:
        self._uow = uow
        self._urls = urls
        self._actor = actor

    async def list_users(self, query: UserQuery) -> Page[UserProfile]:
        after = Cursor.decode(query.cursor) if query.cursor else None
        # One extra row tells us whether a next page exists without a COUNT query.
        rows = await self._uow.users.search(query, after=after, limit=query.limit + 1)
        page, has_more = rows[: query.limit], len(rows) > query.limit
        next_cursor = (
            Cursor(created_at=page[-1].created_at, id=page[-1].id).encode() if has_more else None
        )
        return Page(items=[to_profile(user, self._urls) for user in page], next_cursor=next_cursor)

    async def ban(self, user_id: UUID) -> UserProfile:
        user = await self._locked(user_id)
        ensure_can_ban(self._actor, target_id=user.id, target_role=user.role)
        if user.banned_at is None:
            now = datetime.now(UTC)
            user.banned_at = now
            user.auth_version += 1
            await self._uow.sessions.revoke_all(user.id, now=now)
        await self._uow.flush()
        return to_profile(user, self._urls)

    async def unban(self, user_id: UUID) -> UserProfile:
        user = await self._locked(user_id)
        user.banned_at = None
        await self._uow.flush()
        return to_profile(user, self._urls)

    async def set_role(self, user_id: UUID, role: Role) -> UserProfile:
        user = await self._locked(user_id)
        ensure_can_change_role(self._actor, target_id=user.id)
        user.role = role
        await self._uow.flush()
        return to_profile(user, self._urls)

    async def _locked(self, user_id: UUID) -> User:
        user = await self._uow.users.get(user_id, for_update=True)
        if user is None:
            raise UserNotFoundError()
        return user


class StatsService:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def users_summary(self) -> UsersSummary:
        now = datetime.now(UTC)
        return await self._uow.users.summary(now=now, since=now - timedelta(hours=24))

    async def registrations(self, days: int) -> list[DailyCount]:
        since = datetime.now(UTC) - timedelta(days=days)
        return await self._uow.users.registrations_by_day(since=since)
