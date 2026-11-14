import logging
from collections.abc import Mapping
from datetime import UTC, datetime

from app.db.database import Database
from app.db.models import OutboxEvent
from app.domain.outbox import Handler, OutboxStatus, retry_delay

logger = logging.getLogger(__name__)

_ERROR_TEXT_MAX = 2000


class OutboxDispatcher:
    def __init__(
        self,
        db: Database,
        handlers: Mapping[str, Handler],
        *,
        batch_size: int,
        max_attempts: int,
    ) -> None:
        self._db = db
        self._handlers = handlers
        self._batch_size = batch_size
        self._max_attempts = max_attempts

    async def run_once(self) -> int:
        """Deliver one batch. Returns how many events were taken, so the caller can idle when 0."""
        now = datetime.now(UTC)
        async with self._db.unit_of_work() as uow:
            events = await uow.outbox.claim_batch(limit=self._batch_size, now=now)
            for event in events:
                await self._deliver(event, now)
        return len(events)

    async def _deliver(self, event: OutboxEvent, now: datetime) -> None:
        handler = self._handlers.get(event.topic)
        if handler is None:
            self._fail(event, now, f"no handler for topic {event.topic!r}", final=True)
            return

        event.attempts += 1
        try:
            await handler(event.payload)
        except Exception as exc:  # any handler failure is recorded and retried later
            self._fail(event, now, repr(exc), final=event.attempts >= self._max_attempts)
            return
        event.status = OutboxStatus.DONE
        event.processed_at = now

    def _fail(self, event: OutboxEvent, now: datetime, error: str, *, final: bool) -> None:
        event.last_error = error[:_ERROR_TEXT_MAX]
        if final:
            event.status = OutboxStatus.DEAD
            logger.error("outbox event %s (%s) is dead: %s", event.id, event.topic, error)
        else:
            event.available_at = now + retry_delay(event.attempts)
            logger.warning("outbox event %s (%s) failed: %s", event.id, event.topic, error)
