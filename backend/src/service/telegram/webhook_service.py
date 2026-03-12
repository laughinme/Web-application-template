import logging

from core.config import Settings

from .bot import get_telegram_bot

logger = logging.getLogger(__name__)


async def sync_telegram_webhook(*, settings: Settings) -> None:
    if not settings.TELEGRAM_ENABLED:
        return
    if not settings.TELEGRAM_WEBHOOK_URL:
        logger.info("Telegram webhook URL is empty, skipping webhook sync")
        return

    bot = get_telegram_bot(settings)
    await bot.set_webhook(
        url=settings.TELEGRAM_WEBHOOK_URL,
        secret_token=settings.TELEGRAM_WEBHOOK_SECRET or None,
        drop_pending_updates=False,
    )
    logger.info("Telegram webhook is configured: %s", settings.TELEGRAM_WEBHOOK_URL)


async def clear_telegram_webhook(*, settings: Settings | None = None) -> None:
    try:
        bot = get_telegram_bot(settings)
    except Exception:
        return

    await bot.delete_webhook(drop_pending_updates=False)
