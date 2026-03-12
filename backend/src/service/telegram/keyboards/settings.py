from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def build_settings_keyboard(*, telegram_enabled: bool) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    status = "ON" if telegram_enabled else "OFF"
    builder.button(
        text=f"Telegram notifications: {status}",
        callback_data="notif:toggle:telegram",
    )
    builder.adjust(1)
    return builder.as_markup()
