from __future__ import annotations

import sys

import pytest

pytestmark = pytest.mark.skipif(
    sys.platform != "darwin", reason="Apple Foundation Models is macOS-only"
)

from quill.core.ai.foundation_models import FoundationModelsBackend


def test_backend_reports_availability() -> None:
    available, reason = FoundationModelsBackend().is_available()
    assert isinstance(available, bool)
    if not available:
        assert isinstance(reason, str)


def test_respond_when_available() -> None:
    backend = FoundationModelsBackend()
    available, _ = backend.is_available()
    if not available:
        pytest.skip("Apple Intelligence not available on this machine")
    out = backend.respond("Reply with exactly the word: ok")
    assert isinstance(out, str) and out.strip() != ""


def test_event_loop_reused_across_calls() -> None:
    # M-5: each call to respond() must reuse the same event loop rather than
    # creating a fresh one, preventing OS resource leaks on macOS 26+.
    import asyncio
    from unittest.mock import AsyncMock, MagicMock

    backend = FoundationModelsBackend()

    fake_fm = MagicMock()
    session_mock = MagicMock()
    session_mock.respond = AsyncMock(return_value="hello")
    fake_fm.LanguageModelSession.return_value = session_mock
    backend._fm = fake_fm

    loops_used: list[asyncio.AbstractEventLoop] = []

    original_get_loop = backend._get_loop

    def capturing_get_loop():
        loop = original_get_loop()
        loops_used.append(loop)
        return loop

    backend._get_loop = capturing_get_loop

    backend.respond("ping")
    backend.respond("ping")

    assert len(loops_used) == 2
    assert loops_used[0] is loops_used[1], "event loop must be reused across calls"
