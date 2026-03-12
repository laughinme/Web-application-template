from aiogram import Dispatcher

from .handlers import get_telegram_handlers_router

_telegram_dispatcher: Dispatcher | None = None


def get_telegram_dispatcher() -> Dispatcher:
    global _telegram_dispatcher
    if _telegram_dispatcher is None:
        dispatcher = Dispatcher()
        dispatcher.include_router(get_telegram_handlers_router())
        _telegram_dispatcher = dispatcher
    return _telegram_dispatcher
