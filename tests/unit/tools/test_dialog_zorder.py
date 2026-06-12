"""Gate: dialog z-order (A11Y-Z-ORDER).

Detects the anti-pattern where FlexGridSizer row helpers receive pre-created
controls instead of factory lambdas, causing wx.StaticText labels to appear
AFTER their controls in the child-window z-order. Screen readers use z-order
to associate labels with controls; reversing it causes mis-labelling or double
announcements when the user tabs through a form.
"""

from __future__ import annotations

from pathlib import Path

from quill.tools.check_dialog_zorder import audit_package

_REPO_ROOT = Path(__file__).resolve().parents[3]
_PACKAGE_ROOT = _REPO_ROOT / "quill"


def test_no_dialog_zorder_violations() -> None:
    violations = audit_package(_PACKAGE_ROOT)
    messages = [f"{v.file.relative_to(_REPO_ROOT)}:{v.line}: {v.detail}" for v in violations]
    assert not violations, (
        "A11Y-Z-ORDER violations found (labels created after controls in dialog "
        "grid helpers). Fix by passing a factory lambda instead of a pre-created "
        "control:\n  row('Label', lambda: wx.TextCtrl(...))  # correct\n"
        "  row('Label', self.ctrl)                   # wrong\n\n" + "\n".join(messages)
    )
