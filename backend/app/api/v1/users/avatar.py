from fastapi import APIRouter

from app.api.deps import CurrentUserDep
from app.api.v1.users.deps import ProfileServiceDep
from app.api.v1.users.schemas import (
    AvatarConfirmRequest,
    AvatarPresignRequest,
    AvatarPresignResponse,
    UserOut,
)

router = APIRouter()


@router.post(
    path="/presign",
    summary="Get a presigned URL to upload a new avatar directly to storage",
)
async def presign_avatar(
    payload: AvatarPresignRequest, user: CurrentUserDep, svc: ProfileServiceDep
) -> AvatarPresignResponse:
    return AvatarPresignResponse.from_domain(svc.presign_avatar(user.id, payload.content_type))


@router.post(
    path="/confirm",
    summary="Attach an uploaded file as the avatar",
    responses={409: {"description": "Nothing was uploaded to this key"}},
)
async def confirm_avatar(
    payload: AvatarConfirmRequest, user: CurrentUserDep, svc: ProfileServiceDep
) -> UserOut:
    return UserOut.from_domain(await svc.confirm_avatar(user.id, payload.object_key))


@router.delete(path="", summary="Remove the avatar")
async def delete_avatar(user: CurrentUserDep, svc: ProfileServiceDep) -> UserOut:
    return UserOut.from_domain(await svc.remove_avatar(user.id))
