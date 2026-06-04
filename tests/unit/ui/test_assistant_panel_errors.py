from __future__ import annotations

from quill.ui.assistant_panel import classify_assistant_error


def test_classify_assistant_error_native_loader_failure() -> None:
    message, disable_chat = classify_assistant_error(
        "llama-cpp-python failed to load native code on this machine "
        "(Windows error 0xc000001d). Install a CPU-compatible build or disable AI."
    )

    # Issue #137: the user-facing message must be plain-language and
    # platform-neutral — no hex codes, no "Windows", no library jargon — even
    # though the raw error (the trigger) contains those technical details.
    assert "0xc000001d" not in message
    assert "Windows" not in message
    assert "llama" not in message.lower()
    assert "turn AI off" in message
    assert disable_chat is True


def test_classify_assistant_error_generic() -> None:
    message, disable_chat = classify_assistant_error("temporary network issue")

    assert message == "Error: temporary network issue"
    assert disable_chat is False
