from __future__ import annotations

from pathlib import Path

from quill.core.document import Document
from quill.ui.main_frame import MainFrame


class _Frame:
    pass


def _build_frame() -> MainFrame:
    frame = MainFrame.__new__(MainFrame)
    frame.frame = _Frame()
    frame.document = Document(path=Path("note.md"), text="hello")
    frame.settings = type("Settings", (), {})()
    frame.keymap = {"file.open": "Ctrl+O"}
    frame._notifications = []
    frame._wx = type("Wx", (), {"version": staticmethod(lambda: "4.2-test")})()
    frame._set_status = lambda message: setattr(frame, "_status_message", message)
    frame._record_notification = lambda message, category="info": setattr(
        frame, "_notification", (message, category)
    )
    return frame


def test_report_bug_reviews_then_opens_support_form(monkeypatch) -> None:
    frame = _build_frame()
    opened: list[str] = []
    copied: list[str] = []
    monkeypatch.setattr(
        frame,
        "_review_bug_report",
        lambda: ({"summary": "Bug report: note.md", "body": "Body"}, "https://example.invalid"),
    )
    monkeypatch.setattr(frame, "_copy_to_clipboard", lambda text: copied.append(text) or True)
    monkeypatch.setattr("quill.ui.main_frame.webbrowser.open", lambda url: opened.append(url))

    frame.report_bug()

    assert copied == ["Body"]
    assert opened == ["https://example.invalid"]
    assert frame._notification == ("Opened support-hub bug report form", "support")


def test_save_diagnostics_bundle_cancels_when_review_cancelled(monkeypatch) -> None:
    frame = _build_frame()
    monkeypatch.setattr(frame, "_review_diagnostics_export", lambda: None)

    frame.save_diagnostics_bundle()

    assert frame._status_message == "Diagnostics export cancelled"