from app.core.security.tokens import AccessClaims
from app.db.uow import UnitOfWork
from app.domain.auth import SessionRevokedError
from app.domain.users import AccountBannedError, CurrentUser


async def resolve_current_user(uow: UnitOfWork, claims: AccessClaims) -> CurrentUser:
    """One primary-key lookup per request: catches bans, role changes and logout-everywhere."""
    user = await uow.users.get(claims.user_id)
    if user is None or user.auth_version != claims.auth_version:
        raise SessionRevokedError()
    if user.banned_at is not None:
        raise AccountBannedError()
    return CurrentUser(id=user.id, role=user.role, session_id=claims.session_id)
