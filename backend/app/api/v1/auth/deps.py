from datetime import timedelta
from typing import Annotated, Literal

from fastapi import Depends, Header

from app.api.deps import CodecDep, SettingsDep, UowDep
from app.domain.auth import ClientKind
from app.service.auth import AuthService


def _auth_service(uow: UowDep, codec: CodecDep, settings: SettingsDep) -> AuthService:
    return AuthService(uow, codec, refresh_ttl=timedelta(seconds=settings.refresh_ttl))


def _client_kind(
    x_client: Annotated[Literal["web", "mobile"], Header(alias="X-Client")] = "web",
) -> ClientKind:
    return ClientKind(x_client)


AuthServiceDep = Annotated[AuthService, Depends(_auth_service)]
ClientDep = Annotated[ClientKind, Depends(_client_kind)]
UserAgentDep = Annotated[str | None, Header(alias="User-Agent", include_in_schema=False)]
