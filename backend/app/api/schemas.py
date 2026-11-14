from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.core.errors import ErrorCode


class RequestModel(BaseModel):
    """Request bodies: unknown fields are an error, so client typos don't pass silently."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ResponseModel(BaseModel):
    """Response bodies are built from domain dataclasses, never from ORM objects."""

    model_config = ConfigDict(from_attributes=True)


class CursorPage[T](BaseModel):
    items: list[T]
    next_cursor: str | None = None


class Problem(BaseModel):
    """
    Every error response (RFC 7807). Published in OpenAPI so clients get `error_code`
    as a closed set of values and switch on it, never on `detail` text.
    """

    type: str = "about:blank"
    title: str
    status: int
    detail: str
    error_code: ErrorCode
    instance: str
    timestamp: datetime
    request_id: str | None = None
    details: Any = None
