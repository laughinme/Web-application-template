from dataclasses import dataclass
from enum import StrEnum


class ClientKind(StrEnum):
    """
    `web` keeps the refresh token in an httpOnly cookie guarded by CSRF;
    `mobile` receives it in the response body.
    """

    WEB = "web"
    MOBILE = "mobile"


@dataclass(frozen=True, slots=True)
class IssuedTokens:
    access_token: str
    refresh_token: str
    csrf_token: str
    expires_in: int
