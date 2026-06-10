"""Tests for MainFrame dialog contract helpers (M-28: crash recovery focus)."""

from __future__ import annotations

from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[3] / "quill" / "ui" / "main_frame.py").read_text(
    encoding="utf-8"
)


def test_show_modal_dialog_has_restore_editor_focus_param() -> None:
    # M-28: _show_modal_dialog must accept restore_editor_focus to prevent
    # focus-racing in loops that re-show the same dialog.
    assert "restore_editor_focus: bool = True" in SOURCE


def test_crash_recovery_loop_does_not_steal_focus() -> None:
    # M-28: The crash-recovery re-show loop must pass restore_editor_focus=False
    # so editor.SetFocus is not called between loop iterations, which would race
    # with the dialog's own focus management.
    assert "restore_editor_focus=False" in SOURCE
    # The _show_modal_dialog call for Crash Recovery must carry the flag.
    crash_call = (
        "_show_modal_dialog(\n"
        '                    dialog, "Crash Recovery", restore_editor_focus=False\n'
        "                )"
    )
    assert crash_call in SOURCE


def test_remote_publishing_open_records_explicit_html_surface_metadata() -> None:
    # Publishing content currently opens as raw HTML in a normal editor tab.
    # Until the approved representation chooser lands, the metadata should say
    # that explicitly so later update flows do not have to guess.
    assert '"source_kind": "publishing_remote"' in SOURCE
    assert '"publishing_authoring_surface": "html"' in SOURCE
    assert '"publishing_open_representation": "raw_html"' in SOURCE
