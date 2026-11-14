from uuid import UUID

from app.domain.users.errors import AdminProtectedError, SelfModerationError
from app.domain.users.models import CurrentUser, Role


def normalize_email(email: str) -> str:
    return email.strip().lower()


def ensure_can_ban(actor: CurrentUser, *, target_id: UUID, target_role: Role) -> None:
    if actor.id == target_id:
        raise SelfModerationError()
    if target_role is Role.ADMIN:
        raise AdminProtectedError()


def ensure_can_change_role(actor: CurrentUser, *, target_id: UUID) -> None:
    # Prevents the last admin from locking everyone out by demoting themselves.
    if actor.id == target_id:
        raise SelfModerationError()
