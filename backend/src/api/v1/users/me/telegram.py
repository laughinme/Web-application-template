from typing import Annotated

from fastapi import APIRouter, Depends

from core.config import Settings, get_settings
from core.errors import BadRequestError
from core.security import auth_user
from database.relational_db import UoW, User, get_uow
from database.relational_db.tables.notifications import (
    NotificationPreferencesInterface,
    TelegramLinkTokensInterface,
    TelegramLinksInterface,
)
from domain.notifications import TelegramConnectLinkResponse
from service.telegram import TelegramDeepLinkService

router = APIRouter()


@router.post(
    path="/me/telegram/connect-link",
    response_model=TelegramConnectLinkResponse,
    summary="Generate Telegram deep link for account connection",
)
async def create_telegram_connect_link(
    user: Annotated[User, Depends(auth_user)],
    uow: Annotated[UoW, Depends(get_uow)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TelegramConnectLinkResponse:
    if not settings.TELEGRAM_ENABLED:
        raise BadRequestError("Telegram integration is disabled")
    if not settings.TELEGRAM_BOT_USERNAME:
        raise BadRequestError("TELEGRAM_BOT_USERNAME is not configured")

    service = TelegramDeepLinkService(
        settings=settings,
        uow=uow,
        tokens_repo=TelegramLinkTokensInterface(uow.session),
        links_repo=TelegramLinksInterface(uow.session),
        preferences_repo=NotificationPreferencesInterface(uow.session),
    )
    return await service.create_connect_link(user.id)
