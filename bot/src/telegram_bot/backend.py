import httpx

from .config import Settings


async def link_telegram_account(
    *,
    settings: Settings,
    token: str,
    chat_id: str,
    username: str | None,
) -> bool:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            f"{settings.BACKEND_URL.rstrip('/')}/webhooks/telegram/link",
            headers={"X-Telegram-Link-Secret": settings.TELEGRAM_LINK_SECRET},
            json={
                "token": token,
                "chat_id": chat_id,
                "username": username,
            },
        )

    return 200 <= response.status_code < 300
