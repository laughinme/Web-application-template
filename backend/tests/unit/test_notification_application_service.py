from types import SimpleNamespace
from uuid import uuid4

import pytest

from service.notifications.application.notification_service import NotificationApplicationService


class FakeEventsRepo:
    def __init__(self) -> None:
        self.events = []

    async def add(self, **kwargs):
        event = SimpleNamespace(id=uuid4(), **kwargs)
        self.events.append(event)
        return event


class FakeDeliveriesRepo:
    def __init__(self) -> None:
        self.deliveries = []

    async def add(self, **kwargs):
        self.deliveries.append(kwargs)
        return SimpleNamespace(id=uuid4(), **kwargs)


class FakePreferencesRepo:
    def __init__(self, row=None) -> None:
        self.row = row

    async def get_for_user_event(self, *, user_id, event_type):
        return self.row


class FakeTelegramLinksRepo:
    def __init__(self, link=None) -> None:
        self.link = link

    async def get_by_user_id(self, user_id):
        return self.link


@pytest.mark.unit
@pytest.mark.asyncio
async def test_enqueue_user_registered_creates_email_and_telegram_deliveries() -> None:
    user = SimpleNamespace(id=uuid4(), email="user@example.com", username="Mark")
    settings = SimpleNamespace(EMAIL_PROVIDER="resend", NOTIFICATIONS_ENABLED=True)

    svc = NotificationApplicationService(
        settings=settings,
        events_repo=FakeEventsRepo(),
        deliveries_repo=FakeDeliveriesRepo(),
        preferences_repo=FakePreferencesRepo(),
        telegram_links_repo=FakeTelegramLinksRepo(
            SimpleNamespace(
                chat_id=12345,
                telegram_user_id=54321,
                username="tguser",
                is_active=True,
            )
        ),
    )

    await svc.enqueue_user_registered(user)

    assert len(svc.deliveries_repo.deliveries) == 2

    email_delivery = next(d for d in svc.deliveries_repo.deliveries if d["channel"] == "email")
    telegram_delivery = next(d for d in svc.deliveries_repo.deliveries if d["channel"] == "telegram")

    assert email_delivery["provider"] == "resend"
    assert email_delivery["recipient"] == "user@example.com"

    assert telegram_delivery["provider"] == "telegram_bot"
    assert telegram_delivery["recipient"] == "12345"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_enqueue_user_registered_skips_telegram_without_link() -> None:
    user = SimpleNamespace(id=uuid4(), email="user@example.com", username="Mark")
    settings = SimpleNamespace(EMAIL_PROVIDER="noop", NOTIFICATIONS_ENABLED=True)

    svc = NotificationApplicationService(
        settings=settings,
        events_repo=FakeEventsRepo(),
        deliveries_repo=FakeDeliveriesRepo(),
        preferences_repo=FakePreferencesRepo(),
        telegram_links_repo=FakeTelegramLinksRepo(link=None),
    )

    await svc.enqueue_user_registered(user)

    assert len(svc.deliveries_repo.deliveries) == 1
    assert svc.deliveries_repo.deliveries[0]["channel"] == "email"
