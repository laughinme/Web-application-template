from uuid import UUID

from arq import ArqRedis

from core.config import Settings, get_settings
from task_queue import get_arq_pool

from .constants import NOTIFY_ADMIN_TEXT_JOB, NOTIFY_USER_JOB


class NotificationService:
    def __init__(self, arq_pool: ArqRedis, settings: Settings | None = None):
        self.arq_pool = arq_pool
        self.settings = settings or get_settings()

    async def notify_user(
        self,
        *,
        user_id: UUID | str,
        subject: str,
        text: str,
        html: str | None = None,
    ) -> None:
        await self.arq_pool.enqueue_job(
            NOTIFY_USER_JOB,
            str(user_id),
            subject,
            text,
            html,
            _queue_name=self.settings.ARQ_NOTIFICATIONS_QUEUE,
        )

    async def send_text(self, text: str) -> None:
        await self.arq_pool.enqueue_job(
            NOTIFY_ADMIN_TEXT_JOB,
            text,
            _queue_name=self.settings.ARQ_NOTIFICATIONS_QUEUE,
        )


async def get_notification_service() -> NotificationService:
    arq_pool = await get_arq_pool()
    return NotificationService(arq_pool)
