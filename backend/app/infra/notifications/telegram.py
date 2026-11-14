import httpx


class TelegramNotifier:
    """`Notifier` adapter for the Telegram Bot API."""

    def __init__(self, http: httpx.AsyncClient, *, bot_token: str, chat_id: str) -> None:
        self._http = http
        self._url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        self._chat_id = chat_id

    async def send(self, text: str) -> None:
        response = await self._http.post(
            self._url,
            json={"chat_id": self._chat_id, "text": text, "disable_web_page_preview": True},
        )
        # Raise so the outbox retries the event instead of silently dropping it.
        response.raise_for_status()
