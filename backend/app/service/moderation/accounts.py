from app.core.security.passwords import hash_password
from app.db.models import User
from app.db.uow import UnitOfWork
from app.domain.users import Role, normalize_email


async def ensure_admin(uow: UnitOfWork, *, email: str, password: str) -> str:
    """Create an admin or promote an existing account (the first admin comes from the CLI)."""
    email = normalize_email(email)
    user = await uow.users.get_by_email(email)
    if user is not None:
        user.role = Role.ADMIN
        await uow.flush()
        return f"{email} promoted to admin"
    await uow.users.create(
        User(email=email, password_hash=await hash_password(password), role=Role.ADMIN)
    )
    return f"admin {email} created"
