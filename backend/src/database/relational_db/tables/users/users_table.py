from uuid import UUID, uuid4
from datetime import datetime, date
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, Integer, Uuid, String, Boolean, DateTime, Float, Date, false
from sqlalchemy.dialects.postgresql import BYTEA, ENUM
from sqlalchemy.ext.hybrid import hybrid_property

from domain.users import Gender
from ..table_base import Base
from ..mixins import TimestampMixin


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), default=uuid4, primary_key=True)
    
    # Credentials
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password_hash: Mapped[bytes] = mapped_column(BYTEA, nullable=False)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Profile info
    username: Mapped[str | None] = mapped_column(String, nullable=True)
    profile_pic_url: Mapped[str | None] = mapped_column(String, nullable=True)
    bio: Mapped[str | None] = mapped_column(String, nullable=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[Gender | None] = mapped_column(ENUM(Gender), nullable=True)
    language_code: Mapped[str | None] = mapped_column(
        String(2), ForeignKey('languages.code'), nullable=True
    )
    
    # Service
    # role: Mapped[Role] = mapped_column(Enum(Role), nullable=False, default=Role.GUEST)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=false())
    is_onboarded: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    banned: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
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
        from sqlalchemy import func, extract, case
        today = func.current_date()
        return case(
            (cls.birth_date.is_(None), None),
            else_=extract('year', func.age(today, cls.birth_date))
        )
