from .base import EmailMessage, ProviderSendResult, TelegramMessage


class NoopProvider:
    async def send_email(self, message: EmailMessage) -> ProviderSendResult:
        return ProviderSendResult(provider_message_id=None)

    async def send_telegram(self, message: TelegramMessage) -> ProviderSendResult:
        return ProviderSendResult(provider_message_id=None)
