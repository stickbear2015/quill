from __future__ import annotations

import base64
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from quill.core.net import verified_ssl_context
from quill.core.paths import app_data_dir
from quill.core.publishing_providers import (
    SUPPORTED_PUBLISHING_PROVIDERS,
    WORDPRESS_PROVIDER_ID,
    default_content_format_for_provider,
)
from quill.core.storage import read_json, write_json_atomic
from quill.platform.windows.credential_manager import (
    credential_manager_available,
    delete_generic_credential,
    load_generic_credential,
    save_generic_credential,
)
from quill.platform.windows.dpapi import protect_secret, unprotect_secret

_PUBLISHING_CONNECTION_FILE = "publishing-connection.json"
_PUBLISHING_SECRET_FILE = "publishing-secret.json"
_PUBLISHING_CREDENTIAL_TARGET = "QUILL:publishing:app-password"


@dataclass(slots=True)
class PublishingConnectionSettings:
    provider: str = WORDPRESS_PROVIDER_ID
    site_url: str = ""
    username: str = ""
    content_format: str = "html"

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> PublishingConnectionSettings:
        provider = str(data.get("provider", WORDPRESS_PROVIDER_ID)).strip().lower()
        if provider not in SUPPORTED_PUBLISHING_PROVIDERS:
            provider = WORDPRESS_PROVIDER_ID
        site_url = str(data.get("site_url", "")).strip()
        username = str(data.get("username", "")).strip()
        content_format = str(
            data.get("content_format", default_content_format_for_provider(provider))
        ).strip().lower()
        if content_format not in {"html"}:
            content_format = default_content_format_for_provider(provider)
        return cls(
            provider=provider,
            site_url=site_url,
            username=username,
            content_format=content_format,
        )


def publishing_connection_path() -> Path:
    return app_data_dir() / _PUBLISHING_CONNECTION_FILE


def publishing_secret_path() -> Path:
    return app_data_dir() / _PUBLISHING_SECRET_FILE


def load_publishing_connection_settings() -> PublishingConnectionSettings:
    raw = read_json(publishing_connection_path(), default={})
    if not isinstance(raw, dict):
        return PublishingConnectionSettings()
    return PublishingConnectionSettings.from_dict(raw)


def save_publishing_connection_settings(settings: PublishingConnectionSettings) -> None:
    payload = asdict(settings)
    payload["provider"] = settings.provider.strip().lower() or WORDPRESS_PROVIDER_ID
    payload["site_url"] = settings.site_url.strip()
    payload["username"] = settings.username.strip()
    payload["content_format"] = (
        settings.content_format.strip().lower()
        or default_content_format_for_provider(payload["provider"])
    )
    write_json_atomic(publishing_connection_path(), payload)


def load_publishing_app_password() -> str:
    credential_secret = _load_app_password_from_credential_manager()
    if credential_secret:
        return credential_secret

    raw = read_json(publishing_secret_path(), default={})
    if not isinstance(raw, dict):
        return ""
    encrypted = str(raw.get("protected_secret", "")).strip()
    if not encrypted:
        return ""
    decrypted = unprotect_secret(encrypted)
    if not decrypted:
        return ""
    if _save_app_password_with_credential_manager(decrypted):
        path = publishing_secret_path()
        if path.exists():
            path.unlink()
    return decrypted


def save_publishing_app_password(app_password: str) -> None:
    secret = app_password.strip()
    path = publishing_secret_path()
    if not secret:
        _delete_app_password_from_credential_manager()
        if path.exists():
            path.unlink()
        return
    if _save_app_password_with_credential_manager(secret):
        if path.exists():
            path.unlink()
        return
    write_json_atomic(path, {"protected_secret": protect_secret(secret)})


def clear_publishing_app_password() -> bool:
    had_credential = bool(_load_app_password_from_credential_manager())
    _delete_app_password_from_credential_manager()

    path = publishing_secret_path()
    had_file = path.exists()
    if had_file:
        path.unlink(missing_ok=True)
    return had_credential or had_file


