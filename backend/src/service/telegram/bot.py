from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from core.config import Settings, get_settings

_telegram_bot: Bot | None = None


def get_telegram_bot(settings: Settings | None = None) -> Bot:
    global _telegram_bot
    settings = settings or get_settings()
    if _telegram_bot is None:
        parse_mode = ParseMode(settings.TELEGRAM_PARSE_MODE)
        _telegram_bot = Bot(
            token=settings.TELEGRAM_BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=parse_mode),
        )
    return _telegram_bot


async def close_telegram_bot() -> None:
    global _telegram_bot
    if _telegram_bot is None:
        return
    await _telegram_bot.session.close()
    _telegram_bot = None
