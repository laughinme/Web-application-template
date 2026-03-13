import asyncio
import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from core.config import get_settings
# from core.rbac import permissions_cache_key
from database.redis import CacheRepo
from domain.users import (
    AvatarPresignResponse,
    TelegramDeeplinkResponse,
    UserNotificationSettings,
    UserNotificationSettingsPatch,
    UserPatch,
)
from database.relational_db import (
    LanguagesInterface,
    NotificationInterface,
    RolesInterface,
    UserInterface,
    UoW,
    User,
)
from service.media import ALLOWED_AVATAR_CONTENT_TYPES, MediaStorageService
from .exceptions import (
    AvatarObjectNotFoundError,
    AvatarTooLargeError,
    AvatarUnsupportedContentTypeError,
    InvalidAvatarObjectKeyError,
    InvalidCursorError,
    TelegramAlreadyLinkedError,
    TelegramLinkTokenExpiredError,
    TelegramLinkTokenInvalidError,
    TelegramNotLinkedError,
    UnknownRolesError,
    UnsupportedAvatarContentTypeError,
)


class UserService:
    def __init__(
        self,
        uow: UoW,
        user_repo: UserInterface,
        lang_repo: LanguagesInterface,
        role_repo: RolesInterface,
        media_storage: MediaStorageService,
        cache_repo: CacheRepo | None = None,
        notification_repo: NotificationInterface | None = None,
    ):
        self.uow = uow
        self.user_repo = user_repo
        self.lang_repo = lang_repo
        self.role_repo = role_repo
        self.media_storage = media_storage
        self.cache_repo = cache_repo
        self.notification_repo = notification_repo
        self.settings = get_settings()
        
    async def get_user(self, user_id: UUID | str) -> User | None:
        return await self.user_repo.get_by_id(user_id)
        
    async def patch_user(self, payload: UserPatch, user: User):
        data = payload.model_dump(exclude_none=True)
        
        for field, value in data.items():
            setattr(user, field, value)
            
        await self.uow.commit()
            
        await self.uow.session.refresh(user)

    def _require_notification_repo(self) -> NotificationInterface:
        if self.notification_repo is None:
            raise RuntimeError("Notification repository is not configured")
        return self.notification_repo

    @staticmethod
    def _map_notification_settings(
        *,
        email_enabled: bool,
        telegram_enabled: bool,
        telegram_linked: bool,
        telegram_username: str | None,
    ) -> UserNotificationSettings:
        return UserNotificationSettings(
            email_enabled=email_enabled,
            telegram_enabled=telegram_enabled,
            telegram_linked=telegram_linked,
            telegram_username=telegram_username,
        )

    async def get_notification_settings(self, *, user: User) -> UserNotificationSettings:
        notification_repo = self._require_notification_repo()
        settings = await notification_repo.get_settings(user.id)
        if settings is None:
            settings = await notification_repo.get_or_create_settings(user.id)
            await self.uow.commit()
            await self.uow.session.refresh(settings)
        telegram_account = await notification_repo.get_telegram_account(user.id)
        return self._map_notification_settings(
            email_enabled=settings.email_enabled,
            telegram_enabled=settings.telegram_enabled,
            telegram_linked=telegram_account is not None,
            telegram_username=telegram_account.username if telegram_account else None,
        )

    async def patch_notification_settings(
        self,
        *,
        user: User,
        payload: UserNotificationSettingsPatch,
    ) -> UserNotificationSettings:
        notification_repo = self._require_notification_repo()
        settings = await notification_repo.get_or_create_settings(user.id)

        if payload.email_enabled is not None:
            settings.email_enabled = payload.email_enabled

        if payload.telegram_enabled is not None:
            telegram_account = await notification_repo.get_telegram_account(user.id)
            if payload.telegram_enabled and telegram_account is None:
                raise TelegramNotLinkedError()
            settings.telegram_enabled = payload.telegram_enabled

        await self.uow.commit()
        await self.uow.session.refresh(settings)
        telegram_account = await notification_repo.get_telegram_account(user.id)
        return self._map_notification_settings(
            email_enabled=settings.email_enabled,
            telegram_enabled=settings.telegram_enabled,
            telegram_linked=telegram_account is not None,
            telegram_username=telegram_account.username if telegram_account else None,
        )

    async def create_telegram_deeplink(self, *, user: User) -> TelegramDeeplinkResponse:
        if not self.settings.TELEGRAM_BOT_USERNAME:
            raise RuntimeError("TELEGRAM_BOT_USERNAME must be configured")

        notification_repo = self._require_notification_repo()
        token = secrets.token_urlsafe(24)
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        expires_at = datetime.now(UTC) + timedelta(
            seconds=self.settings.TELEGRAM_LINK_TOKEN_TTL_SEC,
        )

        await notification_repo.upsert_telegram_link_token(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        await self.uow.commit()

        deeplink_payload = f"link_{token}"
        deeplink_url = f"https://t.me/{self.settings.TELEGRAM_BOT_USERNAME}?start={deeplink_payload}"
        return TelegramDeeplinkResponse(
            deeplink_url=deeplink_url,
            expires_at=expires_at,
        )

    async def unlink_telegram(self, *, user: User) -> UserNotificationSettings:
        notification_repo = self._require_notification_repo()
        settings = await notification_repo.get_or_create_settings(user.id)
        settings.telegram_enabled = False
        await notification_repo.unlink_telegram_account(user.id)
        await notification_repo.clear_telegram_link_token(user.id)
        await self.uow.commit()
        return self._map_notification_settings(
            email_enabled=settings.email_enabled,
            telegram_enabled=settings.telegram_enabled,
            telegram_linked=False,
            telegram_username=None,
        )

    async def link_telegram_by_token(
        self,
        *,
        token: str,
        chat_id: str,
        username: str | None,
    ) -> User:
        notification_repo = self._require_notification_repo()
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        link_token = await notification_repo.get_telegram_link_token_by_hash(token_hash)
        if link_token is None:
            raise TelegramLinkTokenInvalidError()

        now = datetime.now(UTC)
        if link_token.expires_at < now:
            raise TelegramLinkTokenExpiredError()

        try:
            await notification_repo.upsert_telegram_account(
                user_id=link_token.user_id,
                chat_id=chat_id,
                username=username,
            )
        except IntegrityError as exc:
            raise TelegramAlreadyLinkedError() from exc

        settings = await notification_repo.get_or_create_settings(link_token.user_id)
        settings.telegram_enabled = True
        await notification_repo.clear_telegram_link_token(link_token.user_id)

        await self.uow.commit()

        user = await self.user_repo.get_by_id(link_token.user_id)
        if user is None:
            raise TelegramLinkTokenInvalidError()
        await self.uow.session.refresh(user)
        return user

    async def create_avatar_presign(
        self,
        *,
        user: User,
        filename: str,
        content_type: str,
    ) -> AvatarPresignResponse:
        if content_type not in ALLOWED_AVATAR_CONTENT_TYPES:
            raise UnsupportedAvatarContentTypeError(list(ALLOWED_AVATAR_CONTENT_TYPES))

        object_key = self.media_storage.build_avatar_key(user.id, filename, content_type)
        upload_url = self.media_storage.create_presigned_upload_url(
            bucket=self.settings.STORAGE_PUBLIC_BUCKET,
            key=object_key,
            content_type=content_type,
            expires_in=self.settings.STORAGE_PRESIGN_EXPIRES_SEC,
        )
        public_url = self.media_storage.build_public_url(
            bucket=self.settings.STORAGE_PUBLIC_BUCKET,
            key=object_key,
        )

        return AvatarPresignResponse(
            object_key=object_key,
            upload_url=upload_url,
            public_url=public_url,
            expires_in=self.settings.STORAGE_PRESIGN_EXPIRES_SEC,
        )

    async def confirm_avatar_upload(self, *, user: User, object_key: str) -> None:
        expected_prefix = f"avatars/{user.id}/"
        if not object_key.startswith(expected_prefix):
            raise InvalidAvatarObjectKeyError()

        stat = await asyncio.to_thread(
            lambda: self.media_storage.get_object_stat(
                bucket=self.settings.STORAGE_PUBLIC_BUCKET,
                key=object_key,
            ),
        )
        if stat is None:
            raise AvatarObjectNotFoundError()

        if stat.content_type not in ALLOWED_AVATAR_CONTENT_TYPES:
            raise AvatarUnsupportedContentTypeError()

        max_size_bytes = self.settings.MAX_PHOTO_SIZE * 1024 * 1024
        if stat.size_bytes > max_size_bytes:
            raise AvatarTooLargeError(self.settings.MAX_PHOTO_SIZE)

        previous_avatar_key = user.avatar_key
        user.avatar_key = object_key
        await self.uow.commit()
        await self.uow.session.refresh(user)

        if previous_avatar_key and previous_avatar_key != object_key:
            await asyncio.to_thread(
                lambda: self.media_storage.delete_object(
                    bucket=self.settings.STORAGE_PUBLIC_BUCKET,
                    key=previous_avatar_key,
                ),
            )

    async def remove_avatar(self, *, user: User) -> None:
        if not user.avatar_key:
            return

        avatar_key = user.avatar_key
        user.avatar_key = None
        await self.uow.commit()
        await self.uow.session.refresh(user)

        await asyncio.to_thread(
            lambda: self.media_storage.delete_object(
                bucket=self.settings.STORAGE_PUBLIC_BUCKET,
                key=avatar_key,
            ),
        )

    async def admin_list_users(
        self,
        *,
        banned: bool | None = None,
        search: str | None = None,
        limit: int = 50,
        cursor: str | None = None,
    ) -> tuple[list[User], str | None]:
        cursor_created_at = None
        cursor_id = None
        if cursor:
            try:
                ts_str, id_str = cursor.split("_", 1)
                cursor_created_at = datetime.fromisoformat(ts_str)
                cursor_id = UUID(id_str)
            except Exception:
                raise InvalidCursorError()

        users = await self.user_repo.admin_list_users(
            banned=banned,
            search=search,
            limit=limit,
            cursor_created_at=cursor_created_at,
            cursor_id=cursor_id,
        )

        next_cursor = None
        if len(users) == limit:
            last = users[-1]
            if last.created_at is None:
                next_cursor = None
            else:
                next_cursor = f"{last.created_at.isoformat()}_{last.id}"

        return users, next_cursor

    async def admin_set_ban(self, target: User, banned: bool) -> User:
        target.banned = banned
        target.bump_auth_version()
        await self.uow.commit()
        await self.uow.session.refresh(target)
        # await self._invalidate_permissions_cache(target.id, target.auth_version)
        return target

    async def list_languages(self, search: str, limit: int):
        return await self.lang_repo.search(search, limit)

    async def admin_assign_roles(
        self,
        target: User,
        role_slugs: list[str],
    ) -> User:
        unique_slugs = list(dict.fromkeys(role_slugs))
        roles = await self.role_repo.get_by_slugs(unique_slugs)
        found_slugs = {role.slug for role in roles}
        missing = [slug for slug in unique_slugs if slug not in found_slugs]
        if missing:
            raise UnknownRolesError(missing)

        await self.user_repo.assign_roles(target, roles)
        target.bump_auth_version()
        await self.uow.commit()
        await self.uow.session.refresh(target)

        # await self._invalidate_permissions_cache(target.id, target.auth_version)
        return target

    # async def _invalidate_permissions_cache(
    #     self,
    #     user_id: UUID | str,
    #     previous_version: int | None,
    # ) -> None:
    #     if not self.cache_repo or previous_version is None:
    #         return
    #     cache_key = permissions_cache_key(user_id, previous_version)
    #     await self.cache_repo.delete(cache_key)
