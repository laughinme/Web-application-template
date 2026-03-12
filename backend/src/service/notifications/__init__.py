from typing import Annotated

from fastapi import Depends

from core.config import Settings, get_settings
from database.relational_db import UoW, get_uow
from database.relational_db.tables.notifications import (
    NotificationDeliveriesInterface,
    NotificationEventsInterface,
    NotificationPreferencesInterface,
    TelegramLinksInterface,
)

from .application import NotificationApplicationService, NotificationPreferenceService
from .providers import NoopProvider, ResendProvider, TelegramBotProvider


def get_notification_service(
    uow: Annotated[UoW, Depends(get_uow)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> NotificationApplicationService:
    session = uow.session
    return NotificationApplicationService(
        settings=settings,
        events_repo=NotificationEventsInterface(session),
        deliveries_repo=NotificationDeliveriesInterface(session),
        preferences_repo=NotificationPreferencesInterface(session),
        telegram_links_repo=TelegramLinksInterface(session),
    )


def get_notification_preference_service(
    uow: Annotated[UoW, Depends(get_uow)],
) -> NotificationPreferenceService:
    return NotificationPreferenceService(NotificationPreferencesInterface(uow.session))


def build_email_provider(settings: Settings):
    if settings.EMAIL_PROVIDER == "resend":
        return ResendProvider(
            api_key=settings.RESEND_API_KEY,
            from_email=settings.EMAIL_FROM,
            reply_to=settings.EMAIL_REPLY_TO,
        )
    return NoopProvider()


def build_telegram_provider(settings: Settings):
    if settings.TELEGRAM_ENABLED and settings.TELEGRAM_BOT_TOKEN:
        return TelegramBotProvider()
    return NoopProvider()
