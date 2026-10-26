from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True, slots=True)
class UsersSummary:
    generated_at: datetime
    total: int
    onboarded: int
    banned: int
    registered_last_24h: int


@dataclass(frozen=True, slots=True)
class DailyCount:
    day: date
    count: int
