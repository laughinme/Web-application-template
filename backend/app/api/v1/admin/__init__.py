from fastapi import APIRouter

from app.api.v1.admin import stats, users

# The group's URL layout lives here; endpoint files only know their own paths.
router = APIRouter(prefix="/admin", tags=["Admin"])
router.include_router(users.router, prefix="/users")
router.include_router(stats.router, prefix="/stats")
