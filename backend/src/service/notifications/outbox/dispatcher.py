from typing import Any
from uuid import UUID, uuid4

from arq.connections import ArqRedis

from core.config import Settings
from database.relational_db.tables.notifications import (
    NotificationDeliveriesInterface,
    NotificationEventsInterface,
)
from domain.notifications.enums import NotificationDeliveryStatus
from service.notifications.providers import (
    EmailMessage,
    EmailProvider,
    ProviderPermanentError,
    ProviderTemporaryError,
    TelegramMessage,
    TelegramProvider,
)
from service.notifications.templates import TemplateRegistry

from .retry_policy import compute_next_attempt


class NotificationOutboxDispatcher:
    def __init__(
        self,
        *,
        settings: Settings,
        deliveries_repo: NotificationDeliveriesInterface,
        events_repo: NotificationEventsInterface,
        email_provider: EmailProvider | None,
        telegram_provider: TelegramProvider | None,
    ) -> None:
        self.settings = settings
        self.deliveries_repo = deliveries_repo
        self.events_repo = events_repo
        self.email_provider = email_provider
        self.telegram_provider = telegram_provider

    async def enqueue_due_jobs(self, redis: ArqRedis, *, limit: int | None = None) -> int:
        due = await self.deliveries_repo.list_due(limit=limit or self.settings.NOTIFICATION_DISPATCH_BATCH_SIZE)
        for delivery in due:
            await redis.enqueue_job("deliver_notification", str(delivery.id))
        return len(due)

    async def deliver(self, delivery_id: UUID) -> None:
        delivery = await self.deliveries_repo.get_by_id(delivery_id)
        if delivery is None:
            return

        if delivery.status not in {
            NotificationDeliveryStatus.PENDING.value,
            NotificationDeliveryStatus.RETRY.value,
        }:
            return

        locked = await self.deliveries_repo.claim(delivery, lock_token=uuid4().hex)
        if not locked:
            return

        delivery = await self.deliveries_repo.get_by_id(delivery_id)
        if delivery is None:
            return

        event = await self.events_repo.get_by_id(delivery.event_id)
        if event is None:
            await self.deliveries_repo.mark_failed(
                delivery,
                error_code="EVENT_NOT_FOUND",
                error_message="Notification event not found",
            )
            return

        if not self.settings.NOTIFICATIONS_ENABLED:
            await self.deliveries_repo.mark_skipped(delivery, reason="Notifications are disabled")
            return

        try:
            if delivery.channel == "email":
                await self._send_email(delivery=delivery, event_type=event.event_type, payload=event.payload_json)
            elif delivery.channel == "telegram":
                await self._send_telegram(delivery=delivery, event_type=event.event_type, payload=event.payload_json)
            else:
                await self.deliveries_repo.mark_skipped(
                    delivery,
                    reason=f"Unsupported channel: {delivery.channel}",
                )
        except ProviderTemporaryError as exc:
            attempts_after = int(delivery.attempts or 0) + 1
            if attempts_after >= self.settings.NOTIFICATION_MAX_ATTEMPTS:
                await self.deliveries_repo.mark_failed(
                    delivery,
                    error_code=exc.code,
                    error_message=str(exc),
                )
            else:
                await self.deliveries_repo.mark_retry(
                    delivery,
                    error_code=exc.code,
                    error_message=str(exc),
                    next_attempt_at=compute_next_attempt(attempts_after),
                )
        except ProviderPermanentError as exc:
            await self.deliveries_repo.mark_failed(
                delivery,
                error_code=exc.code,
                error_message=str(exc),
            )

    async def recover_stuck(self) -> int:
        return await self.deliveries_repo.recover_stuck(self.settings.NOTIFICATION_PROCESSING_TIMEOUT_SEC)

    async def _send_email(self, *, delivery: Any, event_type: str, payload: dict) -> None:
        template = TemplateRegistry.email(event_type, payload)
        if template is None:
            await self.deliveries_repo.mark_skipped(
                delivery,
                reason=f"No email template for event '{event_type}'",
            )
            return

        if self.settings.EMAIL_PROVIDER == "noop" or self.email_provider is None:
            await self.deliveries_repo.mark_skipped(delivery, reason="Email provider is noop")
            return

        result = await self.email_provider.send_email(
            EmailMessage(
                to=delivery.recipient,
                subject=template.subject,
                html=template.html,
                text=template.text,
                idempotency_key=f"delivery:{delivery.id}",
            )
        )
        await self.deliveries_repo.mark_sent(delivery, provider_message_id=result.provider_message_id)

    async def _send_telegram(self, *, delivery: Any, event_type: str, payload: dict) -> None:
        text = TemplateRegistry.telegram(event_type, payload)
        if text is None:
            await self.deliveries_repo.mark_skipped(
                delivery,
                reason=f"No telegram template for event '{event_type}'",
            )
            return

        if not self.settings.TELEGRAM_ENABLED or self.telegram_provider is None:
            await self.deliveries_repo.mark_skipped(delivery, reason="Telegram provider is disabled")
            return

        try:
            chat_id = int(delivery.recipient)
        except ValueError as exc:
            raise ProviderPermanentError("Invalid telegram chat id", code="BAD_TELEGRAM_RECIPIENT") from exc

        result = await self.telegram_provider.send_telegram(
            TelegramMessage(chat_id=chat_id, text=text)
        )
        await self.deliveries_repo.mark_sent(delivery, provider_message_id=result.provider_message_id)
