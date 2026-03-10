import asyncio
import os
import sys
import time
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
import pytest_asyncio
from alembic import command
from alembic.config import Config
from faker import Faker
from httpx import ASGITransport, AsyncClient
from redis.asyncio import Redis
from sqlalchemy import text

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
SECRETS_DIR = ROOT_DIR / "secrets"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

os.environ.setdefault("APP_STAGE", "dev")
os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://postgres:secret@localhost:5439/templatepg_test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6380/9")
os.environ.setdefault("JWT_PRIVATE_KEY_PATH", str(SECRETS_DIR / "jwt_private_key.pem"))
os.environ.setdefault("JWT_PUBLIC_KEY_PATH", str(SECRETS_DIR / "jwt_public_key.pem"))
os.environ.setdefault("SCHEDULER_ENABLED", "false")

from core.config import clear_settings_cache

clear_settings_cache()


async def _wait_for_redis(redis: Redis, attempts: int = 30, delay: float = 1.0) -> None:
    last_error = None
    for _ in range(attempts):
        try:
            await redis.ping()
            return
        except Exception as exc:
            last_error = exc
            await asyncio.sleep(delay)
    raise RuntimeError("Could not connect to redis for integration tests") from last_error


@pytest.fixture(scope="session")
def faker() -> Faker:
    fake = Faker()
    fake.seed_instance(262626)
    return fake


@pytest.fixture(scope="session")
def _migrate_database() -> None:
    config = Config(str(SRC_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(SRC_DIR / "migrations"))
    config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

    last_error = None
    for _ in range(30):
        try:
            command.upgrade(config, "head")
            return
        except Exception as exc:
            last_error = exc
            time.sleep(1)

    raise RuntimeError("Failed to apply migrations for integration tests") from last_error


@pytest_asyncio.fixture
async def redis_client() -> AsyncGenerator[Redis, None]:
    redis = Redis.from_url(os.environ["REDIS_URL"], decode_responses=True)
    await _wait_for_redis(redis)
    await redis.flushdb()
    yield redis
    await redis.flushdb()
    await redis.aclose()


@pytest_asyncio.fixture
async def _integration_state(
    _migrate_database: None,
    redis_client: Redis,
) -> AsyncGenerator[None, None]:
    from database.relational_db import dispose_engine, get_engine

    await dispose_engine()
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE user_roles, users RESTART IDENTITY CASCADE"))

    await redis_client.flushdb()
    yield
    await redis_client.flushdb()
    await dispose_engine()

@pytest_asyncio.fixture
async def app(
    redis_client: Redis,
):
    from main import create_app
    from database.redis import get_redis

    clear_settings_cache()
    application = create_app(
        enable_rate_limiter=False,
        check_db_on_startup=False,
        enable_scheduler=False,
    )

    def override_get_redis() -> Redis:
        return redis_client

    application.dependency_overrides[get_redis] = override_get_redis
    yield application
    application.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as api_client:
        yield api_client
