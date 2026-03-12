from uuid import UUID

from database.relational_db.tables.notifications import NotificationPreferencesInterface
from domain.notifications import NotificationEventType


class NotificationPreferenceService:
    def __init__(self, preferences_repo: NotificationPreferencesInterface) -> None:
        self.preferences_repo = preferences_repo

    async def get_user_defaults(self, user_id: UUID) -> dict[str, bool]:
        row = await self.preferences_repo.get_for_user_event(
            user_id=user_id,
            event_type=NotificationEventType.USER_REGISTERED.value,
        )
        if row is None:
            return {
                "email_enabled": True,
                "telegram_enabled": True,
            }

        return {
            "email_enabled": bool(row.email_enabled),
            "telegram_enabled": bool(row.telegram_enabled),
        }

    async def set_telegram_enabled(self, user_id: UUID, enabled: bool) -> None:
        current = await self.preferences_repo.get_for_user_event(
            user_id=user_id,
            event_type=NotificationEventType.USER_REGISTERED.value,
        )
        email_enabled = current.email_enabled if current else True

        await self.preferences_repo.upsert(
            user_id=user_id,
            event_type=NotificationEventType.USER_REGISTERED.value,
            email_enabled=email_enabled,
            telegram_enabled=enabled,
        )
