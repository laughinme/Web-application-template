from aiogram import Router

from .fallback import router as fallback_router
from .help import router as help_router
from .settings import router as settings_router
from .start import router as start_router
from .stop import router as stop_router


def get_telegram_handlers_router() -> Router:
    router = Router(name="telegram_handlers")
    router.include_router(start_router)
    router.include_router(help_router)
    router.include_router(settings_router)
    router.include_router(stop_router)
    router.include_router(fallback_router)
    return router
