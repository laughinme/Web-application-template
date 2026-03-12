from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from core.config import get_settings
from database.relational_db import UoW, get_session_factory
from database.relational_db.tables.notifications import (
    NotificationPreferencesInterface,
    TelegramLinksInterface,
)
from service.notifications.application import NotificationPreferenceService
from service.telegram.keyboards.settings import build_settings_keyboard

router = Router(name="telegram_settings")


def _render_settings_text(telegram_enabled: bool) -> str:
    status = "enabled" if telegram_enabled else "disabled"
    return f"Telegram notifications are currently {status}."


@router.message(Command("settings"))
async def settings_command(message: Message) -> None:
    if message.chat.type != ChatType.PRIVATE:
        await message.answer("Settings are available only in private chat.")
        return

    settings = get_settings()
    session_factory = get_session_factory(settings)

    async with session_factory() as session:
        async with UoW(session):
            links_repo = TelegramLinksInterface(session)
            preferences_repo = NotificationPreferencesInterface(session)

            link = await links_repo.get_by_chat_id(message.chat.id)
            if link is None or not link.is_active:
                await message.answer("This chat is not linked. Use Telegram connect link from website profile.")
                return

            pref_service = NotificationPreferenceService(preferences_repo)
            state = await pref_service.get_user_defaults(link.user_id)

    telegram_enabled = bool(state["telegram_enabled"])
    await message.answer(
        _render_settings_text(telegram_enabled),
        reply_markup=build_settings_keyboard(telegram_enabled=telegram_enabled),
    )


@router.callback_query(F.data == "notif:toggle:telegram")
async def toggle_telegram(callback: CallbackQuery) -> None:
    if callback.message is None:
        await callback.answer("No message context", show_alert=True)
        return

    settings = get_settings()
    session_factory = get_session_factory(settings)

    async with session_factory() as session:
        async with UoW(session):
            links_repo = TelegramLinksInterface(session)
            preferences_repo = NotificationPreferencesInterface(session)

            link = await links_repo.get_by_chat_id(callback.message.chat.id)
            if link is None or not link.is_active:
                await callback.answer("Chat is not linked", show_alert=True)
                return

            pref_service = NotificationPreferenceService(preferences_repo)
            current = await pref_service.get_user_defaults(link.user_id)
            new_value = not bool(current["telegram_enabled"])

            await pref_service.set_telegram_enabled(link.user_id, new_value)

    await callback.message.edit_text(
        _render_settings_text(new_value),
        reply_markup=build_settings_keyboard(telegram_enabled=new_value),
    )
    await callback.answer("Updated")
