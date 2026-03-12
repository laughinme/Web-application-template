from dataclasses import dataclass
from typing import Protocol


class ProviderError(Exception):
    def __init__(self, message: str, *, code: str = "PROVIDER_ERROR") -> None:
        self.code = code
        super().__init__(message)


class ProviderTemporaryError(ProviderError):
    pass


class ProviderPermanentError(ProviderError):
    pass


@dataclass(slots=True)
class EmailMessage:
    to: str
    subject: str
    html: str | None = None
    text: str | None = None
    idempotency_key: str | None = None


@dataclass(slots=True)
class TelegramMessage:
    chat_id: int
    text: str


@dataclass(slots=True)
class ProviderSendResult:
    provider_message_id: str | None = None


class EmailProvider(Protocol):
    async def send_email(self, message: EmailMessage) -> ProviderSendResult: ...


class TelegramProvider(Protocol):
    async def send_telegram(self, message: TelegramMessage) -> ProviderSendResult: ...
