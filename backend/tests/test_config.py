import pytest
from pydantic import ValidationError

from hr_assistant_backend.core.config import Settings


def build_settings(**overrides: object) -> Settings:
    defaults = {
        "secret_key": "a" * 32,
        "cookie_samesite": "lax",
        "cookie_secure": False,
    }
    defaults.update(overrides)
    return Settings(**defaults)


def test_settings_reject_short_secret_key() -> None:
    with pytest.raises(ValidationError):
        build_settings(secret_key="short-secret")


def test_settings_normalize_cookie_samesite_to_lowercase() -> None:
    settings = build_settings(cookie_samesite="Strict")

    assert settings.cookie_samesite == "strict"


def test_settings_require_secure_cookie_for_none_samesite() -> None:
    with pytest.raises(ValidationError):
        build_settings(cookie_samesite="none", cookie_secure=False)


def test_settings_allow_secure_cookie_for_none_samesite() -> None:
    settings = build_settings(cookie_samesite="none", cookie_secure=True)

    assert settings.cookie_samesite == "none"
    assert settings.cookie_secure is True
