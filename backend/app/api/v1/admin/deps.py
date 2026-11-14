from typing import Annotated

from fastapi import Depends

from app.api.deps import CurrentUserDep, StorageDep, UowDep
from app.service.admin import AdminUserService, StatsService


def _admin_users(uow: UowDep, storage: StorageDep, actor: CurrentUserDep) -> AdminUserService:
    # The permission itself is checked per endpoint with `require(...)`.
    return AdminUserService(uow, storage, actor)


def _stats(uow: UowDep) -> StatsService:
    return StatsService(uow)


AdminUserServiceDep = Annotated[AdminUserService, Depends(_admin_users)]
StatsServiceDep = Annotated[StatsService, Depends(_stats)]
