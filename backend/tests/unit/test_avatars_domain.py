from uuid import uuid4

import pytest

from app.domain.avatars import (
    AvatarKeyInvalidError,
    AvatarTooLargeError,
    AvatarTypeUnsupportedError,
    avatar_key,
    ensure_own_avatar_key,
    ensure_valid_upload,
)

MB = 1024 * 1024


def test_avatar_key_lives_under_the_user_prefix() -> None:
    user_id = uuid4()

    key = avatar_key(user_id, "image/png", "abc")

    assert key == f"avatars/{user_id}/abc.png"
    ensure_own_avatar_key(user_id, key)


def test_avatar_key_rejects_unknown_type() -> None:
    with pytest.raises(AvatarTypeUnsupportedError):
        avatar_key(uuid4(), "image/gif", "abc")


@pytest.mark.parametrize("key", ["avatars/{other}/a.png", "avatars/{me}/../{other}/a.png", "a.png"])
def test_foreign_keys_are_rejected(key: str) -> None:
    me, other = uuid4(), uuid4()

    with pytest.raises(AvatarKeyInvalidError):
        ensure_own_avatar_key(me, key.format(me=me, other=other))


def test_upload_checks_type_and_size() -> None:
    ensure_valid_upload(content_type="image/webp", size_bytes=MB, max_bytes=5 * MB)
    with pytest.raises(AvatarTypeUnsupportedError):
        ensure_valid_upload(content_type="text/html", size_bytes=1, max_bytes=5 * MB)
    with pytest.raises(AvatarTooLargeError):
        ensure_valid_upload(content_type="image/png", size_bytes=6 * MB, max_bytes=5 * MB)
