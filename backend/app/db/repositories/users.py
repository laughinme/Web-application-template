from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

from sqlalchemy import func, or_, select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.domain.pagination import Cursor
from app.domain.stats import DailyCount, UsersSummary
from app.domain.users import UserQuery


def _like_pattern(text: str) -> str:
    escaped = text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, user: User) -> None:
        self._session.add(user)

    async def get(self, user_id: UUID, *, for_update: bool = False) -> User | None:
        if not for_update:
            return await self._session.get(User, user_id)
        # Row lock for read-modify-write (ban, role change, auth_version bump).
        stmt = (
            select(User)
            .where(User.id == user_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return await self._session.scalar(stmt)

    async def get_by_email(self, email: str) -> User | None:
        return await self._session.scalar(select(User).where(User.email == email))

    async def search(self, query: UserQuery, *, after: Cursor | None, limit: int) -> Sequence[User]:
        stmt = select(User)
        if query.search:
            pattern = _like_pattern(query.search.strip())
            stmt = stmt.where(
                or_(
                    User.email.ilike(pattern, escape="\\"),
                    User.username.ilike(pattern, escape="\\"),
                )
            )
        if query.role is not None:
            stmt = stmt.where(User.role == query.role)
        if query.banned is not None:
            stmt = stmt.where(
                User.banned_at.is_not(None) if query.banned else User.banned_at.is_(None)
            )
        if after is not None:
            stmt = stmt.where(tuple_(User.created_at, User.id) < (after.created_at, after.id))

        stmt = stmt.order_by(User.created_at.desc(), User.id.desc()).limit(limit)
        return (await self._session.scalars(stmt)).all()

    async def summary(self, *, now: datetime, since: datetime) -> UsersSummary:
        stmt = select(
            func.count(),
            func.count().filter(User.is_onboarded),
            func.count().filter(User.banned_at.is_not(None)),
            func.count().filter(User.created_at >= since),
        ).select_from(User)
        total, onboarded, banned, recent = (await self._session.execute(stmt)).one()
        return UsersSummary(
            generated_at=now,
            total=total,
            onboarded=onboarded,
            banned=banned,
            registered_last_24h=recent,
        )

    async def registrations_by_day(self, *, since: datetime) -> list[DailyCount]:
        day = func.date(func.timezone("UTC", User.created_at)).label("day")
        stmt = (
            select(day, func.count().label("count"))
            .where(User.created_at >= since)
            .group_by(day)
            .order_by(day)
        )
        rows = (await self._session.execute(stmt)).all()
        return [DailyCount(day=day_value, count=count) for day_value, count in rows]
