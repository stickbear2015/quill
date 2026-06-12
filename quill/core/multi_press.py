"""MultiPressDispatcher — tracks rapid consecutive presses of the same binding.

Usage (caller owns the timer via wx.CallLater or similar):

    dispatcher = MultiPressDispatcher()

    # In a key handler:
    count, needs_timer = dispatcher.press("edit.paste_from_tray_1")
    if needs_timer:
        # (Re)start a timer for dispatcher.window_ms.
        # When it fires: count = dispatcher.timeout("edit.paste_from_tray_1")
        # Then dispatch based on count.
    else:
        # max_count reached — fire immediately without waiting.
        dispatch_action(count)
"""

from __future__ import annotations


class MultiPressDispatcher:
    """Pure-Python state machine for multi-press key combos.

    Timer scheduling is left to the caller (wx.CallLater, threading.Timer,
    etc.) so this class carries no UI or threading dependencies.
    """

    def __init__(self, window_ms: int = 400, max_count: int = 3) -> None:
        self._window_ms = window_ms
        self._max_count = max_count
        self._pending: dict[str, int] = {}

    @property
    def window_ms(self) -> int:
        return self._window_ms

    def press(self, binding: str) -> tuple[int, bool]:
        """Record a key press. Returns (current_count, needs_timer).

        If needs_timer is False, the max_count was reached — fire immediately.
        If needs_timer is True, (re)start a timer for window_ms; on expiry
        call timeout(binding) to finalize the count and take action.
        """
        count = self._pending.get(binding, 0) + 1
        if count >= self._max_count:
            self._pending.pop(binding, None)
            return count, False
        self._pending[binding] = count
        return count, True

    def timeout(self, binding: str) -> int:
        """Called on timer expiry. Returns accumulated count and clears state."""
        return self._pending.pop(binding, 0) or 1

    def cancel(self, binding: str) -> None:
        self._pending.pop(binding, None)

    def reset(self) -> None:
        self._pending.clear()
