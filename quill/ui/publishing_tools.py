from __future__ import annotations

from quill.core.publishing import (
    PublishingConnectionProfile,
    load_publishing_connections,
    load_publishing_secret,
    remove_publishing_connection,
    save_publishing_secret,
    set_current_publishing_connection,
    upsert_publishing_connection,
    verify_publishing_connection,
)
from quill.core.publishing_providers import (
    auth_method_definition,
    provider_auth_methods,
    publishing_auth_method_name,
    publishing_provider_display_name,
)
from quill.ui.dialog_contract import apply_modal_ids, show_modal_dialog


class EditPublishingConnectionDialog:
    _PROVIDER_CHOICES: tuple[tuple[str, str], ...] = (("wordpress", "WordPress"),)

    def __init__(self, parent: object, profile: PublishingConnectionProfile | None = None) -> None:
        import wx

        self._wx = wx
        self.dialog = wx.Dialog(
            parent,
            title="Edit Publishing Connection",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.dialog.SetSize((760, 560))

        self._profile = profile or PublishingConnectionProfile()
        self._secret = load_publishing_secret(self._profile.id) if self._profile.id else ""
        self.last_verification_ok: bool | None = None
        self.last_verification_message: str = "Not checked"

        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(
            wx.StaticText(
                self.dialog,
                label=(
                    "Create or edit a publishing connection. Quill stays generic until you "
                    "choose a provider, then shows the sign-in options known for that provider."
                ),
            ),
            0,
            wx.EXPAND | wx.ALL,
            8,
        )

        panel = wx.Panel(self.dialog)
        panel_sizer = wx.BoxSizer(wx.VERTICAL)
        form = wx.FlexGridSizer(0, 2, 8, 8)
        form.AddGrowableCol(1, 1)

        def add_row(label: object, control: object) -> None:
            form.Add(label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 8)
            form.Add(control, 1, wx.EXPAND | wx.RIGHT, 8)

        self.connection_label_caption = wx.StaticText(panel, label="Connection name")
        self.connection_label = wx.TextCtrl(panel)
        self.connection_label.SetValue(self._profile.label)
        self.connection_label.SetName("Connection name")
        add_row(self.connection_label_caption, self.connection_label)

        self.provider_caption = wx.StaticText(panel, label="Publishing type")
        self.provider = wx.Choice(
            panel, choices=[label for _value, label in self._PROVIDER_CHOICES]
        )
        self.provider.SetName("Publishing type")
        self.provider.SetSelection(self._provider_choice_index(self._profile.provider_id))
        add_row(self.provider_caption, self.provider)

        self.site_url_caption = wx.StaticText(panel, label="Site address")
        self.site_url = wx.TextCtrl(panel)
        self.site_url.SetValue(self._profile.site_url)
        self.site_url.SetName("Site address")
        add_row(self.site_url_caption, self.site_url)

        self.auth_method_caption = wx.StaticText(panel, label="Sign-in method")
        self.auth_method = wx.Choice(panel)
        self.auth_method.SetName("Sign-in method")
        add_row(self.auth_method_caption, self.auth_method)

        self.identifier_label = wx.StaticText(panel, label="Username or email")
        self.account_identifier = wx.TextCtrl(panel)
        self.account_identifier.SetValue(self._profile.account_identifier)
        self.account_identifier.SetName("Username or email")
        form.Add(self.identifier_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 8)
        form.Add(self.account_identifier, 1, wx.EXPAND | wx.RIGHT, 8)

        self.secret_label = wx.StaticText(panel, label="Application password")
        self.secret_row = wx.BoxSizer(wx.HORIZONTAL)
        self.secret = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        self.secret.SetValue(self._secret)
        self.secret.SetName("Application password")
        self.secret_row.Add(self.secret, 1, wx.EXPAND | wx.RIGHT, 8)
        self.reveal_secret = wx.Button(panel, label="Reveal")
        self.reveal_secret.SetName("Reveal application password")
        self.secret_row.Add(self.reveal_secret, 0)
        form.Add(self.secret_label, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 8)
        form.Add(self.secret_row, 1, wx.EXPAND | wx.RIGHT, 8)

        panel_sizer.Add(form, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, 8)

        self.verify_button = wx.Button(panel, label="Verify Connection")
        panel_sizer.Add(self.verify_button, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        self.connection_status = wx.StaticText(
            panel, label="Save and verify this connection before publishing."
        )
        panel_sizer.Add(self.connection_status, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        panel.SetSizer(panel_sizer)
        root.Add(panel, 1, wx.EXPAND | wx.ALL, 8)

        buttons = self.dialog.CreateButtonSizer(wx.OK | wx.CANCEL)
        if buttons is not None:
            root.Add(buttons, 0, wx.EXPAND | wx.ALL, 8)
        self.dialog.SetSizerAndFit(root)
        apply_modal_ids(self.dialog, affirmative_id=wx.ID_OK, escape_id=wx.ID_CANCEL)
        self.provider.Bind(wx.EVT_CHOICE, self._on_provider_changed)
        self.auth_method.Bind(wx.EVT_CHOICE, self._on_auth_method_changed)
        self.verify_button.Bind(wx.EVT_BUTTON, self._on_verify_connection)
        self.reveal_secret.Bind(wx.EVT_BUTTON, self._on_toggle_secret_reveal)
        self._secret_revealed = False
        self._on_provider_changed(None)
        self.reveal_secret.MoveAfterInTabOrder(self.secret)
        self.connection_label.SetFocus()

    def _provider_choice_index(self, provider_id: str) -> int:
        normalized = provider_id.strip().lower()
        for index, (value, _label) in enumerate(self._PROVIDER_CHOICES):
            if value == normalized:
                return index
        return 0

    def _provider_value(self) -> str:
        selection = self.provider.GetSelection()
        if selection < 0 or selection >= len(self._PROVIDER_CHOICES):
            return self._PROVIDER_CHOICES[0][0]
        return self._PROVIDER_CHOICES[selection][0]

    def _auth_method_value(self) -> str:
        selection = self.auth_method.GetSelection()
        methods = provider_auth_methods(self._provider_value())
        if selection < 0 or selection >= len(methods):
            return methods[0]
        return methods[selection]

    def _current_profile(self) -> PublishingConnectionProfile:
        return PublishingConnectionProfile(
            id=self._profile.id or "",
            label=self.connection_label.GetValue().strip(),
            provider_id=self._provider_value(),
            site_url=self.site_url.GetValue().strip(),
            auth_method=self._auth_method_value(),
            account_identifier=self.account_identifier.GetValue().strip(),
            content_format="html",
        )

    def _on_provider_changed(self, _event: object | None) -> None:
        provider_id = self._provider_value()
        methods = provider_auth_methods(provider_id)
        self.auth_method.SetItems([publishing_auth_method_name(item) for item in methods])
        try:
            selection = methods.index(self._profile.auth_method)
        except ValueError:
            selection = 0
        self.auth_method.SetSelection(selection)
        self._on_auth_method_changed(None)

    def _on_auth_method_changed(self, _event: object | None) -> None:
        method = auth_method_definition(self._auth_method_value())
        self.identifier_label.Show(method.requires_identifier)
        self.account_identifier.Show(method.requires_identifier)
        self.secret_label.Show(method.requires_secret)
        self.secret.Show(method.requires_secret)
        self.reveal_secret.Show(method.requires_secret)
        self.secret_label.SetLabel(
            "Application password" if method.requires_secret else "Saved sign-in secret"
        )
        if not method.requires_secret:
            self._set_secret_revealed(False)
        self.dialog.Layout()

    def _on_toggle_secret_reveal(self, _event: object) -> None:
        self._set_secret_revealed(not self._secret_revealed)

    def _set_secret_revealed(self, revealed: bool) -> None:
        value = self.secret.GetValue()
        parent = self.secret.GetParent()
        self.secret_row.Detach(self.secret)
        self.secret.Destroy()
        style = 0 if revealed else self._wx.TE_PASSWORD
        self.secret = self._wx.TextCtrl(parent, style=style)
        self.secret.SetValue(value)
        self.secret.SetName("Application password")
        self.secret_row.Insert(0, self.secret, 1, self._wx.EXPAND | self._wx.RIGHT, 8)
        self._secret_revealed = revealed
        self.reveal_secret.SetLabel("Hide" if revealed else "Reveal")
        self.reveal_secret.SetName(
            "Hide application password" if revealed else "Reveal application password"
        )
        self.reveal_secret.MoveAfterInTabOrder(self.secret)
        self.dialog.Layout()

    def _on_verify_connection(self, _event: object) -> None:
        ok, message = verify_publishing_connection(self._current_profile(), self.secret.GetValue())
        self.last_verification_ok = ok
        self.last_verification_message = message
        self.connection_status.SetLabel(message)
        icon = self._wx.ICON_INFORMATION if ok else self._wx.ICON_WARNING
        self._wx.MessageBox(message, "Publishing Connection Check", icon | self._wx.OK)

    def show_modal(self) -> PublishingConnectionProfile | None:
        self.dialog.CentreOnParent()
        try:
            if show_modal_dialog(self.dialog, "Edit Publishing Connection") != self._wx.ID_OK:
                return None
            draft = self._current_profile()
            had_id = bool(draft.id)
            store = upsert_publishing_connection(draft)
            saved = None
            if had_id:
                for item in store.connections:
                    if item.id == draft.id:
                        saved = item
                        break
            else:
                for item in reversed(store.connections):
                    if (
                        item.site_url == draft.site_url
                        and item.label == (draft.label or item.label)
                        and item.account_identifier == draft.account_identifier
                    ):
                        saved = item
                        break
            if saved is None:
                return None
            save_publishing_secret(saved.id, self.secret.GetValue())
            self._profile = saved
            return saved
        finally:
            self.dialog.Destroy()


class PublishingConnectionsDialog:
    def __init__(self, parent: object) -> None:
        import wx

        self._wx = wx
        self.dialog = wx.Dialog(
            parent,
            title="Publishing Connections",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.dialog.SetSize((820, 520))

        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(
            wx.StaticText(
                self.dialog,
                label=(
                    "Manage your saved publishing connections here. You can keep multiple sites, "
                    "choose the current one, and verify the selected connection before publishing."
                ),
            ),
            0,
            wx.EXPAND | wx.ALL,
            8,
        )

        self.connection_list = wx.ListBox(self.dialog)
        self.connection_list.SetName("Saved publishing connections")
        root.Add(self.connection_list, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        self.summary = wx.TextCtrl(
            self.dialog,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.BORDER_SIMPLE,
            size=(-1, 120),
        )
        self.summary.SetName("Selected publishing connection details")
        root.Add(self.summary, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        actions = wx.BoxSizer(wx.HORIZONTAL)
        self.add_button = wx.Button(self.dialog, label="Add")
        self.edit_button = wx.Button(self.dialog, label="Edit")
        self.remove_button = wx.Button(self.dialog, label="Remove")
        self.use_button = wx.Button(self.dialog, label="Use This Connection")
        self.verify_button = wx.Button(self.dialog, label="Verify Current Connection")
        actions.Add(self.add_button, 0, wx.RIGHT, 8)
        actions.Add(self.edit_button, 0, wx.RIGHT, 8)
        actions.Add(self.remove_button, 0, wx.RIGHT, 8)
        actions.Add(self.use_button, 0, wx.RIGHT, 8)
        actions.Add(self.verify_button, 0)
        root.Add(actions, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        buttons = self.dialog.CreateButtonSizer(wx.OK | wx.CANCEL)
        if buttons is not None:
            root.Add(buttons, 0, wx.EXPAND | wx.ALL, 8)
        self.dialog.SetSizerAndFit(root)
        apply_modal_ids(self.dialog, affirmative_id=wx.ID_OK, escape_id=wx.ID_CANCEL)

        self.connection_list.Bind(wx.EVT_LISTBOX, self._on_selection_changed)
        self.add_button.Bind(wx.EVT_BUTTON, self._on_add)
        self.edit_button.Bind(wx.EVT_BUTTON, self._on_edit)
        self.remove_button.Bind(wx.EVT_BUTTON, self._on_remove)
        self.use_button.Bind(wx.EVT_BUTTON, self._on_use)
        self.verify_button.Bind(wx.EVT_BUTTON, self._on_verify)

        self._store = load_publishing_connections()
        self._refresh_connections()
        self.connection_list.SetFocus()

    def _refresh_connections(self) -> None:
        labels: list[str] = []
        selection = 0
        for index, item in enumerate(self._store.connections):
            label = (
                item.label or item.site_url or publishing_provider_display_name(item.provider_id)
            )
            if item.id == self._store.current_connection_id:
                label += " (Current)"
                selection = index
            labels.append(label)
        self.connection_list.Set(labels)
        if labels:
            self.connection_list.SetSelection(selection)
        self._update_summary()

    def _selected_connection(self) -> PublishingConnectionProfile | None:
        selection = self.connection_list.GetSelection()
        if selection == self._wx.NOT_FOUND or selection < 0:
            return None
        if selection >= len(self._store.connections):
            return None
        return self._store.connections[selection]

    def _update_summary(self) -> None:
        selected = self._selected_connection()
        if selected is None:
            self.summary.SetValue("No publishing connection selected.")
            return
        method = auth_method_definition(selected.auth_method)
        lines = [
            f"Label: {selected.label or '(unnamed connection)'}",
            f"Provider: {publishing_provider_display_name(selected.provider_id)}",
            f"Site URL: {selected.site_url or '(not set)'}",
            f"Sign-in method: {method.name}",
        ]
        if method.requires_identifier:
            lines.append(f"Sign-in name or email: {selected.account_identifier or '(not set)'}")
        lines.append(
            "Current connection: yes"
            if selected.id == self._store.current_connection_id
            else "Current connection: no"
        )
        self.summary.SetValue("\n".join(lines))

    def _on_selection_changed(self, _event: object) -> None:
        self._update_summary()

    def _on_add(self, _event: object) -> None:
        dialog = EditPublishingConnectionDialog(self.dialog)
        if dialog.show_modal() is None:
            return
        self._store = load_publishing_connections()
        self._refresh_connections()

    def _on_edit(self, _event: object) -> None:
        selected = self._selected_connection()
        if selected is None:
            return
        dialog = EditPublishingConnectionDialog(self.dialog, selected)
        if dialog.show_modal() is None:
            return
        self._store = load_publishing_connections()
        self._refresh_connections()

    def _on_remove(self, _event: object) -> None:
        selected = self._selected_connection()
        if selected is None:
            return
        answer = self._wx.MessageBox(
            f"Remove the publishing connection '{selected.label or selected.site_url}'?",
            "Remove Publishing Connection",
            self._wx.YES_NO | self._wx.ICON_WARNING,
        )
        if answer != self._wx.YES:
            return
        self._store = remove_publishing_connection(selected.id)
        self._refresh_connections()

    def _on_use(self, _event: object) -> None:
        selected = self._selected_connection()
        if selected is None:
            return
        self._store = set_current_publishing_connection(selected.id)
        self._refresh_connections()

    def _on_verify(self, _event: object) -> None:
        selected = self._selected_connection()
        if selected is None:
            return
        secret = load_publishing_secret(selected.id)
        ok, message = verify_publishing_connection(selected, secret)
        icon = self._wx.ICON_INFORMATION if ok else self._wx.ICON_WARNING
        self._wx.MessageBox(message, "Publishing Connection Check", icon | self._wx.OK)
        self.summary.SetValue(self.summary.GetValue() + f"\n\nLast check: {message}")

    def show_modal(self) -> bool:
        self.dialog.CentreOnParent()
        try:
            return show_modal_dialog(self.dialog, "Publishing Connections") == self._wx.ID_OK
        finally:
            self.dialog.Destroy()
