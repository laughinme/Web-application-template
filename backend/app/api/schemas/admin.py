from datetime import date, datetime
from typing import Self

from pydantic import Field

from app.api.schemas.base import RequestModel, ResponseModel
from app.domain.stats import DailyCount, UsersSummary
from app.domain.users import Role


class RoleUpdate(RequestModel):
    role: Role


class UsersSummaryOut(ResponseModel):
    generated_at: datetime
    total: int = Field(..., ge=0)
    onboarded: int = Field(..., ge=0)
    banned: int = Field(..., ge=0)
    registered_last_24h: int = Field(..., ge=0)

    @classmethod
    def from_domain(cls, summary: UsersSummary) -> Self:
        return cls.model_validate(summary)


class DailyCountOut(ResponseModel):
    day: date
    count: int

    @classmethod
    def from_domain(cls, row: DailyCount) -> Self:
        return cls.model_validate(row)
