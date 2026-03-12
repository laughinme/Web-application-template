from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from core.config import get_settings
from database.relational_db import UoW, get_session_factory
from database.relational_db.tables.notifications import (
    NotificationPreferencesInterface,
    TelegramLinkTokensInterface,
    TelegramLinksInterface,
)
from service.notifications.application import NotificationPreferenceService
from service.telegram.deeplink_service import TelegramDeepLinkService

router = Router(name="telegram_stop")


@router.message(Command("stop"))
async def stop_notifications(message: Message) -> None:
    settings = get_settings()
    session_factory = get_session_factory(settings)

    async with session_factory() as session:
        async with UoW(session) as uow:
            links_repo = TelegramLinksInterface(session)
            preferences_repo = NotificationPreferencesInterface(session)
            service = TelegramDeepLinkService(
                settings=settings,
                uow=uow,
                tokens_repo=TelegramLinkTokensInterface(session),
                links_repo=links_repo,
                preferences_repo=preferences_repo,
            )

            linked = await links_repo.get_by_chat_id(message.chat.id)
            if linked:
                pref_service = NotificationPreferenceService(preferences_repo)
                await pref_service.set_telegram_enabled(linked.user_id, False)

            success = await service.deactivate_by_chat_id(message.chat.id)

    if success:
        await message.answer("Telegram notifications disabled and chat unlinked.")
    else:
        await message.answer("This chat is not linked yet.")
