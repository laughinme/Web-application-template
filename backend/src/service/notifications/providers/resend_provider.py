import asyncio
import json
import urllib.error
import urllib.request

from .base import EmailMessage, ProviderPermanentError, ProviderSendResult, ProviderTemporaryError


class ResendProvider:
    API_URL = "https://api.resend.com/emails"

    def __init__(self, *, api_key: str, from_email: str, reply_to: str | None = None) -> None:
        self.api_key = api_key
        self.from_email = from_email
        self.reply_to = reply_to

    def _send_sync(self, message: EmailMessage) -> ProviderSendResult:
        if not self.api_key:
            raise ProviderPermanentError("Resend API key is not configured", code="RESEND_NOT_CONFIGURED")

        payload: dict[str, str | list[str]] = {
            "from": self.from_email,
            "to": [message.to],
            "subject": message.subject,
        }
        if message.html:
            payload["html"] = message.html
        if message.text:
            payload["text"] = message.text
        if self.reply_to:
            payload["reply_to"] = [self.reply_to]

        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if message.idempotency_key:
            headers["Idempotency-Key"] = message.idempotency_key

        request = urllib.request.Request(
            self.API_URL,
            data=data,
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                body = response.read().decode("utf-8")
                parsed = json.loads(body) if body else {}
                return ProviderSendResult(provider_message_id=parsed.get("id"))
        except urllib.error.HTTPError as exc:
            body_text = exc.read().decode("utf-8", errors="ignore")
            message_text = body_text or str(exc)
            if exc.code >= 500 or exc.code == 429:
                raise ProviderTemporaryError(message_text, code=f"RESEND_HTTP_{exc.code}") from exc
            raise ProviderPermanentError(message_text, code=f"RESEND_HTTP_{exc.code}") from exc
        except urllib.error.URLError as exc:
            raise ProviderTemporaryError(str(exc), code="RESEND_NETWORK_ERROR") from exc

    async def send_email(self, message: EmailMessage) -> ProviderSendResult:
        return await asyncio.to_thread(self._send_sync, message)
