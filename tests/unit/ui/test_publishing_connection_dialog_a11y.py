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


def test_publishing_dialogs_keep_a_simple_label_then_control_flow() -> None:
    body = _edit_dialog_source()
    for helper_name in (
        "connection_label_hint",
        "provider_hint",
        "site_url_hint",
        "auth_hint",
        "account_identifier_hint",
        "secret_hint",
    ):
        assert helper_name not in body


def test_publishing_dialogs_keep_plain_language_status_copy() -> None:
    body = _edit_dialog_source()
    assert "Create or edit a publishing connection." in body
    assert "Save and verify this connection before publishing." in body


def test_publishing_dialog_labels_are_immediately_paired_with_controls() -> None:
    body = _edit_dialog_source()
    assert "wx.FlexGridSizer(0, 2, 8, 8)" in body
    assert "form.AddGrowableCol(1, 1)" in body
    assert 'self.connection_label_caption = wx.StaticText(panel, label="Connection name")' in body
    assert "self.connection_label = wx.TextCtrl(panel)" in body
    assert "add_row(self.connection_label_caption, self.connection_label)" in body
    assert 'self.provider_caption = wx.StaticText(panel, label="Publishing type")' in body
    assert "add_row(self.provider_caption, self.provider)" in body
    assert 'self.site_url_caption = wx.StaticText(panel, label="Site address")' in body
    assert "add_row(self.site_url_caption, self.site_url)" in body
    assert 'self.auth_method_caption = wx.StaticText(panel, label="Sign-in method")' in body
    assert "add_row(self.auth_method_caption, self.auth_method)" in body


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
