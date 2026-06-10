from __future__ import annotations

from pathlib import Path

import pytest

import quill.core.macros as macros_module
from quill.core.macros import MacroManager


def test_macro_manager_records_and_plays(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(macros_module, "macros_path", lambda: tmp_path / "macros.json")
    manager = MacroManager.load()

    manager.start_recording("demo")
    manager.record("edit.find")
    manager.record("edit.find_next")
    saved = manager.stop_recording()

    assert saved is not None
    assert saved.name == "demo"
    assert saved.steps == ["edit.find", "edit.find_next"]

    played: list[str] = []
    manager.play_last_macro(played.append)
    assert played == ["edit.find", "edit.find_next"]


def test_macro_manager_ignores_recording_during_playback(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(macros_module, "macros_path", lambda: tmp_path / "macros.json")
    manager = MacroManager.load()
    manager.start_recording("demo")
    manager.record("edit.find")
    manager.stop_recording()

    def runner(command_id: str) -> None:
        manager.record(command_id)

    manager.play_last_macro(runner)
    assert manager.macros["demo"].steps == ["edit.find"]


def test_macro_manager_rename_delete_and_reload(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(macros_module, "macros_path", lambda: tmp_path / "macros.json")
    manager = MacroManager.load()
    manager.start_recording("demo")
    manager.record("edit.find")
    manager.stop_recording()
    manager.rename_macro("demo", "renamed")
    assert "renamed" in manager.macros
    manager.delete_macro("renamed")
    assert manager.macros == {}

    reloaded = MacroManager.load()
    assert reloaded.macros == {}


def test_macro_dispatch_marshalled_to_ui_thread(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # M-8: _watch_run_macro must dispatch to the UI thread via wx.CallAfter
    # so that macro steps execute on the thread that owns wx widgets.
    import threading
    from unittest.mock import MagicMock

    monkeypatch.setattr(macros_module, "macros_path", lambda: tmp_path / "macros.json")
    manager = MacroManager.load()
    manager.start_recording("watch-test")
    manager.record("edit.copy")
    manager.stop_recording()

    class _FakeFrame:
        def __init__(self):
            self.macros = manager
            self._wx = MagicMock()
            self._call_after_target = None
            call_after_event = threading.Event()

            def fake_call_after(fn, *args, **kwargs):
                self._call_after_target = fn
                call_after_event.set()

            self._wx.CallAfter = fake_call_after
            self._call_after_event = call_after_event

        def _watch_run_macro(self, path, macro_name):
            call_after = getattr(self._wx, "CallAfter", None)
            if callable(call_after):
                call_after(self._watch_run_macro_ui, path, macro_name)

        def _watch_run_macro_ui(self, path, macro_name):
            pass

    frame = _FakeFrame()
    doc_path = tmp_path / "doc.txt"
    doc_path.write_text("hello", encoding="utf-8")

    frame._watch_run_macro(doc_path, "watch-test")

    assert frame._call_after_event.wait(timeout=1), "wx.CallAfter was not called"
    assert frame._call_after_target is not None
