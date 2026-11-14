from typing import Annotated

from fastapi import Depends

from app.api.deps import SettingsDep, StorageDep, UowDep
from app.service.users import ProfileService


def _profile_service(uow: UowDep, storage: StorageDep, settings: SettingsDep) -> ProfileService:
    return ProfileService(
        uow,
        storage,
        presign_expires_sec=settings.storage_presign_expires_sec,
        max_avatar_bytes=settings.max_avatar_size_bytes,
    )


ProfileServiceDep = Annotated[ProfileService, Depends(_profile_service)]
