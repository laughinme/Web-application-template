from aiogram import Router
from aiogram.types import Message

router = Router(name="telegram_fallback")


@router.message()
async def fallback_message(message: Message) -> None:
    await message.answer("Unknown command. Use /help to see available commands.")
