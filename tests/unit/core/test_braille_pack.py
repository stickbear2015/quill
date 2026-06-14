"""#243 (BR-020): optional braille pack detection and stub install."""

from __future__ import annotations

import sys
import types

import quill.core.braille_pack as pack


def test_not_installed_in_default_env(monkeypatch) -> None:
    monkeypatch.setattr(pack.shutil, "which", lambda _name: None)
    monkeypatch.setattr(pack.importlib.util, "find_spec", lambda _name: None)
    for name in ("louis", "lou_translate"):
        monkeypatch.delitem(sys.modules, name, raising=False)
    assert pack.is_braille_pack_installed() is False
    assert pack.braille_pack_version() is None


def test_installed_when_module_present(monkeypatch) -> None:
    monkeypatch.setattr(pack.shutil, "which", lambda _name: None)
    monkeypatch.setitem(sys.modules, "lou_translate", types.ModuleType("lou_translate"))
    assert pack.is_braille_pack_installed() is True


def test_installed_when_cli_on_path(monkeypatch) -> None:
    monkeypatch.setattr(
        pack.shutil,
        "which",
        lambda name: "/usr/bin/lou_translate" if name == "lou_translate" else None,
    )
    assert pack.is_braille_pack_installed() is True


def test_install_is_a_stub_that_reports_progress(monkeypatch) -> None:
    messages: list[str] = []
    result = pack.install_braille_pack(messages.append)
    assert result is False
    assert messages and "Braille Pack" in messages[0]
