from dataclasses import dataclass
from typing import Protocol

# Ports: what the application needs from the outside world, written from its side.
# Adapters in app/infra implement them; services import only this package, never app/infra,
# and tests pass small in-memory fakes. A Protocol needs no inheritance: any class with these
# methods fits, and mypy checks it where the adapter is plugged in (app/api/deps.py, worker).


@dataclass(frozen=True, slots=True)
class ObjectInfo:
    size_bytes: int
    content_type: str | None


class PublicUrls(Protocol):
    def public_url(self, key: str) -> str: ...


class AvatarStorage(PublicUrls, Protocol):
    def presign_upload(self, key: str, *, content_type: str, expires_in: int) -> str: ...

    async def stat(self, key: str) -> ObjectInfo | None: ...


class ObjectDeleter(Protocol):
    async def delete(self, key: str) -> None: ...