def verify_publishing_connection(
    settings: PublishingConnectionSettings,
    app_password: str,
    *,
    timeout_seconds: float = 8.0,
) -> tuple[bool, str]:
    provider = settings.provider.strip().lower()
    if provider != WORDPRESS_PROVIDER_ID:
        return False, "Only the WordPress publishing provider is supported right now."

    site_url = settings.site_url.strip()
    if not site_url:
        return False, "Enter a site URL before verifying the publishing connection."
    if not settings.username.strip():
        return False, "Enter a username before verifying the publishing connection."
    if not app_password.strip():
        return False, "Enter an application password before verifying the publishing connection."

    policy_error = _validate_endpoint_security(site_url)
    if policy_error:
        return False, policy_error

    endpoint = wordpress_users_me_endpoint(site_url)
    request = Request(
        endpoint,
        headers={
            "Accept": "application/json",
            "Authorization": _basic_auth_header(settings.username, app_password),
        },
        method="GET",
    )
    try:
        with urlopen(
            request,
            timeout=timeout_seconds,
            context=_context_for(endpoint),
        ) as response:
            payload = json.loads(response.read().decode("utf-8", errors="replace"))
    except HTTPError as exc:
        if exc.code == 401:
            return False, "Authentication failed. Check your username or application password."
        if exc.code == 403:
            return False, "Access denied. Your account cannot publish on this site."
        return False, f"WordPress returned HTTP {exc.code} while verifying the publishing connection."
    except URLError as exc:
        reason = getattr(exc, "reason", None)
        text = str(reason).strip() or "unknown network error"
        if "timed out" in text.lower():
            return False, "Connection timed out. Check the site URL and try again."
        return False, f"Could not reach the publishing site: {text}"
    except TimeoutError:
        return False, "Connection timed out. Check the site URL and try again."
    except json.JSONDecodeError:
        return False, "The publishing site returned an invalid response."

    if not isinstance(payload, dict):
        return False, "The publishing site returned an invalid response."
    return True, f"Publishing connection verified for {_display_host(site_url)}."


def wordpress_users_me_endpoint(site_url: str) -> str:
    return site_url.rstrip("/") + "/wp-json/wp/v2/users/me?context=edit"


def _display_host(site_url: str) -> str:
    return (urlparse(site_url).netloc or site_url.strip()).strip().rstrip("/")


def _basic_auth_header(username: str, app_password: str) -> str:
    token = f"{username.strip()}:{app_password.strip()}".encode("utf-8")
    return "Basic " + base64.b64encode(token).decode("ascii")


def _context_for(endpoint: str):
    if urlparse(endpoint).scheme == "https":
        return verified_ssl_context()
    return None


def _validate_endpoint_security(site_url: str) -> str | None:
    parsed = urlparse(site_url)
    scheme = parsed.scheme.lower()
    hostname = (parsed.hostname or "").lower()
    if scheme == "https":
        return None
    if scheme == "http" and _is_local_host(hostname):
        return None
    return (
        "Only HTTPS endpoints are allowed for remote publishing sites. "
        "HTTP is only supported for local loopback/private-network endpoints."
    )


def _is_local_host(hostname: str) -> bool:
    if not hostname:
        return False
    if hostname in {"localhost", "::1"}:
        return True
    if hostname.endswith(".localhost"):
        return True
    if hostname.startswith("127."):
        return True
    if hostname.startswith("10.") or hostname.startswith("192.168."):
        return True
    if hostname.startswith("172."):
        try:
            second_octet = int(hostname.split(".")[1])
        except (IndexError, ValueError):
            return False
        return 16 <= second_octet <= 31
    return False


def _load_app_password_from_credential_manager() -> str:
    if not credential_manager_available():
        return ""
    credential = load_generic_credential(_PUBLISHING_CREDENTIAL_TARGET)
    if credential is None:
        return ""
    return credential.secret.strip()


def _save_app_password_with_credential_manager(app_password: str) -> bool:
    secret = app_password.strip()
    if not secret or not credential_manager_available():
        return False
    try:
        save_generic_credential(_PUBLISHING_CREDENTIAL_TARGET, secret)
    except OSError:
        return False
    return True


def _delete_app_password_from_credential_manager() -> None:
    if not credential_manager_available():
        return
    try:
        delete_generic_credential(_PUBLISHING_CREDENTIAL_TARGET)
    except OSError:
        return
