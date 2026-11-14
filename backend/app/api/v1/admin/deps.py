from typing import Annotated

from fastapi import Depends

from app.api.deps import CurrentUserDep, StorageDep, UowDep
from app.service.moderation import ModerationService
from app.service.stats import UserStatsService


def _moderation(uow: UowDep, storage: StorageDep, actor: CurrentUserDep) -> ModerationService:
    # The permission itself is checked per endpoint with `require(...)`.
    return ModerationService(uow, storage, actor)


def _stats(uow: UowDep) -> UserStatsService:
    return UserStatsService(uow)


ModerationServiceDep = Annotated[ModerationService, Depends(_moderation)]
UserStatsServiceDep = Annotated[UserStatsService, Depends(_stats)]
