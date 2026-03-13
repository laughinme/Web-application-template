from fastapi import APIRouter


def get_me_router() -> APIRouter:
    from .profile import router as profile_router
    from .avatar import router as avatar_router
    from .notifications import router as notifications_router
    
    router = APIRouter()
    
    router.include_router(profile_router)
    router.include_router(avatar_router)
    router.include_router(notifications_router)
    
    return router
