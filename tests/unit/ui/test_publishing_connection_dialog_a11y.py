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
    assert 'self.connection_label.SetName("Publishing connection label")' in body
    assert 'self.provider.SetName("Publishing provider")' in body
    assert 'self.site_url.SetName("Publishing site URL")' in body
    assert 'self.auth_method.SetName("Publishing sign-in method")' in body
    assert 'self.account_identifier.SetName("Publishing sign-in name or email")' in body
    assert 'self.secret.SetName("Publishing secret")' in body
    assert 'self.reveal_secret.SetName("Reveal publishing secret")' in body
    assert 'self.connection_label.SetHint("Example: My blog or Team site")' in body
    assert 'self.site_url.SetHint("Example: https://example.com")' in body
    assert 'self.account_identifier.SetHint("Example: your username or email address")' in body


def test_manager_dialog_names_the_connections_list() -> None:
    body = _manager_dialog_source()
    assert 'self.connection_list.SetName("Saved publishing connections")' in body
    assert 'self.summary.SetName("Selected publishing connection details")' in body


def test_publishing_dialogs_set_initial_focus_and_stable_secret_tab_order() -> None:
    source = _publishing_tools_source()
    assert "self.connection_label.SetFocus()" in source
    assert "self.connection_list.SetFocus()" in source
    assert "self.reveal_secret.MoveAfterInTabOrder(self.secret)" in source


def test_publishing_dialogs_explain_field_purpose_in_plain_language() -> None:
    body = _edit_dialog_source()
    assert "Optional. Give this saved connection a short name" in body
    assert "Enter the full site address for the site you want to publish to." in body
    assert "Enter the username or email address used with this sign-in method." in body
    assert "Provider details:" in body
    assert "Sign-in method details:" in body


def test_publishing_dialogs_have_no_storage_jargon() -> None:
    source = _publishing_tools_source()
    for term in ("Credential Manager", "DPAPI", "encrypted fallback"):
        assert term not in source


def test_publishing_dialogs_use_modal_contract() -> None:
    source = _publishing_tools_source()
    assert "apply_modal_ids(" in source
    assert "show_modal_dialog(" in source
    assert ".ShowModal()" not in source
