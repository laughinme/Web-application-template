from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import require
from app.api.v1.admin.deps import UserStatsServiceDep
from app.api.v1.admin.schemas import DailyCountOut, UsersSummaryOut
from app.domain.users import Permission

router = APIRouter(dependencies=[Depends(require(Permission.STATS_READ))])


@router.get(path="/users", summary="User counters")
async def users_summary(svc: UserStatsServiceDep) -> UsersSummaryOut:
    return UsersSummaryOut.from_domain(await svc.users_summary())


@router.get(path="/registrations", summary="New registrations per day (UTC)")
async def registrations(
    svc: UserStatsServiceDep,
    days: Annotated[int, Query(ge=1, le=365, description="How many days back")] = 30,
) -> list[DailyCountOut]:
    return [DailyCountOut.from_domain(row) for row in await svc.registrations(days)]
