from typing import Annotated

from fastapi import APIRouter, Depends, Header

from core.config import get_settings
from core.errors import UnauthorizedError
from domain.users import TelegramLinkRequest
from service.users import UserService, get_user_service

router = APIRouter()


@router.post("/telegram/link")
async def link_telegram_account(
    payload: TelegramLinkRequest,
    svc: Annotated[UserService, Depends(get_user_service)],
    link_secret: Annotated[str | None, Header(alias="X-Telegram-Link-Secret")] = None,
) -> dict[str, str]:
    settings = get_settings()
    if not settings.TELEGRAM_LINK_SECRET or link_secret != settings.TELEGRAM_LINK_SECRET:
        raise UnauthorizedError("Invalid Telegram link secret")

    user = await svc.link_telegram_by_token(
        token=payload.token,
        chat_id=payload.chat_id,
        username=payload.username,
    )
    return {"status": "linked", "user_id": str(user.id)}
