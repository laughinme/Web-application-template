from fastapi import Response

from app.api.v1.auth.cookies import set_auth_cookies
from app.api.v1.auth.schemas import TokenPair
from app.core.config import Settings
from app.domain.auth import ClientKind, IssuedTokens


def token_pair(
    response: Response, tokens: IssuedTokens, client: ClientKind, settings: Settings
) -> TokenPair:
    """Web clients get the refresh token as a cookie, mobile clients in the body."""
    if client is ClientKind.WEB:
        set_auth_cookies(response, tokens, settings)
        return TokenPair(access_token=tokens.access_token, expires_in=tokens.expires_in)
    return TokenPair(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        expires_in=tokens.expires_in,
    )
