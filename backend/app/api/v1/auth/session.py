from contextlib import suppress
from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Header, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.deps import CurrentUserDep, SettingsDep, rate_limit
from app.api.v1.auth.cookies import REFRESH_COOKIE, clear_auth_cookies, clearing_headers
from app.api.v1.auth.deps import AuthServiceDep
from app.api.v1.auth.schemas import TokenPair
from app.api.v1.auth.tokens import token_pair
from app.core.errors import InvalidTokenError, UnauthorizedError
from app.domain.auth import ClientKind

router = APIRouter()

_refresh_bearer = HTTPBearer(
    auto_error=False, description="Mobile clients send the refresh token as Bearer"
)
RefreshBearerDep = Annotated[HTTPAuthorizationCredentials | None, Depends(_refresh_bearer)]
RefreshCookieDep = Annotated[str | None, Cookie(alias=REFRESH_COOKIE, include_in_schema=False)]


@router.post(
    path="/refresh",
    summary="Rotate the refresh token and get a new access token",
    dependencies=[Depends(rate_limit("refresh"))],
)
async def refresh(
    response: Response,
    svc: AuthServiceDep,
    settings: SettingsDep,
    bearer: RefreshBearerDep,
    refresh_cookie: RefreshCookieDep = None,
    csrf_token: Annotated[
        str | None, Header(alias="X-CSRF-Token", description="Browsers only: the csrf_token cookie")
    ] = None,
) -> TokenPair:
    if refresh_cookie:
        try:
            tokens = await svc.refresh(refresh_cookie, csrf_token=csrf_token)
        except UnauthorizedError as exc:
            exc.headers.extend(clearing_headers(settings))
            raise
        return token_pair(response, tokens, ClientKind.WEB, settings)

    if bearer is None:
        raise UnauthorizedError("Refresh token is missing")
    tokens = await svc.refresh(bearer.credentials, csrf_token=None)
    return token_pair(response, tokens, ClientKind.MOBILE, settings)


@router.post(
    path="/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="End the current session (idempotent)",
)
async def logout(
    response: Response,
    svc: AuthServiceDep,
    settings: SettingsDep,
    bearer: RefreshBearerDep,
    refresh_cookie: RefreshCookieDep = None,
) -> None:
    raw_token = refresh_cookie or (bearer.credentials if bearer else None)
    if raw_token:
        # Not a refresh token (e.g. a web client's access token): nothing to revoke.
        with suppress(InvalidTokenError):
            await svc.logout(raw_token)
    clear_auth_cookies(response, settings)


@router.post(
    path="/logout-all",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="End every session of the current user and invalidate issued access tokens",
)
async def logout_all(
    user: CurrentUserDep,
    response: Response,
    svc: AuthServiceDep,
    settings: SettingsDep,
) -> None:
    await svc.logout_everywhere(user.id)
    clear_auth_cookies(response, settings)
