from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from domain.notifications.enums import NotificationDeliveryStatus

from .notification_deliveries import NotificationDelivery
from .notification_events import NotificationEvent
from .notification_preferences import NotificationPreference
from .telegram_link_tokens import TelegramLinkToken
from .telegram_links import TelegramLink


class NotificationEventsInterface:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(
        self,
        *,
        event_type: str,
        payload_json: dict,
        user_id: UUID | None = None,
        actor_user_id: UUID | None = None,
        dedupe_key: str | None = None,
        source: str = "backend",
    ) -> NotificationEvent:
        event = NotificationEvent(
            event_type=event_type,
            payload_json=payload_json,
            user_id=user_id,
            actor_user_id=actor_user_id,
            dedupe_key=dedupe_key,
            source=source,
        )
        self.session.add(event)
        await self.session.flush()
        return event

    async def get_by_id(self, event_id: UUID) -> NotificationEvent | None:
        return await self.session.scalar(
            select(NotificationEvent).where(NotificationEvent.id == event_id)
        )


class NotificationDeliveriesInterface:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(
        self,
        *,
        event_id: UUID,
        channel: str,
        provider: str,
        recipient: str,
        recipient_snapshot_json: dict | None,
        status: NotificationDeliveryStatus = NotificationDeliveryStatus.PENDING,
    ) -> NotificationDelivery:
        delivery = NotificationDelivery(
            event_id=event_id,
            channel=channel,
            provider=provider,
            recipient=recipient,
            recipient_snapshot_json=recipient_snapshot_json,
            status=status.value,
        )
        self.session.add(delivery)
        await self.session.flush()
        return delivery

    async def get_by_id(self, delivery_id: UUID) -> NotificationDelivery | None:
        return await self.session.scalar(
            select(NotificationDelivery).where(NotificationDelivery.id == delivery_id)
        )

    async def list_due(self, limit: int = 100) -> list[NotificationDelivery]:
        now = datetime.now(UTC)
        stmt = (
            select(NotificationDelivery)
            .where(
                NotificationDelivery.status.in_(
                    [
                        NotificationDeliveryStatus.PENDING.value,
                        NotificationDeliveryStatus.RETRY.value,
                    ]
                )
            )
            .where(
                (NotificationDelivery.next_attempt_at.is_(None))
                | (NotificationDelivery.next_attempt_at <= now)
            )
            .order_by(NotificationDelivery.created_at.asc())
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        rows = await self.session.scalars(stmt)
        return list(rows.all())

    async def claim(self, delivery: NotificationDelivery, *, lock_token: str) -> bool:
        now = datetime.now(UTC)
        stmt = (
            update(NotificationDelivery)
            .where(NotificationDelivery.id == delivery.id)
            .where(
                NotificationDelivery.status.in_(
                    [
                        NotificationDeliveryStatus.PENDING.value,
                        NotificationDeliveryStatus.RETRY.value,
                    ]
                )
            )
            .values(
                status=NotificationDeliveryStatus.PROCESSING.value,
                locked_at=now,
                lock_token=lock_token,
                updated_at=now,
            )
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return (result.rowcount or 0) > 0

    async def mark_sent(
        self,
        delivery: NotificationDelivery,
        *,
        provider_message_id: str | None,
    ) -> None:
        now = datetime.now(UTC)
        delivery.status = NotificationDeliveryStatus.SENT.value
        delivery.provider_message_id = provider_message_id
        delivery.sent_at = now
        delivery.locked_at = None
        delivery.lock_token = None
        delivery.last_error_code = None
        delivery.last_error_message = None
        delivery.updated_at = now
        await self.session.flush()

    async def mark_retry(
        self,
        delivery: NotificationDelivery,
        *,
        error_code: str,
        error_message: str,
        next_attempt_at: datetime,
    ) -> None:
        now = datetime.now(UTC)
        delivery.status = NotificationDeliveryStatus.RETRY.value
        delivery.attempts = int(delivery.attempts or 0) + 1
        delivery.next_attempt_at = next_attempt_at
        delivery.last_error_code = error_code
        delivery.last_error_message = error_message
        delivery.locked_at = None
        delivery.lock_token = None
        delivery.updated_at = now
        await self.session.flush()

    async def mark_failed(
        self,
        delivery: NotificationDelivery,
        *,
        error_code: str,
        error_message: str,
    ) -> None:
        now = datetime.now(UTC)
        delivery.status = NotificationDeliveryStatus.FAILED.value
        delivery.attempts = int(delivery.attempts or 0) + 1
        delivery.last_error_code = error_code
        delivery.last_error_message = error_message
        delivery.locked_at = None
        delivery.lock_token = None
        delivery.updated_at = now
        await self.session.flush()

    async def mark_skipped(
        self,
        delivery: NotificationDelivery,
        *,
        reason: str,
    ) -> None:
        now = datetime.now(UTC)
        delivery.status = NotificationDeliveryStatus.SKIPPED.value
        delivery.last_error_code = "SKIPPED"
        delivery.last_error_message = reason
        delivery.locked_at = None
        delivery.lock_token = None
        delivery.updated_at = now
        await self.session.flush()

    async def recover_stuck(self, timeout_seconds: int, limit: int = 200) -> int:
        now = datetime.now(UTC)
        threshold = now.timestamp() - timeout_seconds
        threshold_dt = datetime.fromtimestamp(threshold, tz=UTC)

        stmt = (
            update(NotificationDelivery)
            .where(NotificationDelivery.status == NotificationDeliveryStatus.PROCESSING.value)
            .where(NotificationDelivery.locked_at.is_not(None))
            .where(NotificationDelivery.locked_at < threshold_dt)
            .values(
                status=NotificationDeliveryStatus.RETRY.value,
                next_attempt_at=now,
                locked_at=None,
                lock_token=None,
                last_error_code="WORKER_TIMEOUT",
                last_error_message="Recovered stuck delivery",
                updated_at=now,
            )
            .execution_options(synchronize_session=False)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return int(result.rowcount or 0)


class NotificationPreferencesInterface:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_for_user_event(
        self,
        *,
        user_id: UUID,
        event_type: str,
    ) -> NotificationPreference | None:
        stmt = (
            select(NotificationPreference)
            .where(NotificationPreference.user_id == user_id)
            .where(NotificationPreference.event_type == event_type)
        )
        return await self.session.scalar(stmt)

    async def upsert(
        self,
        *,
        user_id: UUID,
        event_type: str,
        email_enabled: bool,
        telegram_enabled: bool,
    ) -> NotificationPreference:
        current = await self.get_for_user_event(user_id=user_id, event_type=event_type)
        if current is None:
            current = NotificationPreference(
                user_id=user_id,
                event_type=event_type,
                email_enabled=email_enabled,
                telegram_enabled=telegram_enabled,
            )
            self.session.add(current)
            await self.session.flush()
            return current

        current.email_enabled = email_enabled
        current.telegram_enabled = telegram_enabled
        await self.session.flush()
        return current


class TelegramLinksInterface:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id: UUID) -> TelegramLink | None:
        return await self.session.scalar(select(TelegramLink).where(TelegramLink.user_id == user_id))

    async def get_by_chat_id(self, chat_id: int) -> TelegramLink | None:
        return await self.session.scalar(select(TelegramLink).where(TelegramLink.chat_id == chat_id))

    async def upsert_link(
        self,
        *,
        user_id: UUID,
        telegram_user_id: int,
        chat_id: int,
        username: str | None,
        first_name: str | None,
        last_name: str | None,
        language_code: str | None,
    ) -> TelegramLink:
        now = datetime.now(UTC)
        current = await self.get_by_user_id(user_id)
        if current is None:
            current = TelegramLink(
                user_id=user_id,
                telegram_user_id=telegram_user_id,
                chat_id=chat_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                language_code=language_code,
                linked_at=now,
                last_interaction_at=now,
                is_active=True,
            )
            self.session.add(current)
            await self.session.flush()
            return current

        current.telegram_user_id = telegram_user_id
        current.chat_id = chat_id
        current.username = username
        current.first_name = first_name
        current.last_name = last_name
        current.language_code = language_code
        current.is_active = True
        current.blocked_at = None
        current.last_interaction_at = now
        await self.session.flush()
        return current

    async def deactivate(self, user_id: UUID) -> None:
        current = await self.get_by_user_id(user_id)
        if current is None:
            return

        now = datetime.now(UTC)
        current.is_active = False
        current.blocked_at = now
        current.last_interaction_at = now
        await self.session.flush()


class TelegramLinkTokensInterface:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        *,
        user_id: UUID,
        token_hash: str,
        expires_at: datetime,
    ) -> TelegramLinkToken:
        token = TelegramLinkToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.session.add(token)
        await self.session.flush()
        return token

    async def get_valid(self, token_hash: str) -> TelegramLinkToken | None:
        now = datetime.now(UTC)
        stmt = (
            select(TelegramLinkToken)
            .where(TelegramLinkToken.token_hash == token_hash)
            .where(TelegramLinkToken.consumed_at.is_(None))
            .where(TelegramLinkToken.expires_at > now)
        )
        return await self.session.scalar(stmt)

    async def consume(self, token: TelegramLinkToken) -> None:
        token.consumed_at = datetime.now(UTC)
        await self.session.flush()
