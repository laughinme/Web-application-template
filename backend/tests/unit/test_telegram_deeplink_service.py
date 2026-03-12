import hashlib
from types import SimpleNamespace
from uuid import uuid4

import pytest

from service.telegram.deeplink_service import TelegramDeepLinkService


class FakeTokenRow(SimpleNamespace):
    pass


class FakeTokensRepo:
    def __init__(self) -> None:
        self.rows: dict[str, FakeTokenRow] = {}

    async def create(self, *, user_id, token_hash, expires_at):
        row = FakeTokenRow(user_id=user_id, token_hash=token_hash, expires_at=expires_at, consumed_at=None)
        self.rows[token_hash] = row
        return row

    async def get_valid(self, token_hash):
        row = self.rows.get(token_hash)
        if row is None:
            return None
        if row.consumed_at is not None:
            return None
        return row

    async def consume(self, token):
        token.consumed_at = "consumed"


class FakeLinksRepo:
    def __init__(self) -> None:
        self.last_upsert = None

    async def upsert_link(self, **kwargs):
        self.last_upsert = kwargs
        return SimpleNamespace(**kwargs)

    async def get_by_chat_id(self, chat_id):
        return None

    async def deactivate(self, user_id):
        return None


class FakePreferencesRepo:
    def __init__(self) -> None:
        self.last_upsert = None

    async def get_for_user_event(self, *, user_id, event_type):
        return None

    async def upsert(self, **kwargs):
        self.last_upsert = kwargs
        return SimpleNamespace(**kwargs)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_and_consume_deeplink_token() -> None:
    user_id = uuid4()
    tokens_repo = FakeTokensRepo()
    links_repo = FakeLinksRepo()
    preferences_repo = FakePreferencesRepo()

    settings = SimpleNamespace(
        TELEGRAM_LINK_TOKEN_TTL_SEC=900,
        TELEGRAM_BOT_USERNAME="my_bot",
    )

    svc = TelegramDeepLinkService(
        settings=settings,
        uow=SimpleNamespace(),
        tokens_repo=tokens_repo,
        links_repo=links_repo,
        preferences_repo=preferences_repo,
    )

    response = await svc.create_connect_link(user_id)
    assert response.url.startswith("https://t.me/my_bot?start=")
    token_payload = response.url.split("start=", 1)[1]

    consumed_user_id = await svc.consume_link_token_and_bind(
        token_payload=token_payload,
        telegram_user_id=123,
        chat_id=456,
        username="tg",
        first_name="Test",
        last_name="User",
        language_code="en",
    )

    token_hash = hashlib.sha256(token_payload.encode("utf-8")).hexdigest()
    assert consumed_user_id == user_id
    assert tokens_repo.rows[token_hash].consumed_at is not None
    assert links_repo.last_upsert is not None
    assert preferences_repo.last_upsert is not None
