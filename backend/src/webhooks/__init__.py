from fastapi import APIRouter


def get_webhooks() -> APIRouter:
    from .telegram import router as telegram_router

    webhooks = APIRouter(prefix="/webhooks", tags=["Webhooks"])
    webhooks.include_router(telegram_router)

    return webhooks
