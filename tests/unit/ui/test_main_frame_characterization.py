from __future__ import annotations

from quill.tools.ui_surface import (
    load_snapshot,
    main_frame_public_methods,
)


def test_main_frame_public_surface_is_unchanged() -> None:
    """Characterization gate (GATE-6).

    The public method surface of MainFrame is frozen so that decomposing the
    18k-line module stays behavior-preserving. If this fails because of a
    deliberate refactor (a method moved to a collaborator, was renamed, or was
    intentionally removed), regenerate the snapshot with
    ``python -m quill.tools.ui_surface --write`` and review the diff.
    """
    live = main_frame_public_methods()
    snapshot = load_snapshot()

    added = sorted(set(live) - set(snapshot))
    removed = sorted(set(snapshot) - set(live))

    assert not removed, (
        "MainFrame public methods were removed or renamed without updating the "
        f"characterization snapshot: {removed}. If intentional, run "
        "'python -m quill.tools.ui_surface --write'."
    )
    assert not added, (
        "MainFrame gained new public methods not in the characterization "
        f"snapshot: {added}. If intentional, run "
        "'python -m quill.tools.ui_surface --write'."
    )
