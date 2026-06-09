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
    assert 'self.connection_label.SetName("Connection name")' in body
    assert 'self.provider.SetName("Publishing type")' in body
    assert 'self.site_url.SetName("Site address")' in body
    assert 'self.auth_method.SetName("Sign-in method")' in body
    assert 'self.account_identifier.SetName("Username or email")' in body
    assert 'self.secret.SetName("Application password")' in body
    assert 'self.reveal_secret.SetName("Reveal application password")' in body


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
    assert "Enter the full address of the site you want to publish to." in body
    assert "Enter the username or email address you use to sign in to this site." in body
    assert "Choose the kind of site you want to publish to." in body
    assert "Enter the application password for this site." in body


def test_publishing_dialogs_do_not_rely_on_placeholder_examples_for_labels() -> None:
    body = _edit_dialog_source()
    assert ".SetHint(" not in body


def test_publishing_dialog_only_surfaces_working_wordpress_sign_in_method() -> None:
    source = _publishing_tools_source()
    assert "provider_auth_methods(provider_id)" in source
    assert "provider_supported_auth_methods(" not in source
    assert "provider_help_text" not in source


def test_publishing_dialogs_have_no_storage_jargon() -> None:
    source = _publishing_tools_source()
    for term in ("Credential Manager", "DPAPI", "encrypted fallback"):
        assert term not in source


def test_publishing_dialogs_use_modal_contract() -> None:
    source = _publishing_tools_source()
    assert "apply_modal_ids(" in source
    assert "show_modal_dialog(" in source
    assert ".ShowModal()" not in source
