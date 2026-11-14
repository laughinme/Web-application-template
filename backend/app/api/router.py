from fastapi import APIRouter

from app.api import system, v1

api_router = APIRouter(prefix="/api")
api_router.include_router(system.router)
api_router.include_router(v1.router)
