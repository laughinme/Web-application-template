from fastapi import APIRouter

from app.api.v1.users import avatar, profile

# The group's URL layout lives here; endpoint files only know their own paths.
router = APIRouter(tags=["Me"])
router.include_router(profile.router, prefix="/users/me")
router.include_router(avatar.router, prefix="/users/me/avatar")
