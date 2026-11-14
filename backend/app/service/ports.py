from dataclasses import dataclass
from typing import Protocol

# Ports: what the service layer needs from the outside world, written from its side.
# Adapters in `app/infra` implement them; services never import `app/infra` (import-linter
# checks it), and tests pass small in-memory fakes. Protocols need no inheritance: any class
# with matching methods fits, and mypy verifies that where the adapter is plugged in.
#
# Repositories are not abstracted here on purpose: they are our own code over our own
# database, covered by integration tests on real Postgres (see docs/backend/architecture.md).


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


class Notifier(Protocol):
    async def send(self, text: str) -> None: ...
