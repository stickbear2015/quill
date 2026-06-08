"""Issue #126: preview panes must follow the OS appearance under the default
``system`` theme so links are not low-contrast blue on a dark desktop."""

from __future__ import annotations

from types import SimpleNamespace

from quill.ui.main_frame import MainFrame


class _Appearance:
    def __init__(self, dark: bool) -> None:
        self._dark = dark

    def IsDark(self) -> bool:  # noqa: N802
        return self._dark


class _SystemSettings:
    def __init__(self, dark: bool) -> None:
        self._dark = dark

    def GetAppearance(self) -> _Appearance:  # noqa: N802
        return _Appearance(self._dark)


def _frame(theme: str, system_dark: bool) -> MainFrame:
    frame = MainFrame.__new__(MainFrame)
    frame.settings = SimpleNamespace(theme=theme)
    frame._wx = SimpleNamespace(SystemSettings=_SystemSettings(system_dark))
    return frame


def test_explicit_dark_theme_is_dark() -> None:
    assert _frame("dark", system_dark=False)._preview_is_dark() is True


def test_explicit_light_theme_is_not_dark() -> None:
    assert _frame("light", system_dark=True)._preview_is_dark() is False


def test_system_theme_follows_dark_os_appearance() -> None:
    assert _frame("system", system_dark=True)._preview_is_dark() is True


def test_system_theme_stays_light_on_light_os() -> None:
    assert _frame("system", system_dark=False)._preview_is_dark() is False
