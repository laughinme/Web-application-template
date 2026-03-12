from enum import StrEnum


class NotificationEventType(StrEnum):
    USER_REGISTERED = "user_registered"
    ADMIN_NEW_USER_REGISTERED = "admin_new_user_registered"
