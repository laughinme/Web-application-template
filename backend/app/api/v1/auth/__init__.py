from fastapi import APIRouter

from app.api.v1.auth import credentials, session

router = APIRouter(prefix="/auth", tags=["Auth"])
router.include_router(credentials.router)
router.include_router(session.router)
