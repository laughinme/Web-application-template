from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from .notifications_table import (
    UserNotificationSettings,
    UserTelegramAccount,
    UserTelegramLinkToken,
)


class NotificationInterface:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_settings(self, user_id: UUID | str) -> UserNotificationSettings | None:
        return await self.session.scalar(
            select(UserNotificationSettings).where(UserNotificationSettings.user_id == user_id),
        )

    async def get_or_create_settings(self, user_id: UUID | str) -> UserNotificationSettings:
        settings = await self.get_settings(user_id)
        if settings is not None:
            return settings

        settings = UserNotificationSettings(user_id=user_id)
        self.session.add(settings)
        await self.session.flush()
        return settings

    async def get_telegram_account(self, user_id: UUID | str) -> UserTelegramAccount | None:
        return await self.session.scalar(
            select(UserTelegramAccount).where(UserTelegramAccount.user_id == user_id),
        )

    async def upsert_telegram_account(
        self,
        *,
        user_id: UUID | str,
        chat_id: str,
        username: str | None,
    ) -> UserTelegramAccount:
        account = await self.get_telegram_account(user_id)
        if account is None:
            account = UserTelegramAccount(
                user_id=user_id,
                chat_id=chat_id,
                username=username,
            )
            self.session.add(account)
        else:
            account.chat_id = chat_id
            account.username = username

        await self.session.flush()
        return account

    async def unlink_telegram_account(self, user_id: UUID | str) -> None:
        await self.session.execute(
            delete(UserTelegramAccount).where(UserTelegramAccount.user_id == user_id),
        )
        await self.session.flush()

    async def upsert_telegram_link_token(
        self,
        *,
        user_id: UUID | str,
        token_hash: str,
        expires_at: datetime,
    ) -> UserTelegramLinkToken:
        link = await self.session.scalar(
            select(UserTelegramLinkToken).where(UserTelegramLinkToken.user_id == user_id),
        )
        if link is None:
            link = UserTelegramLinkToken(
                user_id=user_id,
                token_hash=token_hash,
                expires_at=expires_at,
            )
            self.session.add(link)
        else:
            link.token_hash = token_hash
            link.expires_at = expires_at

        await self.session.flush()
        return link

    async def get_telegram_link_token_by_hash(
        self,
        token_hash: str,
    ) -> UserTelegramLinkToken | None:
        return await self.session.scalar(
            select(UserTelegramLinkToken).where(UserTelegramLinkToken.token_hash == token_hash),
        )

    async def clear_telegram_link_token(self, user_id: UUID | str) -> None:
        await self.session.execute(
            delete(UserTelegramLinkToken).where(UserTelegramLinkToken.user_id == user_id),
        )
        await self.session.flush()
