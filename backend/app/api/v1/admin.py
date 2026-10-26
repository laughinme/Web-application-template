from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import StorageDep, UowDep, require
from app.api.schemas.admin import DailyCountOut, RoleUpdate, UsersSummaryOut
from app.api.schemas.base import CursorPage
from app.api.schemas.users import UserOut
from app.domain.users import CurrentUser, Permission, Role, UserQuery
from app.service.admin import AdminUserService, StatsService

router = APIRouter(prefix="/admin", tags=["Admin"])

UsersReader = Annotated[CurrentUser, Depends(require(Permission.USERS_READ))]
UsersBanner = Annotated[CurrentUser, Depends(require(Permission.USERS_BAN))]
RoleManager = Annotated[CurrentUser, Depends(require(Permission.USERS_MANAGE_ROLES))]
StatsReader = Annotated[CurrentUser, Depends(require(Permission.STATS_READ))]


@router.get(path="/users", summary="Search users (cursor pagination, newest first)")
async def list_users(
    admin: UsersReader,
    uow: UowDep,
    storage: StorageDep,
    search: Annotated[
        str | None, Query(max_length=100, description="Email or username part")
    ] = None,
    role: Role | None = None,
    banned: bool | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    cursor: Annotated[
        str | None, Query(max_length=200, description="next_cursor of the previous page")
    ] = None,
) -> CursorPage[UserOut]:
    query = UserQuery(search=search, role=role, banned=banned, limit=limit, cursor=cursor)
    page = await AdminUserService(uow, storage, admin).list_users(query)
    return CursorPage(
        items=[UserOut.from_domain(p) for p in page.items], next_cursor=page.next_cursor
    )


@router.post(path="/users/{user_id}/ban", summary="Ban a user and end all their sessions")
async def ban_user(user_id: UUID, admin: UsersBanner, uow: UowDep, storage: StorageDep) -> UserOut:
    return UserOut.from_domain(await AdminUserService(uow, storage, admin).ban(user_id))


@router.delete(path="/users/{user_id}/ban", summary="Lift a ban")
async def unban_user(
    user_id: UUID, admin: UsersBanner, uow: UowDep, storage: StorageDep
) -> UserOut:
    return UserOut.from_domain(await AdminUserService(uow, storage, admin).unban(user_id))


@router.put(path="/users/{user_id}/role", summary="Change a user's role")
async def set_role(
    user_id: UUID, payload: RoleUpdate, admin: RoleManager, uow: UowDep, storage: StorageDep
) -> UserOut:
    profile = await AdminUserService(uow, storage, admin).set_role(user_id, payload.role)
    return UserOut.from_domain(profile)


@router.get(path="/stats/users", summary="User counters")
async def users_summary(_: StatsReader, uow: UowDep) -> UsersSummaryOut:
    return UsersSummaryOut.from_domain(await StatsService(uow).users_summary())


@router.get(path="/stats/registrations", summary="New registrations per day (UTC)")
async def registrations(
    _: StatsReader,
    uow: UowDep,
    days: Annotated[int, Query(ge=1, le=365, description="How many days back")] = 30,
) -> list[DailyCountOut]:
    return [DailyCountOut.from_domain(row) for row in await StatsService(uow).registrations(days)]
