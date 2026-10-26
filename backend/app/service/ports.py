from typing import Protocol

from app.infra.storage import ObjectInfo


class PublicUrls(Protocol):
    def public_url(self, key: str) -> str: ...


class AvatarStorage(PublicUrls, Protocol):
    def presign_upload(self, key: str, *, content_type: str, expires_in: int) -> str: ...

    async def stat(self, key: str) -> ObjectInfo | None: ...


class ObjectDeleter(Protocol):
    async def delete(self, key: str) -> None: ...
