from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="telegram_help")


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    await message.answer(
        "Available commands:\n"
        "/start - connect account using deep link\n"
        "/settings - toggle Telegram notification preferences\n"
        "/stop - disable Telegram notifications"
    )
