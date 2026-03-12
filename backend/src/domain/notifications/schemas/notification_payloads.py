from pydantic import BaseModel, Field

from domain.notifications.enums import NotificationEventType


class UserRegisteredPayload(BaseModel):
    event_type: NotificationEventType = Field(default=NotificationEventType.USER_REGISTERED)
    user_email: str
    username: str | None = None
