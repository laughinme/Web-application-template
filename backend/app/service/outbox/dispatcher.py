import logging
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from app.db.database import Database
from app.domain.outbox import ClaimedEvent, Handler, retry_delay

logger = logging.getLogger(__name__)

_ERROR_TEXT_MAX = 2000


@dataclass(frozen=True, slots=True)
class _Outcome:
    event: ClaimedEvent
    error: str | None = None


class OutboxDispatcher:
    """
    Delivers committed events in three steps, so no transaction is open while a handler waits
    on the network: claim a batch (short transaction), run handlers (no transaction), record
    the outcomes (short transaction). Like the request dependency and the CLI, it owns its UoWs.
    """

    def __init__(
        self,
        db: Database,
        handlers: Mapping[str, Handler],
        *,
        batch_size: int,
        max_attempts: int,
        lease: timedelta = timedelta(minutes=5),
    ) -> None:
        self._db = db
        self._handlers = handlers
        self._batch_size = batch_size
        self._max_attempts = max_attempts
        self._lease = lease

    async def run_once(self) -> int:
        """Deliver one batch. Returns how many events were taken, so the caller can idle when 0."""
        async with self._db.unit_of_work() as uow:
            events = await uow.outbox.claim(
                limit=self._batch_size, now=datetime.now(UTC), lease=self._lease
            )
        if not events:
            return 0

        outcomes = [await self._deliver(event) for event in events]

        now = datetime.now(UTC)
        async with self._db.unit_of_work() as uow:
            for outcome in outcomes:
                if outcome.error is None:
                    await uow.outbox.mark_done(outcome.event.id, now=now)
                else:
                    await uow.outbox.mark_failed(
                        outcome.event.id,
                        error=outcome.error[:_ERROR_TEXT_MAX],
                        retry_at=self._retry_at(outcome, now),
                    )
        return len(events)

    async def _deliver(self, event: ClaimedEvent) -> _Outcome:
        handler = self._handlers.get(event.topic)
        if handler is None:
            return _Outcome(event, f"no handler for topic {event.topic!r}")
        try:
            await handler(event.payload)
        except Exception as exc:  # any handler failure is recorded and retried later
            return _Outcome(event, repr(exc))
        return _Outcome(event)

    def _retry_at(self, outcome: _Outcome, now: datetime) -> datetime | None:
        event = outcome.event
        if event.topic not in self._handlers or event.attempts >= self._max_attempts:
            logger.error("outbox event %s (%s) is dead: %s", event.id, event.topic, outcome.error)
            return None
        logger.warning("outbox event %s (%s) failed: %s", event.id, event.topic, outcome.error)
        return now + retry_delay(event.attempts)
