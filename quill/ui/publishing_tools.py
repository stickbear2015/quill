from __future__ import annotations

from quill.core.publishing import (
    PublishingConnectionSettings,
    load_publishing_app_password,
    load_publishing_connection_settings,
    save_publishing_app_password,
    save_publishing_connection_settings,
    verify_publishing_connection,
)
from quill.core.publishing_providers import (
    SUPPORTED_PUBLISHING_PROVIDERS,
    publishing_provider_display_name,
    publishing_provider_help_text,
)
from quill.ui.dialog_contract import apply_modal_ids, show_modal_dialog


class PublishingConnectionDialog:
    _PROVIDER_CHOICES: tuple[tuple[str, str], ...] = tuple(
        (provider_id, publishing_provider_display_name(provider_id))
        for provider_id in sorted(SUPPORTED_PUBLISHING_PROVIDERS)
    )

    def __init__(self, parent: object) -> None:
        import wx

        self._wx = wx
        self.dialog = wx.Dialog(
            parent,
            title="Publishing Connection Settings",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self.dialog.SetSize((760, 460))

        self._settings = load_publishing_connection_settings()
        self._app_password = load_publishing_app_password()
        self._app_password_revealed = False
        self.last_verification_ok: bool | None = None
        self.last_verification_message: str = "Not checked"

        root = wx.BoxSizer(wx.VERTICAL)
        root.Add(
            wx.StaticText(
                self.dialog,
                label=(
                    "Select a publishing provider, enter the site details, and verify the "
                    "connection before publishing. This works with WordPress.com and "
                    "self-hosted WordPress sites that expose the standard REST API."
                ),
            ),
            0,
            wx.EXPAND | wx.ALL,
            8,
        )

        panel = wx.Panel(self.dialog)
        panel_sizer = wx.BoxSizer(wx.VERTICAL)

        self.provider = wx.Choice(
            panel,
            choices=[label for _value, label in self._PROVIDER_CHOICES],
        )
        self.provider.SetName("Provider")
        self.provider.SetSelection(self._provider_choice_index(self._settings.provider))
        panel_sizer.Add(wx.StaticText(panel, label="Provider"), 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
        panel_sizer.Add(self.provider, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        self.provider_hint = wx.StaticText(panel, label="")
        panel_sizer.Add(self.provider_hint, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        self.site_url = wx.TextCtrl(panel)
        self.site_url.SetValue(self._settings.site_url)
        self.site_url.SetName("Site URL")
        panel_sizer.Add(wx.StaticText(panel, label="Site URL"), 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
        panel_sizer.Add(self.site_url, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        self.username = wx.TextCtrl(panel)
        self.username.SetValue(self._settings.username)
        self.username.SetName("Username")
        panel_sizer.Add(wx.StaticText(panel, label="Username"), 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
        panel_sizer.Add(self.username, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        self.app_password_label = wx.StaticText(panel, label="Application password")
        panel_sizer.Add(self.app_password_label, 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)

        self.app_password_row = wx.BoxSizer(wx.HORIZONTAL)
        self.app_password = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        self.app_password.SetValue(self._app_password)
        self.app_password.SetName("Application password")
        self.app_password_row.Add(self.app_password, 1, wx.EXPAND | wx.RIGHT, 8)
        self.reveal_app_password = wx.Button(panel, label="Reveal")
        self.reveal_app_password.SetName("Reveal application password")
        self.app_password_row.Add(self.reveal_app_password, 0)
        panel_sizer.Add(self.app_password_row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
        self.app_password_hint = wx.StaticText(
            panel,
            label="The application password is stored securely on this device.",
        )
        panel_sizer.Add(self.app_password_hint, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        actions = wx.BoxSizer(wx.HORIZONTAL)
        self.verify_button = wx.Button(panel, label="Verify Connection")
        actions.Add(self.verify_button, 0)
        panel_sizer.Add(actions, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)

        self.connection_status = wx.StaticText(
            panel,
            label="Verify the connection before publishing to this site.",
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
        self.verify_button.Bind(wx.EVT_BUTTON, self._on_verify_connection)
        self.reveal_app_password.Bind(wx.EVT_BUTTON, self._on_toggle_app_password_reveal)
        self._on_provider_changed(None)

    def _provider_choice_index(self, provider: str) -> int:
        normalized = provider.strip().lower()
        for index, (value, _label) in enumerate(self._PROVIDER_CHOICES):
            if value == normalized:
                return index
        return 0

    def _provider_value(self) -> str:
        selection = self.provider.GetSelection()
        if selection < 0 or selection >= len(self._PROVIDER_CHOICES):
            return self._PROVIDER_CHOICES[0][0]
        return self._PROVIDER_CHOICES[selection][0]

    def _current_settings(self) -> PublishingConnectionSettings:
        provider = self._provider_value()
        return PublishingConnectionSettings(
            provider=provider,
            site_url=self.site_url.GetValue().strip(),
            username=self.username.GetValue().strip(),
            content_format="html",
        )

    def _on_provider_changed(self, _event: object | None) -> None:
        provider = self._provider_value()
        self.provider_hint.SetLabel(publishing_provider_help_text(provider))
        self.dialog.Layout()

    def _on_toggle_app_password_reveal(self, _event: object) -> None:
        self._set_app_password_revealed(not self._app_password_revealed)

    def _set_app_password_revealed(self, revealed: bool) -> None:
        value = self.app_password.GetValue()
        parent = self.app_password.GetParent()
        self.app_password_row.Detach(self.app_password)
        self.app_password.Destroy()
        style = 0 if revealed else self._wx.TE_PASSWORD
        self.app_password = self._wx.TextCtrl(parent, style=style)
        self.app_password.SetValue(value)
        self.app_password.SetName("Application password")
        self.app_password_row.Insert(0, self.app_password, 1, self._wx.EXPAND | self._wx.RIGHT, 8)
        self._app_password_revealed = revealed
        self.reveal_app_password.SetLabel("Hide" if revealed else "Reveal")
        self.reveal_app_password.SetName(
            "Hide application password" if revealed else "Reveal application password"
        )
        self.dialog.Layout()

    def _on_verify_connection(self, _event: object) -> None:
        ok, message = verify_publishing_connection(
            self._current_settings(),
            self.app_password.GetValue(),
        )
        self.last_verification_ok = ok
        self.last_verification_message = message
        self.connection_status.SetLabel(message)
        icon = self._wx.ICON_INFORMATION if ok else self._wx.ICON_WARNING
        self._wx.MessageBox(message, "Publishing Connection Check", icon | self._wx.OK)

    def show_modal(self) -> bool:
        self.dialog.CentreOnParent()
        try:
            if show_modal_dialog(self.dialog, "Publishing Connection Settings") != self._wx.ID_OK:
                return False
            settings = self._current_settings()
            app_password = self.app_password.GetValue()
            save_publishing_connection_settings(settings)
            save_publishing_app_password(app_password)
            ok, message = verify_publishing_connection(settings, app_password)
            self.last_verification_ok = ok
            self.last_verification_message = message
            self.connection_status.SetLabel(message)
            return True
        finally:
            self.dialog.Destroy()
