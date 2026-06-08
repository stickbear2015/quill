from __future__ import annotations

from pathlib import Path


def _publishing_tools_source() -> str:
    return Path("quill/ui/publishing_tools.py").read_text(encoding="utf-8")


def _connection_dialog_source() -> str:
    source = _publishing_tools_source()
    start = source.index("class PublishingConnectionDialog")
    return source[start:]


def test_publishing_connection_controls_set_accessible_names() -> None:
    body = _connection_dialog_source()
    assert 'self.provider.SetName("Provider")' in body
    assert 'self.site_url.SetName("Site URL")' in body
    assert 'self.username.SetName("Username")' in body
    assert 'self.app_password.SetName("Application password")' in body


def test_publishing_connection_dialog_has_no_storage_jargon() -> None:
    body = _connection_dialog_source()
    for term in ("Credential Manager", "DPAPI", "encrypted fallback"):
        assert term not in body


def test_publishing_connection_dialog_uses_modal_contract() -> None:
    body = _connection_dialog_source()
    assert "apply_modal_ids(" in body
    assert "show_modal_dialog(" in body
    assert ".ShowModal()" not in body
