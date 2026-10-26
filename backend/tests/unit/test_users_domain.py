from uuid import uuid4

import pytest

from app.domain.users import (
    AdminProtectedError,
    CurrentUser,
    Permission,
    Role,
    SelfModerationError,
    ensure_can_ban,
    ensure_can_change_role,
    normalize_email,
)


def _actor(role: Role = Role.ADMIN) -> CurrentUser:
    return CurrentUser(id=uuid4(), role=role, session_id=uuid4())


def test_admin_has_every_permission_member_has_none() -> None:
    assert all(_actor(Role.ADMIN).can(permission) for permission in Permission)
    assert not any(_actor(Role.MEMBER).can(permission) for permission in Permission)


def test_cannot_ban_yourself() -> None:
    actor = _actor()
    with pytest.raises(SelfModerationError):
        ensure_can_ban(actor, target_id=actor.id, target_role=Role.ADMIN)


def test_cannot_ban_another_admin() -> None:
    with pytest.raises(AdminProtectedError):
        ensure_can_ban(_actor(), target_id=uuid4(), target_role=Role.ADMIN)


def test_can_ban_a_member() -> None:
    ensure_can_ban(_actor(), target_id=uuid4(), target_role=Role.MEMBER)


def test_cannot_change_own_role() -> None:
    actor = _actor()
    with pytest.raises(SelfModerationError):
        ensure_can_change_role(actor, target_id=actor.id)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("User@Example.COM", "user@example.com"), ("  a@b.io ", "a@b.io")],
)
def test_normalize_email(raw: str, expected: str) -> None:
    assert normalize_email(raw) == expected
