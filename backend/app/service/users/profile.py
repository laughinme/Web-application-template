from secrets import token_hex
from uuid import UUID

from app.db.models import User
from app.db.uow import UnitOfWork
from app.domain.common import UNSET
from app.domain.outbox import Topic
from app.domain.users import (
    AvatarNotUploadedError,
    AvatarUpload,
    ProfileChanges,
    UserNotFoundError,
    UserProfile,
    avatar_key,
    ensure_own_avatar_key,
    ensure_valid_upload,
)
from app.ports import AvatarStorage
from app.service.users.mappers import to_profile


class ProfileService:
    def __init__(
        self,
        uow: UnitOfWork,
        storage: AvatarStorage,
        *,
        presign_expires_sec: int,
        max_avatar_bytes: int,
    ) -> None:
        self._uow = uow
        self._storage = storage
        self._presign_expires = presign_expires_sec
        self._max_avatar_bytes = max_avatar_bytes

    async def get(self, user_id: UUID) -> UserProfile:
        return to_profile(await self._user(user_id), self._storage)

    async def update(self, user_id: UUID, changes: ProfileChanges) -> UserProfile:
        user = await self._user(user_id)
        if changes.username is not UNSET:
            user.username = changes.username
        if changes.bio is not UNSET:
            user.bio = changes.bio
        await self._uow.flush()
        return to_profile(user, self._storage)

    def presign_avatar(self, user_id: UUID, content_type: str) -> AvatarUpload:
        key = avatar_key(user_id, content_type, token_hex(16))
        return AvatarUpload(
            object_key=key,
            upload_url=self._storage.presign_upload(
                key, content_type=content_type, expires_in=self._presign_expires
            ),
            public_url=self._storage.public_url(key),
            expires_in=self._presign_expires,
        )

    async def confirm_avatar(self, user_id: UUID, object_key: str) -> UserProfile:
        ensure_own_avatar_key(user_id, object_key)
        info = await self._storage.stat(object_key)
        if info is None:
            raise AvatarNotUploadedError()
        ensure_valid_upload(
            content_type=info.content_type,
            size_bytes=info.size_bytes,
            max_bytes=self._max_avatar_bytes,
        )

        user = await self._user(user_id)
        if user.avatar_key != object_key:
            self._orphan(user.avatar_key)
            user.avatar_key = object_key
        await self._uow.flush()
        return to_profile(user, self._storage)

    async def remove_avatar(self, user_id: UUID) -> UserProfile:
        user = await self._user(user_id)
        self._orphan(user.avatar_key)
        user.avatar_key = None
        await self._uow.flush()
        return to_profile(user, self._storage)

    def _orphan(self, key: str | None) -> None:
        # The file is deleted by the worker after commit: if this transaction rolls back,
        # the profile still points to an existing file.
        if key is not None:
            self._uow.outbox.add(Topic.STORAGE_OBJECT_ORPHANED, {"key": key})

    async def _user(self, user_id: UUID) -> User:
        user = await self._uow.users.get(user_id)
        if user is None:
            raise UserNotFoundError()
        return user
