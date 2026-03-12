from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, JSON, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..mixins import CreatedAtMixin
from ..table_base import Base

if TYPE_CHECKING:
    from .notification_deliveries import NotificationDelivery


class NotificationEvent(CreatedAtMixin, Base):
    __tablename__ = "notification_events"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), default=uuid4, primary_key=True)
    event_type: Mapped[str] = mapped_column(String(128), nullable=False, index=True)

    user_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True,
    )
    actor_user_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True,
    )

    payload_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    dedupe_key: Mapped[str | None] = mapped_column(String(256), nullable=True, index=True)
    scheduled_for: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    source: Mapped[str] = mapped_column(String(64), nullable=False, server_default="backend")

    deliveries: Mapped[list["NotificationDelivery"]] = relationship(
        "NotificationDelivery",
        back_populates="event",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
