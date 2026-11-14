from fastapi import APIRouter

from app.api.deps import CurrentUserDep
from app.api.v1.users.deps import ProfileServiceDep
from app.api.v1.users.schemas import ProfileUpdate, UserOut

router = APIRouter()


@router.get(path="", summary="Current user's profile")
async def get_me(user: CurrentUserDep, svc: ProfileServiceDep) -> UserOut:
    return UserOut.from_domain(await svc.get(user.id))


@router.patch(path="", summary="Update profile fields; omitted fields stay unchanged")
async def update_me(
    payload: ProfileUpdate, user: CurrentUserDep, svc: ProfileServiceDep
) -> UserOut:
    return UserOut.from_domain(await svc.update(user.id, payload.to_changes()))
