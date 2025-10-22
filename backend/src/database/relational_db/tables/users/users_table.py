from uuid import UUID, uuid4
from datetime import datetime, date

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Uuid,
    case,
    extract,
    func,
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..mixins import TimestampMixin
from ..table_base import Base



class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), default=uuid4, primary_key=True
    )

    # Credentials
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Profile info
    username: Mapped[str | None] = mapped_column(String, nullable=True)
    profile_pic_url: Mapped[str | None] = mapped_column(String, nullable=True)
    bio: Mapped[str | None] = mapped_column(String, nullable=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    language_code: Mapped[str | None] = mapped_column(
        String(2), ForeignKey("languages.code"), nullable=True
    )

    # Service
    is_onboarded: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    banned: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    auth_version: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default="1"
    )

    roles: Mapped[list["Role"]] = relationship(  # pyright: ignore[reportUndefinedVariable]
        "Role",
        secondary="user_roles",
        back_populates="users",
        lazy="selectin",
    )

    @hybrid_property
    def age(self) -> int | None:
        if not self.birth_date:
            return None
        today = date.today()
        age = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
        return age

    @age.expression
    @classmethod
    def age_expr(cls):
        today = func.current_date()
        return case(
            (cls.birth_date.is_(None), None),
            else_=extract("year", func.age(today, cls.birth_date)),
        )

    __table_args__ = (
        # GIN trigram indexes for fast text search
        Index(
            "users_username_trgm",
            "username",
            postgresql_using="gin",
            postgresql_ops={"username": "gin_trgm_ops"},
        ),
        Index(
            "users_email_trgm",
            "email",
            postgresql_using="gin",
            postgresql_ops={"email": "gin_trgm_ops"},
        ),
    )

    @property
    def role_slugs(self) -> list[str]:
        return [role.slug for role in self.roles]

    @property
    def permission_slugs(self) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for role in self.roles:
            for permission in role.permissions:
                if permission.slug not in seen:
                    seen.add(permission.slug)
                    result.append(permission.slug)
        return result

    def has_roles(self, *slugs: str) -> bool:
        if not slugs:
            return True
        owned = set(self.role_slugs)
        return all(slug in owned for slug in slugs)

    def has_permissions(self, *slugs: str) -> bool:
        if not slugs:
            return True
        owned = set(self.permission_slugs)
        return all(slug in owned for slug in slugs)

    def bump_auth_version(self) -> None:
        self.auth_version = (self.auth_version or 0) + 1
