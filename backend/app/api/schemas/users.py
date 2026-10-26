from datetime import datetime
from typing import Literal, Self
from uuid import UUID

from pydantic import EmailStr, Field

from app.api.schemas.base import RequestModel, ResponseModel
from app.domain.avatars import AvatarUpload
from app.domain.common import UNSET
from app.domain.users import ProfileChanges, Role, UserProfile


class UserOut(ResponseModel):
    """User account representation."""

    id: UUID
    email: EmailStr
    username: str | None = Field(None, description="Display name")
    bio: str | None = Field(None, description="Short text about the user")
    avatar_key: str | None = Field(None, description="Storage key of the avatar object")
    avatar_url: str | None = Field(None, description="Public URL of the avatar")
    role: Role
    is_onboarded: bool
    banned: bool = Field(..., validation_alias="is_banned")
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, profile: UserProfile) -> Self:
        return cls.model_validate(profile)


class ProfileUpdate(RequestModel):
    """Only the fields present in the body change; `null` clears a field."""

    username: str | None = Field(None, min_length=1, max_length=64)
    bio: str | None = Field(None, max_length=500)

    def to_changes(self) -> ProfileChanges:
        sent = self.model_fields_set
        return ProfileChanges(
            username=self.username if "username" in sent else UNSET,
            bio=self.bio if "bio" in sent else UNSET,
        )


AvatarContentType = Literal["image/jpeg", "image/png", "image/webp"]


class AvatarPresignRequest(RequestModel):
    content_type: AvatarContentType
    filename: str | None = Field(
        None, max_length=255, description="Original file name, informational only"
    )


class AvatarPresignResponse(ResponseModel):
    object_key: str
    upload_url: str = Field(..., description="PUT the file here with the same Content-Type")
    public_url: str
    expires_in: int

    @classmethod
    def from_domain(cls, upload: AvatarUpload) -> Self:
        return cls.model_validate(upload)


class AvatarConfirmRequest(RequestModel):
    object_key: str = Field(..., min_length=1, max_length=512)
