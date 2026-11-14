from fastapi import APIRouter

from app.api.v1 import admin, auth, users

# Every endpoint group is a package that exposes one `router`; a new group is mounted here.
router = APIRouter(prefix="/v1")
router.include_router(auth.router)
router.include_router(users.router)
router.include_router(admin.router)
