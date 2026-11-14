from collections.abc import Awaitable, Callable

from httpx import AsyncClient
from sqlalchemy import select, update

from app.db.database import Database
from app.db.models import OutboxEvent
from app.domain.outbox import OutboxStatus, Topic
from tests.factories import RecordingNotifier, register

RunOutbox = Callable[[], Awaitable[int]]


async def _events(db: Database) -> list[OutboxEvent]:
    async with db.unit_of_work() as uow:
        return list((await uow.session.scalars(select(OutboxEvent))).all())


async def _make_due(db: Database) -> None:
    async with db.unit_of_work() as uow:
        await uow.session.execute(update(OutboxEvent).values(available_at=OutboxEvent.created_at))


async def test_registration_notifies_after_commit(
    client: AsyncClient, db: Database, notifier: RecordingNotifier, run_outbox: RunOutbox
) -> None:
    await register(client, email="new@example.com")
    [event] = await _events(db)
    assert event.topic == Topic.USER_REGISTERED
    assert notifier.messages == []  # nothing is sent from inside the request

    assert await run_outbox() == 1

    assert notifier.messages == ["New user registered: new@example.com"]
    [event] = await _events(db)
    assert event.status == OutboxStatus.DONE


async def test_failed_delivery_is_retried_then_dead(
    client: AsyncClient, db: Database, notifier: RecordingNotifier, run_outbox: RunOutbox
) -> None:
    await register(client)
    notifier.fail_with = RuntimeError("telegram is down")

    for _ in range(3):  # run_outbox fixture allows 3 attempts
        await run_outbox()
        await _make_due(db)

    [event] = await _events(db)
    assert event.status == OutboxStatus.DEAD
    assert event.attempts == 3
    assert event.last_error is not None
    assert "telegram is down" in event.last_error


async def test_failed_request_leaves_no_event(client: AsyncClient, db: Database) -> None:
    await register(client, email="dup@example.com")

    duplicate = await client.post(
        "/api/v1/auth/register", json={"email": "dup@example.com", "password": "password-123"}
    )

    assert duplicate.status_code == 409
    assert len(await _events(db)) == 1
