import logging
from contextlib import asynccontextmanager
from urllib.parse import urlparse
from uuid import UUID

from arq import cron
from arq.connections import RedisSettings

from core.config import get_settings
from database.relational_db import UoW, get_session_factory
from database.relational_db.tables.notifications import (
    NotificationDeliveriesInterface,
    NotificationEventsInterface,
)
from service.notifications import build_email_provider, build_telegram_provider
from service.notifications.outbox import NotificationOutboxDispatcher

logger = logging.getLogger(__name__)


def _redis_settings_from_url(url: str) -> RedisSettings:
    parsed = urlparse(url)
    db = 0
    if parsed.path and parsed.path != "/":
        db = int(parsed.path.removeprefix("/"))

    return RedisSettings(
        host=parsed.hostname or "localhost",
        port=parsed.port or 6379,
        database=db,
        username=parsed.username,
        password=parsed.password,
        ssl=parsed.scheme == "rediss",
    )


@asynccontextmanager
async def _dispatcher_context():
    settings = get_settings()
    session_factory = get_session_factory(settings)
    async with session_factory() as session:
        async with UoW(session):
            yield NotificationOutboxDispatcher(
                settings=settings,
                deliveries_repo=NotificationDeliveriesInterface(session),
                events_repo=NotificationEventsInterface(session),
                email_provider=build_email_provider(settings),
                telegram_provider=build_telegram_provider(settings),
            )


async def deliver_notification(ctx: dict, delivery_id: str) -> None:
    async with _dispatcher_context() as dispatcher:
        await dispatcher.deliver(UUID(delivery_id))


async def dispatch_due_deliveries(ctx: dict) -> int:
    async with _dispatcher_context() as dispatcher:
        count = await dispatcher.enqueue_due_jobs(ctx["redis"])
        logger.info("Enqueued %s notification deliveries", count)
        return count


async def recover_stuck_deliveries(ctx: dict) -> int:
    async with _dispatcher_context() as dispatcher:
        recovered = await dispatcher.recover_stuck()
        logger.info("Recovered %s stuck deliveries", recovered)
        return recovered


class WorkerSettings:
    settings = get_settings()

    functions = [deliver_notification, dispatch_due_deliveries, recover_stuck_deliveries]
    redis_settings = _redis_settings_from_url(settings.REDIS_URL)

    cron_jobs = [
        cron(dispatch_due_deliveries, second={0, 10, 20, 30, 40, 50}),
        cron(recover_stuck_deliveries, minute={0, 10, 20, 30, 40, 50}, second=5),
    ]

    max_tries = settings.NOTIFICATION_MAX_ATTEMPTS
