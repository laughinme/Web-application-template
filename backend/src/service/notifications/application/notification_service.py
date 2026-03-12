from uuid import UUID

from core.config import Settings
from database.relational_db import User
from database.relational_db.tables.notifications import (
    NotificationDeliveriesInterface,
    NotificationEventsInterface,
    NotificationPreferencesInterface,
    TelegramLinksInterface,
)
from domain.notifications import NotificationChannel, NotificationEventType, UserRegisteredPayload


class NotificationApplicationService:
    def __init__(
        self,
        *,
        settings: Settings,
        events_repo: NotificationEventsInterface,
        deliveries_repo: NotificationDeliveriesInterface,
        preferences_repo: NotificationPreferencesInterface,
        telegram_links_repo: TelegramLinksInterface,
    ) -> None:
        self.settings = settings
        self.events_repo = events_repo
        self.deliveries_repo = deliveries_repo
        self.preferences_repo = preferences_repo
        self.telegram_links_repo = telegram_links_repo

    async def enqueue_user_registered(self, user: User) -> UUID:
        payload = UserRegisteredPayload(
            user_email=user.email,
            username=user.username,
        )

        event = await self.events_repo.add(
            event_type=NotificationEventType.USER_REGISTERED.value,
            payload_json=payload.model_dump(mode="json"),
            user_id=user.id,
            source="auth.register",
        )

        if not self.settings.NOTIFICATIONS_ENABLED:
            return event.id

        preference = await self.preferences_repo.get_for_user_event(
            user_id=user.id,
            event_type=NotificationEventType.USER_REGISTERED.value,
        )
        email_enabled = preference.email_enabled if preference else True
        telegram_enabled = preference.telegram_enabled if preference else True

        if email_enabled:
            await self.deliveries_repo.add(
                event_id=event.id,
                channel=NotificationChannel.EMAIL.value,
                provider=self.settings.EMAIL_PROVIDER,
                recipient=user.email,
                recipient_snapshot_json={
                    "user_id": str(user.id),
                    "email": user.email,
                },
            )

        if telegram_enabled:
            link = await self.telegram_links_repo.get_by_user_id(user.id)
            if link and link.is_active:
                await self.deliveries_repo.add(
                    event_id=event.id,
                    channel=NotificationChannel.TELEGRAM.value,
                    provider="telegram_bot",
                    recipient=str(link.chat_id),
                    recipient_snapshot_json={
                        "user_id": str(user.id),
                        "chat_id": link.chat_id,
                        "telegram_user_id": link.telegram_user_id,
                        "username": link.username,
                    },
                )

        return event.id
