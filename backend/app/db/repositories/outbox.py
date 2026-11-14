from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import OutboxEvent
from app.domain.outbox import ClaimedEvent, OutboxStatus, Topic


class OutboxRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def add(self, topic: Topic, payload: dict[str, Any]) -> None:
        self._session.add(OutboxEvent(topic=topic.value, payload=payload))

    async def claim(self, *, limit: int, now: datetime, lease: timedelta) -> list[ClaimedEvent]:
        """
        Take due events and hide them for `lease` by moving `available_at` forward. The caller
        commits right away, so the row locks last milliseconds; if the worker dies mid-delivery,
        the events become due again when the lease ends.
        """
        # SKIP LOCKED lets several workers claim side by side without taking the same event.
        due = (
            select(OutboxEvent.id)
            .where(OutboxEvent.status == OutboxStatus.PENDING, OutboxEvent.available_at <= now)
            .order_by(OutboxEvent.available_at)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        stmt = (
            update(OutboxEvent)
            .where(OutboxEvent.id.in_(due.scalar_subquery()))
            .values(available_at=now + lease, attempts=OutboxEvent.attempts + 1)
            .returning(OutboxEvent.id, OutboxEvent.topic, OutboxEvent.payload, OutboxEvent.attempts)
        )
        rows = (await self._session.execute(stmt)).all()
        return [
            ClaimedEvent(id=event_id, topic=topic, payload=payload, attempts=attempts)
            for event_id, topic, payload, attempts in rows
        ]

    async def mark_done(self, event_id: UUID, *, now: datetime) -> None:
        await self._session.execute(
            update(OutboxEvent)
            .where(OutboxEvent.id == event_id)
            .values(status=OutboxStatus.DONE, processed_at=now, last_error=None)
        )

    async def mark_failed(self, event_id: UUID, *, error: str, retry_at: datetime | None) -> None:
        """`retry_at=None` means no more attempts: the event is dead and waits for a human."""
        values: dict[str, Any] = {"last_error": error}
        if retry_at is None:
            values["status"] = OutboxStatus.DEAD
        else:
            values["available_at"] = retry_at
        await self._session.execute(
            update(OutboxEvent).where(OutboxEvent.id == event_id).values(**values)
        )
