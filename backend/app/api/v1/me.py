from fastapi import APIRouter

from app.api.deps import CurrentUserDep, ProfileServiceDep
from app.api.schemas.users import (
    AvatarConfirmRequest,
    AvatarPresignRequest,
    AvatarPresignResponse,
    ProfileUpdate,
    UserOut,
)

router = APIRouter(prefix="/users/me", tags=["Me"])


@router.get(path="", summary="Current user's profile")
async def get_me(user: CurrentUserDep, svc: ProfileServiceDep) -> UserOut:
    return UserOut.from_domain(await svc.get(user.id))


@router.patch(path="", summary="Update profile fields; omitted fields stay unchanged")
async def update_me(
    payload: ProfileUpdate, user: CurrentUserDep, svc: ProfileServiceDep
) -> UserOut:
    return UserOut.from_domain(await svc.update(user.id, payload.to_changes()))


@router.post(
    path="/avatar/presign",
    summary="Get a presigned URL to upload a new avatar directly to storage",
)
async def presign_avatar(
    payload: AvatarPresignRequest, user: CurrentUserDep, svc: ProfileServiceDep
) -> AvatarPresignResponse:
    return AvatarPresignResponse.from_domain(svc.presign_avatar(user.id, payload.content_type))


@router.post(
    path="/avatar/confirm",
    summary="Attach an uploaded file as the avatar",
    responses={409: {"description": "Nothing was uploaded to this key"}},
)
async def confirm_avatar(
    payload: AvatarConfirmRequest, user: CurrentUserDep, svc: ProfileServiceDep
) -> UserOut:
    return UserOut.from_domain(await svc.confirm_avatar(user.id, payload.object_key))


@router.delete(path="/avatar", summary="Remove the avatar")
async def delete_avatar(user: CurrentUserDep, svc: ProfileServiceDep) -> UserOut:
    return UserOut.from_domain(await svc.remove_avatar(user.id))
