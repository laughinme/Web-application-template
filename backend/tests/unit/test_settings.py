from collections.abc import Callable

import pytest
from pydantic import SecretStr, ValidationError

from app.core.config import Settings


def test_production_refuses_development_secrets(make_settings: Callable[..., Settings]) -> None:
    with pytest.raises(ValidationError, match="Unsafe production settings"):
        make_settings(app_stage="prod", debug=False)


def test_production_accepts_real_secrets(make_settings: Callable[..., Settings]) -> None:
    settings = make_settings(
        app_stage="prod",
        debug=False,
        cookie_secure=True,
        csrf_hmac_key=SecretStr("a-long-random-value"),
        storage_secret_key=SecretStr("another-random-value"),
    )

    assert not settings.show_api_docs


def test_jwt_keys_are_required(make_settings: Callable[..., Settings]) -> None:
    with pytest.raises(ValidationError, match="JWT keys are required"):
        make_settings(jwt_private_key=None, jwt_public_key=None)


def test_cors_origins_are_split(make_settings: Callable[..., Settings]) -> None:
    settings = make_settings(cors_allow_origins="http://a.test, http://b.test,")

    assert settings.cors_origins == ["http://a.test", "http://b.test"]
