from datetime import datetime

from sqlalchemy import Index, String, Text, false
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UuidPkMixin, pg_enum
from app.domain.users import Role


class User(UuidPkMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(320), unique=True)
    password_hash: Mapped[str] = mapped_column(Text)

    username: Mapped[str | None] = mapped_column(String(64))
    bio: Mapped[str | None] = mapped_column(String(500))
    avatar_key: Mapped[str | None] = mapped_column(String(512))

    role: Mapped[Role] = mapped_column(
        pg_enum(Role, "user_role"), default=Role.MEMBER, server_default=Role.MEMBER.value
    )
    is_onboarded: Mapped[bool] = mapped_column(default=False, server_default=false())
    banned_at: Mapped[datetime | None]
    # Bumped on ban and "log out everywhere": access tokens carry it and die on mismatch.
    auth_version: Mapped[int] = mapped_column(default=1, server_default="1")

    __table_args__ = (
        Index("ix_users_created_at_id", "created_at", "id"),
        Index(
            "ix_users_email_trgm",
            "email",
            postgresql_using="gin",
            postgresql_ops={"email": "gin_trgm_ops"},
        ),
        Index(
            "ix_users_username_trgm",
            "username",
            postgresql_using="gin",
            postgresql_ops={"username": "gin_trgm_ops"},
        ),
    )
