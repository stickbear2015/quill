from __future__ import annotations

from quill.ui.preview_dialog import _build_accessible_dialog_body


def test_dialog_body_returns_html_unchanged_when_no_anchor() -> None:
    # The library owns focus/keyboard management; no script should be injected
    # when there is nothing Quill-specific to add.
    body = "<h1>About</h1>"
    result = _build_accessible_dialog_body(body)

    assert result == body
    assert "<script>" not in result


def test_dialog_body_does_not_inject_focus_or_keydown_listeners() -> None:
    html = _build_accessible_dialog_body("<p>Read me</p>")

    assert "c.focus()" not in html
    assert "tabindex" not in html
    assert "keydown" not in html
    assert "addEventListener" not in html


def test_dialog_body_scrolls_to_anchor_when_provided() -> None:
    html = _build_accessible_dialog_body("<h2 id='startup'>Startup</h2>", start_anchor="startup")

    assert 'document.getElementById("startup")' in html
    assert "n.scrollIntoView()" in html
    # Must not contain any focus or keyboard manipulation alongside the scroll
    assert "c.focus()" not in html
    assert "keydown" not in html


def test_dialog_body_no_script_injected_without_anchor() -> None:
    # Empty / None body should also come back clean.
    assert _build_accessible_dialog_body("") == ""
    assert _build_accessible_dialog_body(None) == ""  # type: ignore[arg-type]
