from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramNetworkError, TelegramRetryAfter

from service.telegram import get_telegram_bot

from .base import ProviderPermanentError, ProviderSendResult, ProviderTemporaryError, TelegramMessage


class TelegramBotProvider:
    async def send_telegram(self, message: TelegramMessage) -> ProviderSendResult:
        bot = get_telegram_bot()

        try:
            sent = await bot.send_message(
                chat_id=message.chat_id,
                text=message.text,
                disable_web_page_preview=True,
            )
        except TelegramRetryAfter as exc:
            raise ProviderTemporaryError(str(exc), code="TELEGRAM_RETRY_AFTER") from exc
        except TelegramNetworkError as exc:
            raise ProviderTemporaryError(str(exc), code="TELEGRAM_NETWORK_ERROR") from exc
        except TelegramForbiddenError as exc:
            raise ProviderPermanentError(str(exc), code="TELEGRAM_FORBIDDEN") from exc
        except TelegramBadRequest as exc:
            raise ProviderPermanentError(str(exc), code="TELEGRAM_BAD_REQUEST") from exc

        return ProviderSendResult(provider_message_id=str(sent.message_id))
