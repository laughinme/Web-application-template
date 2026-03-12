from typing import Annotated

from aiogram.types import Update
from fastapi import APIRouter, Header, Request

from core.config import get_settings
from core.errors import NotFoundError, UnauthorizedError
from service.telegram import get_telegram_bot, get_telegram_dispatcher

router = APIRouter()


@router.post("/telegram")
async def telegram_webhook(
    request: Request,
    telegram_secret: Annotated[str | None, Header(alias="X-Telegram-Bot-Api-Secret-Token")] = None,
) -> dict[str, bool]:
    settings = get_settings()
    if not settings.TELEGRAM_ENABLED:
        raise NotFoundError("Telegram integration is disabled")

    if settings.TELEGRAM_WEBHOOK_SECRET and telegram_secret != settings.TELEGRAM_WEBHOOK_SECRET:
        raise UnauthorizedError("Invalid Telegram webhook secret")

    body = await request.json()

    bot = get_telegram_bot(settings)
    dispatcher = get_telegram_dispatcher()

    update = Update.model_validate(body, context={"bot": bot})
    await dispatcher.feed_update(bot, update)

    return {"ok": True}
