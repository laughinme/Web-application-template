from typing import Any

from app.domain.outbox import Handler, Topic
from app.service.ports import Notifier, ObjectDeleter


def build_handlers(notifier: Notifier, storage: ObjectDeleter) -> dict[str, Handler]:
    """One handler per `Topic`. They run in the worker after commit and must be idempotent."""

    async def user_registered(payload: dict[str, Any]) -> None:
        await notifier.send(f"New user registered: {payload['email']}")

    async def object_orphaned(payload: dict[str, Any]) -> None:
        # Deleting a missing key is a no-op in S3, so a retry after a crash is safe.
        await storage.delete(payload["key"])

    return {
        Topic.USER_REGISTERED: user_registered,
        Topic.STORAGE_OBJECT_ORPHANED: object_orphaned,
    }
