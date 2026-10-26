from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

import pytest

from app.db.models import User
from app.domain.avatars import AvatarKeyInvalidError, AvatarNotUploadedError
from app.domain.events import Topic
from app.domain.users import ProfileChanges, Role
from app.infra.storage import ObjectInfo
from app.service.profile import ProfileService

# Services only talk to the UoW and to small protocols (app/service/ports.py),
# so a few in-memory fakes are enough to test their logic without Postgres or S3.


class FakeUsers:
    def __init__(self, *users: User) -> None:
        self.rows = {user.id: user for user in users}

    async def get(self, user_id: UUID, *, for_update: bool = False) -> User | None:
        return self.rows.get(user_id)


class FakeOutbox:
    def __init__(self) -> None:
        self.events: list[tuple[Topic, dict[str, Any]]] = []

    def add(self, topic: Topic, payload: dict[str, Any]) -> None:
        self.events.append((topic, payload))


class FakeUow:
    def __init__(self, *users: User) -> None:
        self.users = FakeUsers(*users)
        self.outbox = FakeOutbox()
        self.flushes = 0

    async def flush(self) -> None:
        self.flushes += 1


class FakeStorage:
    def __init__(self) -> None:
        self.objects: dict[str, ObjectInfo] = {}

    def public_url(self, key: str) -> str:
        return f"https://cdn.test/{key}"

    def presign_upload(self, key: str, *, content_type: str, expires_in: int) -> str:
        return f"https://upload.test/{key}"

    async def stat(self, key: str) -> ObjectInfo | None:
        return self.objects.get(key)


def make_user(**overrides: Any) -> User:
    now = datetime.now(UTC)
    values: dict[str, Any] = {
        "id": uuid4(),
        "email": "u@example.com",
        "password_hash": "x",
        "role": Role.MEMBER,
        "is_onboarded": False,
        "auth_version": 1,
        "created_at": now,
        "updated_at": now,
    }
    values.update(overrides)
    return User(**values)


def make_service(uow: FakeUow, storage: FakeStorage) -> ProfileService:
    return ProfileService(
        uow,  # type: ignore[arg-type]
        storage,
        presign_expires_sec=60,
        max_avatar_bytes=1024,
    )


async def test_patch_changes_only_sent_fields() -> None:
    user = make_user(username="old", bio="keep me")
    service = make_service(FakeUow(user), FakeStorage())

    profile = await service.update(user.id, ProfileChanges(username=None))

    assert profile.username is None
    assert profile.bio == "keep me"


async def test_confirm_avatar_replaces_and_orphans_the_old_file() -> None:
    user = make_user(avatar_key=None)
    uow, storage = FakeUow(user), FakeStorage()
    service = make_service(uow, storage)
    first = service.presign_avatar(user.id, "image/png").object_key
    second = service.presign_avatar(user.id, "image/png").object_key
    storage.objects[first] = ObjectInfo(size_bytes=10, content_type="image/png")
    storage.objects[second] = ObjectInfo(size_bytes=10, content_type="image/png")

    await service.confirm_avatar(user.id, first)
    profile = await service.confirm_avatar(user.id, second)

    assert profile.avatar_url == f"https://cdn.test/{second}"
    assert uow.outbox.events == [(Topic.STORAGE_OBJECT_ORPHANED, {"key": first})]


async def test_confirm_requires_an_uploaded_object() -> None:
    user = make_user()
    service = make_service(FakeUow(user), FakeStorage())
    key = service.presign_avatar(user.id, "image/png").object_key

    with pytest.raises(AvatarNotUploadedError):
        await service.confirm_avatar(user.id, key)


async def test_confirm_rejects_someone_elses_key() -> None:
    user = make_user()
    service = make_service(FakeUow(user), FakeStorage())

    with pytest.raises(AvatarKeyInvalidError):
        await service.confirm_avatar(user.id, f"avatars/{uuid4()}/x.png")
