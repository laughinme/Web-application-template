from domain.notifications.enums import NotificationEventType


def render_telegram_template(event_type: str, payload: dict) -> str | None:
    if event_type == NotificationEventType.USER_REGISTERED.value:
        username = payload.get("username") or "friend"
        return f"Welcome, {username}. Your account was successfully created."

    return None
