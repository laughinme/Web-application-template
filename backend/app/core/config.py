from functools import lru_cache
from pathlib import Path
from typing import Literal, Self

from pydantic import SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]

DEV_CSRF_KEY = "change-me"
DEV_STORAGE_SECRET = "rustfsadmin"  # noqa: S105 - public RustFS default, refused in prod


class Settings(BaseSettings):
    """
    Application settings. Read once at startup from the environment and `backend/.env`,
    then passed down explicitly: nothing in the app calls `Settings()` on import.
    """

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    # Stage and diagnostics
    app_stage: Literal["dev", "test", "prod"] = "dev"
    debug: bool = False
    log_level: str = "INFO"
    log_json: bool = False
    sql_echo: bool = False
    api_docs_enabled: bool | None = None

    # HTTP
    site_url: str = "http://localhost"
    cors_allow_origins: str = ""
    rate_limit_enabled: bool = True
    auth_rate_limit_per_minute: int = 10

    # Postgres and Redis
    database_url: str
    db_pool_size: int = 10
    db_max_overflow: int = 10
    redis_url: str

    # Auth
    jwt_private_key: SecretStr | None = None
    jwt_public_key: str | None = None
    jwt_private_key_path: Path | None = None
    jwt_public_key_path: Path | None = None
    jwt_algo: str = "RS256"
    access_ttl: int = 15 * 60
    refresh_ttl: int = 30 * 24 * 60 * 60
    csrf_hmac_key: SecretStr = SecretStr(DEV_CSRF_KEY)

    # Cookies
    cookie_secure: bool = False
    cookie_samesite: Literal["lax", "strict", "none"] = "lax"
    cookie_domain: str | None = None

    # S3-compatible object storage (RustFS locally; AWS S3, R2, etc. in prod)
    storage_endpoint_internal: str = "http://s3:9000"
    storage_endpoint_public: str = "http://localhost"
    storage_region: str = "us-east-1"
    storage_access_key: str = "rustfsadmin"
    storage_secret_key: SecretStr = SecretStr(DEV_STORAGE_SECRET)
    storage_public_bucket: str = "media-public"
    storage_presign_expires_sec: int = 600
    storage_use_path_style: bool = True
    storage_auto_create_buckets: bool = False
    max_avatar_size_mb: int = 5

    # Notifications (delivered by the worker through the outbox)
    notifications_provider: Literal["log", "telegram"] = "log"
    telegram_bot_token: SecretStr = SecretStr("")
    telegram_chat_id: str = ""

    # Background worker
    outbox_batch_size: int = 20
    outbox_poll_interval_sec: float = 1.0
    outbox_max_attempts: int = 8

    @property
    def show_api_docs(self) -> bool:
        if self.api_docs_enabled is not None:
            return self.api_docs_enabled
        return self.app_stage != "prod"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allow_origins.split(",") if origin.strip()]

    @property
    def max_avatar_size_bytes(self) -> int:
        return self.max_avatar_size_mb * 1024 * 1024

    @field_validator("cookie_samesite", mode="before")
    @classmethod
    def _normalize_samesite(cls, value: object) -> object:
        return value.strip().lower() if isinstance(value, str) else value

    @field_validator("storage_endpoint_internal", "storage_endpoint_public")
    @classmethod
    def _strip_trailing_slash(cls, value: str) -> str:
        return value.rstrip("/")

    @model_validator(mode="after")
    def _load_jwt_keys(self) -> Self:
        if self.jwt_private_key is None and self.jwt_private_key_path is not None:
            self.jwt_private_key = SecretStr(_resolve(self.jwt_private_key_path).read_text())
        if self.jwt_public_key is None and self.jwt_public_key_path is not None:
            self.jwt_public_key = _resolve(self.jwt_public_key_path).read_text()
        if self.jwt_private_key is None or self.jwt_public_key is None:
            raise ValueError("JWT keys are required: set JWT_PRIVATE_KEY/JWT_PUBLIC_KEY or *_PATH")
        return self

    @model_validator(mode="after")
    def _refuse_unsafe_production(self) -> Self:
        if self.app_stage != "prod":
            return self

        problems = []
        if self.csrf_hmac_key.get_secret_value() == DEV_CSRF_KEY:
            problems.append("CSRF_HMAC_KEY still has the development value")
        if self.storage_secret_key.get_secret_value() == DEV_STORAGE_SECRET:
            problems.append("STORAGE_SECRET_KEY still has the development value")
        if not self.cookie_secure:
            problems.append("COOKIE_SECURE must be true")
        if self.debug:
            problems.append("DEBUG must be false")
        if problems:
            raise ValueError("Unsafe production settings: " + "; ".join(problems))
        return self


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else BASE_DIR / path


class MigrationSettings(BaseSettings):
    """Alembic needs only the database URL, not JWT keys and the rest of the app config."""

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    database_url: str


@lru_cache
def get_settings() -> Settings:
    """Entrypoints only (app factory, worker, CLI, alembic); everything else receives settings."""
    return Settings()
