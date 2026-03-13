import asyncio
import logging

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from .backend import link_telegram_account
from .config import get_settings

logger = logging.getLogger(__name__)
router = Router()


def _extract_start_payload(text: str | None) -> str | None:
    if not text:
        return None
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        return None
    payload = parts[1].strip()
    return payload or None


@router.message(CommandStart())
async def on_start(message: Message) -> None:
    payload = _extract_start_payload(message.text)
    if not payload or not payload.startswith("link_"):
        await message.answer(
            "Бот подключен. Для привязки аккаунта откройте deeplink из приложения.",
        )
        return

    token = payload.removeprefix("link_")
    settings = get_settings()
    try:
        linked = await link_telegram_account(
            settings=settings,
            token=token,
            chat_id=str(message.chat.id),
            username=message.from_user.username if message.from_user else None,
        )
    except Exception:
        logger.exception("Failed to link Telegram account")
        await message.answer("Ошибка привязки. Попробуйте еще раз через приложение.")
        return

    if not linked:
        await message.answer(
            "Ссылка недействительна или истекла. Сгенерируйте новую в приложении.",
        )
        return

    await message.answer("Telegram успешно привязан к вашему аккаунту.")


async def run() -> None:
    settings = get_settings()
    bot = Bot(token=settings.BOT_TOKEN)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)
    await dispatcher.start_polling(bot)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s",
    )
    asyncio.run(run())


if __name__ == "__main__":
    main()
