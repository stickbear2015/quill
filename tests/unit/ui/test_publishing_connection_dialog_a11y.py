from __future__ import annotations

from pathlib import Path


def _publishing_tools_source() -> str:
    return Path("quill/ui/publishing_tools.py").read_text(encoding="utf-8")


def _edit_dialog_source() -> str:
    source = _publishing_tools_source()
    start = source.index("class EditPublishingConnectionDialog")
    end = source.index("class PublishingConnectionsDialog")
    return source[start:end]


def _manager_dialog_source() -> str:
    source = _publishing_tools_source()
    start = source.index("class PublishingConnectionsDialog")
    return source[start:]


def test_edit_connection_controls_set_accessible_names() -> None:
    body = _edit_dialog_source()
    assert 'self.connection_label.SetName("Connection label")' in body
    assert 'self.provider.SetName("Provider")' in body
    assert 'self.site_url.SetName("Site URL")' in body
    assert 'self.auth_method.SetName("Sign-in method")' in body
    assert 'self.account_identifier.SetName("Sign-in name or email")' in body
    assert 'self.secret.SetName("Secret")' in body


def test_manager_dialog_names_the_connections_list() -> None:
    body = _manager_dialog_source()
    assert 'self.connection_list.SetName("Publishing connections")' in body


def test_publishing_dialogs_have_no_storage_jargon() -> None:
    source = _publishing_tools_source()
    for term in ("Credential Manager", "DPAPI", "encrypted fallback"):
        assert term not in source


def test_publishing_dialogs_use_modal_contract() -> None:
    source = _publishing_tools_source()
    assert "apply_modal_ids(" in source
    assert "show_modal_dialog(" in source
    assert ".ShowModal()" not in source
