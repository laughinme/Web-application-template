import httpx

from app.core.config import Settings
from app.infra.notifications.log import LogNotifier
from app.infra.notifications.telegram import TelegramNotifier
from app.service.ports import Notifier

__all__ = ["LogNotifier", "TelegramNotifier", "build_notifier"]


def build_notifier(settings: Settings, http: httpx.AsyncClient) -> Notifier:
    """Picks the adapter from settings. A new channel (email, Slack) is one more file here."""
    if settings.notifications_provider == "telegram":
        return TelegramNotifier(
            http,
            bot_token=settings.telegram_bot_token.get_secret_value(),
            chat_id=settings.telegram_chat_id,
        )
    return LogNotifier()
