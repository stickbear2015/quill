"""The main window must always close, even if a shutdown step fails (#210)."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

import quill.stability.shutdown_watchdog as watchdog
import quill.ui.main_frame as mf
from quill.ui.main_frame import MainFrame


class _FakeWx:
    @staticmethod
    def GetTopLevelWindows() -> list[Any]:
        return []

    @staticmethod
    def GetApp() -> Any:
        return None

    @staticmethod
    def CallAfter(*_a: object, **_k: object) -> None:
        pass


def _raise() -> None:
    raise RuntimeError("boom")


def _frame_for_close(monkeypatch: pytest.MonkeyPatch) -> MainFrame:
    # Avoid real disk/lock side effects from the guarded shutdown steps.
    monkeypatch.setattr(mf, "save_settings", lambda *_a, **_k: None)
    monkeypatch.setattr(mf, "mark_clean_exit", lambda *_a, **_k: None)

    frame = MainFrame.__new__(MainFrame)
    frame.settings = SimpleNamespace(tray_enabled=False)
    frame._is_exiting = True
    frame._can_close_all_documents = lambda: True  # type: ignore[method-assign]
    frame._watch_queue_monitor = None
    # Several steps deliberately raise to prove they cannot block the close.
    frame._watch_service = SimpleNamespace(stop=_raise)
    frame._unregister_global_hotkeys = _raise  # type: ignore[method-assign]
    frame._remove_tray_icon = lambda: None  # type: ignore[method-assign]
    frame.close_ssh_connections = _raise  # type: ignore[method-assign]
    frame.flush_persistent_undo = _raise  # type: ignore[method-assign]
    frame.session_id = "test-session"
    frame._wx = _FakeWx()
    frame.frame = object()
    return frame


def test_on_close_always_skips_even_when_cleanup_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    frame = _frame_for_close(monkeypatch)
    skipped: list[bool] = []
    vetoed: list[bool] = []
    event = SimpleNamespace(
        Skip=lambda: skipped.append(True),
        Veto=lambda: vetoed.append(True),
    )

    frame._on_close(event)

    assert skipped == [True], "the window must close (event.Skip) despite failing steps"
    assert vetoed == []


def test_on_close_vetoes_when_documents_cannot_close(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    frame = _frame_for_close(monkeypatch)
    frame._can_close_all_documents = lambda: False  # type: ignore[method-assign]
    skipped: list[bool] = []
    vetoed: list[bool] = []
    event = SimpleNamespace(
        Skip=lambda: skipped.append(True),
        Veto=lambda: vetoed.append(True),
    )

    frame._on_close(event)

    assert vetoed == [True]
    assert skipped == []


def test_on_close_closes_even_if_save_prompt_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # A raising save-on-close prompt is a bug, not a Cancel; the window must
    # still close (#210) rather than being trapped open with nothing to force it.
    frame = _frame_for_close(monkeypatch)
    frame._can_close_all_documents = _raise  # type: ignore[method-assign]
    skipped: list[bool] = []
    vetoed: list[bool] = []
    event = SimpleNamespace(
        Skip=lambda: skipped.append(True),
        Veto=lambda: vetoed.append(True),
    )

    frame._on_close(event)

    assert skipped == [True]
    assert vetoed == []


class _FakeTimer:
    """Records that a hard-exit watchdog timer was started, without arming it."""

    instances: list[_FakeTimer] = []

    def __init__(self, interval: float, function: Any) -> None:
        self.interval = interval
        self.function = function
        self.daemon = False
        self.started = False
        _FakeTimer.instances.append(self)

    def start(self) -> None:
        self.started = True


def _arm_capable_frame(monkeypatch: pytest.MonkeyPatch) -> MainFrame:
    frame = _frame_for_close(monkeypatch)
    # A real frame enables the hard-exit watchdog; __new__ frames do not, which
    # is why the resilience tests above never arm a real os._exit timer.
    frame._hard_exit_enabled = True
    _FakeTimer.instances = []
    monkeypatch.setattr(watchdog.threading, "Timer", _FakeTimer)
    return frame


def test_committed_close_arms_hard_exit_watchdog(monkeypatch: pytest.MonkeyPatch) -> None:
    frame = _arm_capable_frame(monkeypatch)
    event = SimpleNamespace(Skip=lambda: None, Veto=lambda: None)

    frame._on_close(event)

    assert len(_FakeTimer.instances) == 1, "a committed close must arm the watchdog (#210)"
    timer = _FakeTimer.instances[0]
    assert timer.started is True
    assert timer.daemon is True
    assert timer.interval > 0


def test_vetoed_close_does_not_arm_watchdog(monkeypatch: pytest.MonkeyPatch) -> None:
    frame = _arm_capable_frame(monkeypatch)
    frame._can_close_all_documents = lambda: False  # type: ignore[method-assign]
    event = SimpleNamespace(Skip=lambda: None, Veto=lambda: None)

    frame._on_close(event)

    assert _FakeTimer.instances == [], "a vetoed close must not force-exit the process"


def test_force_exit_callback_calls_os_exit(monkeypatch: pytest.MonkeyPatch) -> None:
    frame = _arm_capable_frame(monkeypatch)
    event = SimpleNamespace(Skip=lambda: None, Veto=lambda: None)
    frame._on_close(event)

    exits: list[int] = []
    monkeypatch.setattr(watchdog.os, "_exit", lambda code: exits.append(code))

    _FakeTimer.instances[0].function()

    assert exits == [0], "the watchdog must force the process to exit when it fires"
