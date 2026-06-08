from __future__ import annotations

import json
from pathlib import Path

import pytest

import quill.core.publishing as publishing
from quill.core.publishing import PublishingConnectionSettings
from quill.core.publishing_providers import (
    default_content_format_for_provider,
    publishing_provider_display_name,
    publishing_provider_help_text,
)


def test_publishing_connection_settings_round_trip(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    publishing.save_publishing_connection_settings(
        PublishingConnectionSettings(
            provider="wordpress",
            site_url="https://example.com",
            username="writer",
            content_format="html",
        )
    )
    loaded = publishing.load_publishing_connection_settings()
    assert loaded.provider == "wordpress"
    assert loaded.site_url == "https://example.com"
    assert loaded.username == "writer"
    assert loaded.content_format == "html"


def test_publishing_app_password_is_protected(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    monkeypatch.setattr(publishing, "_save_app_password_with_credential_manager", lambda *_a: False)
    monkeypatch.setattr(publishing, "_load_app_password_from_credential_manager", lambda: "")
    monkeypatch.setattr(publishing, "protect_secret", lambda secret: f"enc:{secret}")
    monkeypatch.setattr(publishing, "unprotect_secret", lambda secret: secret.removeprefix("enc:"))

    publishing.save_publishing_app_password("app-secret")

    assert publishing.load_publishing_app_password() == "app-secret"


def test_publishing_app_password_prefers_credential_manager(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    saved: dict[str, str] = {}

    def _save(secret: str) -> bool:
        saved["secret"] = secret
        return True

    monkeypatch.setattr(publishing, "_save_app_password_with_credential_manager", _save)
    monkeypatch.setattr(
        publishing,
        "_load_app_password_from_credential_manager",
        lambda: saved.get("secret", ""),
    )

    publishing.save_publishing_app_password("vault-secret")

    assert publishing.load_publishing_app_password() == "vault-secret"
    assert not publishing.publishing_secret_path().exists()


def test_clear_publishing_app_password_clears_both_stores(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setenv("QUILL_DATA_DIR", str(tmp_path))
    vault: dict[str, str] = {}
    monkeypatch.setattr(
        publishing,
        "_save_app_password_with_credential_manager",
        lambda secret: vault.update(secret=secret) or True,
    )
    monkeypatch.setattr(
        publishing,
        "_load_app_password_from_credential_manager",
        lambda: vault.get("secret", ""),
    )
    monkeypatch.setattr(
        publishing,
        "_delete_app_password_from_credential_manager",
        lambda: vault.clear(),
    )

    publishing.save_publishing_app_password("to-be-forgotten")

    assert publishing.clear_publishing_app_password() is True
    assert publishing.load_publishing_app_password() == ""
    assert not publishing.publishing_secret_path().exists()
    assert vault == {}
    assert publishing.clear_publishing_app_password() is False


class _FakeResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self) -> _FakeResponse:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


def test_verify_publishing_connection_requires_fields() -> None:
    ok, message = publishing.verify_publishing_connection(
        PublishingConnectionSettings(site_url="", username="writer"),
        "secret",
    )
    assert ok is False
    assert "site URL" in message


def test_verify_publishing_connection_rejects_non_https_remote_endpoint() -> None:
    ok, message = publishing.verify_publishing_connection(
        PublishingConnectionSettings(
            provider="wordpress",
            site_url="http://example.com",
            username="writer",
        ),
        "secret",
    )
    assert ok is False
    assert "Only HTTPS endpoints are allowed" in message


def test_verify_publishing_connection_allows_local_http(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        publishing,
        "urlopen",
        lambda *_a, **_k: _FakeResponse({"id": 7, "name": "Writer"}),
    )
    ok, message = publishing.verify_publishing_connection(
        PublishingConnectionSettings(
            provider="wordpress",
            site_url="http://localhost:8080",
            username="writer",
        ),
        "secret",
    )
    assert ok is True
    assert "Publishing connection verified for localhost:8080." == message


def test_verify_publishing_connection_reports_auth_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _Unauthorized(publishing.HTTPError):
        def __init__(self) -> None:
            super().__init__(
                url="https://example.com/wp-json/wp/v2/users/me?context=edit",
                code=401,
                msg="Unauthorized",
                hdrs=None,
                fp=None,
            )

    monkeypatch.setattr(publishing, "urlopen", lambda *_a, **_k: (_ for _ in ()).throw(_Unauthorized()))
    ok, message = publishing.verify_publishing_connection(
        PublishingConnectionSettings(
            provider="wordpress",
            site_url="https://example.com",
            username="writer",
        ),
        "bad-secret",
    )
    assert ok is False
    assert "Authentication failed" in message


def test_wordpress_endpoint_and_provider_metadata() -> None:
    assert (
        publishing.wordpress_users_me_endpoint("https://example.com/")
        == "https://example.com/wp-json/wp/v2/users/me?context=edit"
    )
    assert publishing_provider_display_name("wordpress") == "WordPress"
    assert "application password" in publishing_provider_help_text("wordpress")
    assert default_content_format_for_provider("wordpress") == "html"
