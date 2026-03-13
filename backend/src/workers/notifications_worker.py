import asyncio
import logging
from typing import Any

import resend
from aiogram import Bot
from arq.worker import Retry
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from core.config import Settings, get_settings
from database.relational_db import (
    NotificationInterface,
    UserInterface,
    dispose_engine,
    get_session_factory,
)

logger = logging.getLogger(__name__)


async def _send_email(
    *,
    settings: Settings,
    to_email: str,
    subject: str,
    text: str,
    html: str | None,
) -> None:
    if not settings.RESEND_API_KEY or not settings.RESEND_FROM_EMAIL:
        logger.info("Skipping e-mail: RESEND_API_KEY/RESEND_FROM_EMAIL are not configured")
        return

    payload: dict[str, Any] = {
        "from": settings.RESEND_FROM_EMAIL,
        "to": [to_email],
        "subject": subject,
    }
    if html:
        payload["html"] = html
    if text:
        payload["text"] = text

    def _send() -> None:
        resend.api_key = settings.RESEND_API_KEY
        resend.Emails.send(payload)

    await asyncio.to_thread(_send)


async def _send_telegram(*, bot: Bot | None, chat_id: str, text: str) -> None:
    if bot is None:
        logger.info("Skipping Telegram: TELEGRAM_BOT_TOKEN is not configured")
        return

    await bot.send_message(chat_id=chat_id, text=text)


def _to_telegram_text(subject: str, text: str) -> str:
    return f"{subject}\n\n{text}".strip()


async def deliver_user_notification_job(
    ctx: dict[str, Any],
    user_id: str,
    subject: str,
    text: str,
    html: str | None = None,
) -> None:
    settings: Settings = ctx["settings"]
    session_factory: async_sessionmaker[AsyncSession] = ctx["session_factory"]
    bot: Bot | None = ctx.get("bot")

    async with session_factory() as session:
        user_repo = UserInterface(session)
        notification_repo = NotificationInterface(session)
        user = await user_repo.get_by_id(user_id)
        notification_settings = (
            await notification_repo.get_settings(user_id)
            if user is not None
            else None
        )
        telegram_account = (
            await notification_repo.get_telegram_account(user_id)
            if user is not None
            else None
        )

    if user is None:
        logger.warning("User %s not found, notification skipped", user_id)
        return

    errors: list[str] = []
    email_enabled = (
        notification_settings.email_enabled if notification_settings is not None else True
    )
    telegram_enabled = (
        notification_settings.telegram_enabled if notification_settings is not None else False
    )

    if email_enabled:
        try:
            await _send_email(
                settings=settings,
                to_email=user.email,
                subject=subject,
                text=text,
                html=html,
            )
        except Exception as exc:
            errors.append(f"email failed: {exc}")

    if (
        telegram_enabled
        and telegram_account is not None
    ):
        try:
            await _send_telegram(
                bot=bot,
                chat_id=telegram_account.chat_id,
                text=_to_telegram_text(subject, text),
            )
        except Exception as exc:
            errors.append(f"telegram failed: {exc}")

    if errors:
        logger.warning("Notification delivery failed for user %s: %s", user_id, "; ".join(errors))
        raise Retry(seconds=5)


async def deliver_admin_text_job(ctx: dict[str, Any], text: str) -> None:
    settings: Settings = ctx["settings"]
    bot: Bot | None = ctx.get("bot")
    errors: list[str] = []

    if settings.NOTIFY_ADMIN_EMAIL:
        try:
            await _send_email(
                settings=settings,
                to_email=settings.NOTIFY_ADMIN_EMAIL,
                subject="Backend notification",
                text=text,
                html=None,
            )
        except Exception as exc:
            errors.append(f"admin email failed: {exc}")

    if settings.NOTIFY_ADMIN_TELEGRAM_CHAT_ID:
        try:
            await _send_telegram(
                bot=bot,
                chat_id=settings.NOTIFY_ADMIN_TELEGRAM_CHAT_ID,
                text=text,
            )
        except Exception as exc:
            errors.append(f"admin telegram failed: {exc}")

    if errors:
        logger.warning("Admin notification delivery failed: %s", "; ".join(errors))
        raise Retry(seconds=5)


async def on_startup(ctx: dict[str, Any]) -> None:
    settings = get_settings()
    session_factory = get_session_factory(settings)
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN) if settings.TELEGRAM_BOT_TOKEN else None
    ctx["settings"] = settings
    ctx["session_factory"] = session_factory
    ctx["bot"] = bot

    logger.info("Notifications worker started")


async def on_shutdown(ctx: dict[str, Any]) -> None:
    bot: Bot | None = ctx.get("bot")
    if bot is not None:
        await bot.session.close()
    await dispose_engine()
    logger.info("Notifications worker stopped")


_settings = get_settings()


class WorkerSettings:
    functions = [deliver_user_notification_job, deliver_admin_text_job]
    redis_settings = {"redis_url": _settings.REDIS_URL}
    queue_name = _settings.ARQ_NOTIFICATIONS_QUEUE
    max_tries = _settings.ARQ_DEFAULT_MAX_TRIES
    on_startup = on_startup
    on_shutdown = on_shutdown
