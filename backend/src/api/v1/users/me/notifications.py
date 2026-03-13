from typing import Annotated

from fastapi import APIRouter, Depends

from core.security import auth_user
from database.relational_db import User
from domain.users import (
    TelegramDeeplinkResponse,
    UserNotificationSettings,
    UserNotificationSettingsPatch,
)
from service.users import UserService, get_user_service

router = APIRouter()


@router.get(
    path="/me/notifications",
    response_model=UserNotificationSettings,
    summary="Get notification settings",
)
async def get_notification_settings(
    user: Annotated[User, Depends(auth_user)],
    svc: Annotated[UserService, Depends(get_user_service)],
) -> UserNotificationSettings:
    return await svc.get_notification_settings(user=user)


@router.patch(
    path="/me/notifications",
    response_model=UserNotificationSettings,
    summary="Update notification settings",
)
async def patch_notification_settings(
    payload: UserNotificationSettingsPatch,
    user: Annotated[User, Depends(auth_user)],
    svc: Annotated[UserService, Depends(get_user_service)],
) -> UserNotificationSettings:
    return await svc.patch_notification_settings(user=user, payload=payload)


@router.post(
    path="/me/notifications/telegram/deeplink",
    response_model=TelegramDeeplinkResponse,
    summary="Generate Telegram deeplink for account linking",
)
async def create_telegram_deeplink(
    user: Annotated[User, Depends(auth_user)],
    svc: Annotated[UserService, Depends(get_user_service)],
) -> TelegramDeeplinkResponse:
    return await svc.create_telegram_deeplink(user=user)


@router.delete(
    path="/me/notifications/telegram",
    response_model=UserNotificationSettings,
    summary="Unlink Telegram and disable Telegram notifications",
)
async def unlink_telegram(
    user: Annotated[User, Depends(auth_user)],
    svc: Annotated[UserService, Depends(get_user_service)],
) -> UserNotificationSettings:
    return await svc.unlink_telegram(user=user)
