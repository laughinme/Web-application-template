from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import require
from app.api.schemas import CursorPage
from app.api.v1.admin.deps import ModerationServiceDep
from app.api.v1.admin.schemas import RoleUpdate
from app.api.v1.users.schemas import UserOut
from app.domain.users import Permission, Role, UserQuery

router = APIRouter()


@router.get(
    path="",
    summary="Search users (cursor pagination, newest first)",
    dependencies=[Depends(require(Permission.USERS_READ))],
)
async def list_users(
    svc: ModerationServiceDep,
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
    page = await svc.list_users(query)
    return CursorPage(
        items=[UserOut.from_domain(p) for p in page.items], next_cursor=page.next_cursor
    )


@router.post(
    path="/{user_id}/ban",
    summary="Ban a user and end all their sessions",
    dependencies=[Depends(require(Permission.USERS_BAN))],
)
async def ban_user(user_id: UUID, svc: ModerationServiceDep) -> UserOut:
    return UserOut.from_domain(await svc.ban(user_id))


@router.delete(
    path="/{user_id}/ban",
    summary="Lift a ban",
    dependencies=[Depends(require(Permission.USERS_BAN))],
)
async def unban_user(user_id: UUID, svc: ModerationServiceDep) -> UserOut:
    return UserOut.from_domain(await svc.unban(user_id))


@router.put(
    path="/{user_id}/role",
    summary="Change a user's role",
    dependencies=[Depends(require(Permission.USERS_MANAGE_ROLES))],
)
async def set_role(user_id: UUID, payload: RoleUpdate, svc: ModerationServiceDep) -> UserOut:
    return UserOut.from_domain(await svc.set_role(user_id, payload.role))
