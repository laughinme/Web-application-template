from dataclasses import dataclass

from domain.notifications.enums import NotificationEventType


@dataclass(slots=True)
class EmailTemplate:
    subject: str
    html: str
    text: str


def render_email_template(event_type: str, payload: dict) -> EmailTemplate | None:
    if event_type == NotificationEventType.USER_REGISTERED.value:
        username = payload.get("username") or "there"
        email = payload.get("user_email") or ""
        return EmailTemplate(
            subject="Welcome to the platform",
            html=f"<p>Hello, <b>{username}</b>!</p><p>Your account {email} is ready.</p>",
            text=f"Hello, {username}! Your account {email} is ready.",
        )

    return None
