"""Unit tests for quill.core.multi_press.MultiPressDispatcher."""

from __future__ import annotations

from quill.core.multi_press import MultiPressDispatcher


class TestMultiPressDispatcher:
    def test_first_press_needs_timer(self) -> None:
        d = MultiPressDispatcher()
        count, needs_timer = d.press("action")
        assert count == 1
        assert needs_timer is True

    def test_second_press_needs_timer(self) -> None:
        d = MultiPressDispatcher()
        d.press("action")
        count, needs_timer = d.press("action")
        assert count == 2
        assert needs_timer is True

    def test_third_press_fires_immediately(self) -> None:
        d = MultiPressDispatcher()
        d.press("action")
        d.press("action")
        count, needs_timer = d.press("action")
        assert count == 3
        assert needs_timer is False

    def test_third_press_clears_state(self) -> None:
        d = MultiPressDispatcher()
        d.press("action")
        d.press("action")
        d.press("action")
        count, needs_timer = d.press("action")
        assert count == 1  # restarted
        assert needs_timer is True

    def test_timeout_returns_count_and_clears(self) -> None:
        d = MultiPressDispatcher()
        d.press("action")
        d.press("action")
        count = d.timeout("action")
        assert count == 2
        count2, _ = d.press("action")
        assert count2 == 1

    def test_timeout_with_no_pending_returns_one(self) -> None:
        d = MultiPressDispatcher()
        assert d.timeout("action") == 1

    def test_cancel_clears_pending(self) -> None:
        d = MultiPressDispatcher()
        d.press("action")
        d.cancel("action")
        count, _ = d.press("action")
        assert count == 1

    def test_different_bindings_are_independent(self) -> None:
        d = MultiPressDispatcher()
        d.press("a")
        d.press("a")
        count_b, _ = d.press("b")
        assert count_b == 1

    def test_reset_clears_all(self) -> None:
        d = MultiPressDispatcher()
        d.press("a")
        d.press("b")
        d.reset()
        ca, _ = d.press("a")
        cb, _ = d.press("b")
        assert ca == 1
        assert cb == 1

    def test_window_ms_property(self) -> None:
        d = MultiPressDispatcher(window_ms=300)
        assert d.window_ms == 300

    def test_custom_max_count(self) -> None:
        d = MultiPressDispatcher(max_count=2)
        d.press("action")
        count, needs_timer = d.press("action")
        assert count == 2
        assert needs_timer is False
