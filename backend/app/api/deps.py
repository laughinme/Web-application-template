from collections.abc import AsyncIterator, Awaitable, Callable
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis

from app.core.config import Settings
from app.core.errors import ForbiddenError, RateLimitedError, UnauthorizedError
from app.core.security.tokens import TokenCodec
from app.db.database import Database
from app.db.uow import UnitOfWork
from app.domain.users import CurrentUser, Permission
from app.infra.rate_limit import RateLimiter
from app.infra.storage import ObjectStorage
from app.service.auth import resolve_current_user

# Dependencies shared by every endpoint group. A group's own ones (its services, headers)
# live in `api/v1/<group>/deps.py`. Long-lived objects are created once in the app factory
# and read from app.state here, so tests can build an app with their own settings and fakes.


def _settings(request: Request) -> Settings:
    settings: Settings = request.app.state.settings
    return settings


def _database(request: Request) -> Database:
    database: Database = request.app.state.db
    return database


def _redis(request: Request) -> Redis:
    redis: Redis = request.app.state.redis
    return redis


def _storage(request: Request) -> ObjectStorage:
    storage: ObjectStorage = request.app.state.storage
    return storage


def _codec(request: Request) -> TokenCodec:
    codec: TokenCodec = request.app.state.token_codec
    return codec


SettingsDep = Annotated[Settings, Depends(_settings)]
DatabaseDep = Annotated[Database, Depends(_database)]
RedisDep = Annotated[Redis, Depends(_redis)]
StorageDep = Annotated[ObjectStorage, Depends(_storage)]
CodecDep = Annotated[TokenCodec, Depends(_codec)]


async def _unit_of_work(db: DatabaseDep) -> AsyncIterator[UnitOfWork]:
    async with db.unit_of_work() as uow:
        yield uow


# scope="function": the commit runs before the response is sent, so a failed commit
# becomes a 500 instead of a 200 for data that was never saved.
UowDep = Annotated[UnitOfWork, Depends(_unit_of_work, scope="function")]

_bearer = HTTPBearer(auto_error=False, description="Access token from /auth/login or /auth/refresh")


async def current_user(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    codec: CodecDep,
    uow: UowDep,
) -> CurrentUser:
    if creds is None:
        raise UnauthorizedError()
    return await resolve_current_user(uow, codec.decode_access(creds.credentials))


CurrentUserDep = Annotated[CurrentUser, Depends(current_user)]


def require(permission: Permission) -> Callable[[CurrentUser], Awaitable[CurrentUser]]:
    """`Depends(require(Permission.X))` on an endpoint or a whole router."""

    async def dependency(user: CurrentUserDep) -> CurrentUser:
        if not user.can(permission):
            raise ForbiddenError()
        return user

    return dependency


def rate_limit(bucket: str) -> Callable[[Request, RedisDep, SettingsDep], Awaitable[None]]:
    """Per client IP. Behind a proxy run uvicorn with --proxy-headers so the IP is the real one."""

    async def dependency(request: Request, redis: RedisDep, settings: SettingsDep) -> None:
        if not settings.rate_limit_enabled:
            return
        limiter = RateLimiter(redis, limit=settings.auth_rate_limit_per_minute, window_sec=60)
        client = request.client.host if request.client else "unknown"
        if not await limiter.hit(f"{bucket}:{client}"):
            raise RateLimitedError()

    return dependency
