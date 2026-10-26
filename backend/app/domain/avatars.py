from collections.abc import Mapping
from dataclasses import dataclass
from uuid import UUID

from app.core.errors import DomainError, ErrorCode

AVATAR_EXTENSIONS: Mapping[str, str] = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


@dataclass(frozen=True, slots=True)
class AvatarUpload:
    object_key: str
    upload_url: str
    public_url: str
    expires_in: int


class AvatarKeyInvalidError(DomainError):
    error_code = ErrorCode.AVATAR_KEY_INVALID
    default_detail = "This object key does not belong to your avatar uploads"


class AvatarNotUploadedError(DomainError):
    status_code = 409
    error_code = ErrorCode.AVATAR_NOT_UPLOADED
    default_detail = "Upload the file to the presigned URL first"


class AvatarTypeUnsupportedError(DomainError):
    status_code = 415
    error_code = ErrorCode.AVATAR_TYPE_UNSUPPORTED
    default_detail = "Avatar must be JPEG, PNG or WebP"


class AvatarTooLargeError(DomainError):
    status_code = 413
    error_code = ErrorCode.AVATAR_TOO_LARGE
    default_detail = "Avatar file is too large"


def avatar_prefix(user_id: UUID) -> str:
    return f"avatars/{user_id}/"


def avatar_key(user_id: UUID, content_type: str, token: str) -> str:
    try:
        extension = AVATAR_EXTENSIONS[content_type]
    except KeyError as exc:
        raise AvatarTypeUnsupportedError() from exc
    return f"{avatar_prefix(user_id)}{token}{extension}"


def ensure_own_avatar_key(user_id: UUID, key: str) -> None:
    if not key.startswith(avatar_prefix(user_id)) or ".." in key:
        raise AvatarKeyInvalidError()


def ensure_valid_upload(*, content_type: str | None, size_bytes: int, max_bytes: int) -> None:
    if content_type not in AVATAR_EXTENSIONS:
        raise AvatarTypeUnsupportedError()
    if size_bytes > max_bytes:
        raise AvatarTooLargeError(f"Avatar must be at most {max_bytes // (1024 * 1024)} MB")
