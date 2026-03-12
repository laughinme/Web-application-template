import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from core.config import Settings
from database.relational_db import UoW
from database.relational_db.tables.notifications import (
    NotificationPreferencesInterface,
    TelegramLinkTokensInterface,
    TelegramLinksInterface,
)
from domain.notifications import NotificationEventType, TelegramConnectLinkResponse


class TelegramDeepLinkService:
    def __init__(
        self,
        *,
        settings: Settings,
        uow: UoW,
        tokens_repo: TelegramLinkTokensInterface,
        links_repo: TelegramLinksInterface,
        preferences_repo: NotificationPreferencesInterface,
    ) -> None:
        self.settings = settings
        self.uow = uow
        self.tokens_repo = tokens_repo
        self.links_repo = links_repo
        self.preferences_repo = preferences_repo

    async def create_connect_link(self, user_id: UUID) -> TelegramConnectLinkResponse:
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
        expires_at = datetime.now(UTC) + timedelta(seconds=self.settings.TELEGRAM_LINK_TOKEN_TTL_SEC)

        await self.tokens_repo.create(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        bot_username = self.settings.TELEGRAM_BOT_USERNAME.lstrip("@")
        url = f"https://t.me/{bot_username}?start={raw_token}"

        return TelegramConnectLinkResponse(
            url=url,
            expires_in=self.settings.TELEGRAM_LINK_TOKEN_TTL_SEC,
        )

    async def consume_link_token_and_bind(
        self,
        *,
        token_payload: str,
        telegram_user_id: int,
        chat_id: int,
        username: str | None,
        first_name: str | None,
        last_name: str | None,
        language_code: str | None,
    ) -> UUID | None:
        token_hash = hashlib.sha256(token_payload.encode("utf-8")).hexdigest()
        token = await self.tokens_repo.get_valid(token_hash)
        if token is None:
            return None

        await self.tokens_repo.consume(token)
        await self.links_repo.upsert_link(
            user_id=token.user_id,
            telegram_user_id=telegram_user_id,
            chat_id=chat_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language_code=language_code,
        )

        current = await self.preferences_repo.get_for_user_event(
            user_id=token.user_id,
            event_type=NotificationEventType.USER_REGISTERED.value,
        )
        email_enabled = current.email_enabled if current else True

        await self.preferences_repo.upsert(
            user_id=token.user_id,
            event_type=NotificationEventType.USER_REGISTERED.value,
            email_enabled=email_enabled,
            telegram_enabled=True,
        )

        return token.user_id

    async def deactivate_by_chat_id(self, chat_id: int) -> bool:
        link = await self.links_repo.get_by_chat_id(chat_id)
        if link is None:
            return False

        await self.links_repo.deactivate(link.user_id)
        return True
