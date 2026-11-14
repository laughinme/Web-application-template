from datetime import UTC, datetime, timedelta

from app.db.uow import UnitOfWork
from app.domain.stats import DailyCount, UsersSummary


class StatsService:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def users_summary(self) -> UsersSummary:
        now = datetime.now(UTC)
        return await self._uow.users.summary(now=now, since=now - timedelta(hours=24))

    async def registrations(self, days: int) -> list[DailyCount]:
        since = datetime.now(UTC) - timedelta(days=days)
        return await self._uow.users.registrations_by_day(since=since)
