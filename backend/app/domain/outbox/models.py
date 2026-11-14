from collections.abc import Awaitable, Callable
from enum import StrEnum
from typing import Any


class Topic(StrEnum):
    """
    Outbox topics: side effects that must happen only after the transaction commits.
    Every topic needs a handler in `service/outbox/handlers.py` (a unit test checks it).
    """

    USER_REGISTERED = "user.registered"
    STORAGE_OBJECT_ORPHANED = "storage.object_orphaned"


class OutboxStatus(StrEnum):
    PENDING = "pending"
    DONE = "done"
    DEAD = "dead"


# Gets the event payload and performs the side effect. Delivery is at-least-once,
# so a handler may run twice for the same event and must be idempotent.
type Handler = Callable[[dict[str, Any]], Awaitable[None]]
