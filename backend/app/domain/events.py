from enum import StrEnum


class Topic(StrEnum):
    """Outbox topics: side effects that must happen only after the transaction commits."""

    USER_REGISTERED = "user.registered"
    STORAGE_OBJECT_ORPHANED = "storage.object_orphaned"


class OutboxStatus(StrEnum):
    PENDING = "pending"
    DONE = "done"
    DEAD = "dead"
