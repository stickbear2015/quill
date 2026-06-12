"""Source-contract tests for AbbreviationManagerDialog and _AbbreviationEditDialog.

Verifies dialog-inventory registration and A11Y-4 hardening contract without
constructing wx widgets (no wx dependency in this file).
"""

from __future__ import annotations

import json
from pathlib import Path


def _load_inventory() -> dict[str, str]:
    inv_path = Path(__file__).parent / "fixtures" / "dialog_inventory.json"
    return json.loads(inv_path.read_text(encoding="utf-8"))


def test_abbreviation_manager_dialog_registered_in_inventory() -> None:
    inv = _load_inventory()
    key = "quill/ui/abbreviation_manager_dialog.py::AbbreviationManagerDialog.__init__::wx.Dialog"
    assert key in inv, f"Dialog surface not in inventory: {key}"
    assert inv[key] == "hardened_custom"


def test_abbreviation_edit_dialog_registered_in_inventory() -> None:
    inv = _load_inventory()
    key = "quill/ui/abbreviation_manager_dialog.py::_AbbreviationEditDialog.__init__::wx.Dialog"
    assert key in inv, f"Dialog surface not in inventory: {key}"
    assert inv[key] == "hardened_custom"


def test_abbreviation_manager_delete_dialog_registered() -> None:
    inv = _load_inventory()
    key = (
        "quill/ui/abbreviation_manager_dialog.py"
        "::AbbreviationManagerDialog._on_delete::wx.MessageDialog"
    )
    assert key in inv, f"Dialog surface not in inventory: {key}"


def test_abbreviation_manager_apply_modal_ids_called() -> None:
    source = (
        Path(__file__).parent.parent.parent.parent
        / "quill"
        / "ui"
        / "abbreviation_manager_dialog.py"
    ).read_text(encoding="utf-8")
    assert "apply_modal_ids" in source, "AbbreviationManagerDialog must call apply_modal_ids"
    assert source.count("apply_modal_ids") >= 2, "Both dialog classes must call apply_modal_ids"


def test_abbreviation_manager_exposes_show_and_close() -> None:
    source = (
        Path(__file__).parent.parent.parent.parent
        / "quill"
        / "ui"
        / "abbreviation_manager_dialog.py"
    ).read_text(encoding="utf-8")
    assert "def show(self)" in source
    assert "def close(self)" in source


def test_abbreviation_manager_has_import_export() -> None:
    source = (
        Path(__file__).parent.parent.parent.parent
        / "quill"
        / "ui"
        / "abbreviation_manager_dialog.py"
    ).read_text(encoding="utf-8")
    assert "_on_import" in source, "Import handler must be present"
    assert "_on_export" in source, "Export handler must be present"


def test_abbreviation_manager_has_search_field() -> None:
    source = (
        Path(__file__).parent.parent.parent.parent
        / "quill"
        / "ui"
        / "abbreviation_manager_dialog.py"
    ).read_text(encoding="utf-8")
    assert "_search_ctrl" in source, "Search field must be present"
    assert "_on_search" in source, "Search handler must be present"
