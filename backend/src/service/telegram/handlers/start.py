from aiogram import Router
from aiogram.enums import ChatType
from aiogram.filters import CommandObject, CommandStart
from aiogram.types import Message

from core.config import get_settings
from database.relational_db import UoW, get_session_factory
from database.relational_db.tables.notifications import (
    NotificationPreferencesInterface,
    TelegramLinkTokensInterface,
    TelegramLinksInterface,
)
from service.telegram.deeplink_service import TelegramDeepLinkService

router = Router(name="telegram_start")


@router.message(CommandStart(deep_link=True))
async def start_with_payload(message: Message, command: CommandObject) -> None:
    if message.chat.type != ChatType.PRIVATE:
        await message.answer("Please use this command in a private chat with the bot.")
        return

    payload = command.args or ""
    if not payload:
        await message.answer("Empty link payload received. Open connect link from the website again.")
        return

    settings = get_settings()
    session_factory = get_session_factory(settings)

    async with session_factory() as session:
        async with UoW(session) as uow:
            service = TelegramDeepLinkService(
                settings=settings,
                uow=uow,
                tokens_repo=TelegramLinkTokensInterface(session),
                links_repo=TelegramLinksInterface(session),
                preferences_repo=NotificationPreferencesInterface(session),
            )
            linked_user_id = await service.consume_link_token_and_bind(
                token_payload=payload,
                telegram_user_id=message.from_user.id,
                chat_id=message.chat.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                language_code=message.from_user.language_code,
            )

    if linked_user_id is None:
        await message.answer("Link is invalid or expired. Please generate a new Telegram link in the website.")
        return

    await message.answer("Telegram account linked successfully. Notifications are enabled.")


@router.message(CommandStart())
async def start_plain(message: Message) -> None:
    await message.answer(
        "Hello. To link this bot with your account, open Telegram connect link from your profile settings."
    )
