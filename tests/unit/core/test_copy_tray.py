"""Unit tests for quill.core.copy_tray — CopyTray and TraySlot."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from quill.core.copy_tray import CopyTray, TraySlot

# ---------------------------------------------------------------------------
# TraySlot helpers
# ---------------------------------------------------------------------------


def test_tray_slot_is_empty_when_no_text() -> None:
    assert TraySlot().is_empty()


def test_tray_slot_not_empty_with_text() -> None:
    assert not TraySlot(text="hello").is_empty()


def test_preview_empty_slot() -> None:
    assert TraySlot().preview() == "(empty)"


def test_preview_short_text() -> None:
    slot = TraySlot(text="hello world")
    assert slot.preview() == "hello world"


def test_preview_truncates_at_max_chars() -> None:
    slot = TraySlot(text="a" * 100)
    result = slot.preview(max_chars=10)
    assert result == "a" * 10 + "..."


def test_preview_flattens_whitespace() -> None:
    slot = TraySlot(text="line one\nline two")
    assert slot.preview() == "line one line two"


def test_display_label_no_label() -> None:
    assert TraySlot().display_label(3) == "Slot 3"


def test_display_label_with_label() -> None:
    slot = TraySlot(label="research")
    assert slot.display_label(5) == "Slot 5: research"


# ---------------------------------------------------------------------------
# CopyTray round-trips
# ---------------------------------------------------------------------------


def test_copy_to_and_paste_from_all_slots(tmp_path: Path) -> None:
    tray = CopyTray(tmp_path)
    for n in range(1, 13):
        tray.copy_to(n, f"content {n}")
    for n in range(1, 13):
        assert tray.paste_from(n) == f"content {n}"


def test_set_label_persists(tmp_path: Path) -> None:
    tray = CopyTray(tmp_path)
    tray.copy_to(1, "some text")
    tray.set_label(1, "my label")
    assert tray.slot(1).label == "my label"


def test_clear_slot_empties_one_without_affecting_others(tmp_path: Path) -> None:
    tray = CopyTray(tmp_path)
    tray.copy_to(1, "alpha")
    tray.copy_to(2, "beta")
    tray.copy_to(3, "gamma")
    tray.clear_slot(2)
    assert tray.paste_from(1) == "alpha"
    assert tray.paste_from(2) == ""
    assert tray.paste_from(3) == "gamma"


def test_clear_all_empties_every_slot(tmp_path: Path) -> None:
    tray = CopyTray(tmp_path)
    for n in range(1, 13):
        tray.copy_to(n, f"data {n}")
    tray.clear_all()
    for n in range(1, 13):
        assert tray.paste_from(n) == ""
        assert tray.slot(n).is_empty()


# ---------------------------------------------------------------------------
# Boundary checks
# ---------------------------------------------------------------------------


def test_slot_0_raises_value_error(tmp_path: Path) -> None:
    tray = CopyTray(tmp_path)
    with pytest.raises(ValueError):
        tray.copy_to(0, "x")


def test_slot_13_raises_value_error(tmp_path: Path) -> None:
    tray = CopyTray(tmp_path)
    with pytest.raises(ValueError):
        tray.copy_to(13, "x")


def test_slot_1_is_valid(tmp_path: Path) -> None:
    tray = CopyTray(tmp_path)
    tray.copy_to(1, "first")
    assert tray.paste_from(1) == "first"


def test_slot_12_is_valid(tmp_path: Path) -> None:
    tray = CopyTray(tmp_path)
    tray.copy_to(12, "last")
    assert tray.paste_from(12) == "last"


# ---------------------------------------------------------------------------
# Persistence across instances
# ---------------------------------------------------------------------------


def test_data_survives_across_instances(tmp_path: Path) -> None:
    tray1 = CopyTray(tmp_path)
    tray1.copy_to(4, "persisted text")
    tray1.set_label(4, "important")

    tray2 = CopyTray(tmp_path)
    assert tray2.paste_from(4) == "persisted text"
    assert tray2.slot(4).label == "important"


def test_empty_slots_survive_across_instances(tmp_path: Path) -> None:
    tray1 = CopyTray(tmp_path)
    tray1.copy_to(1, "only slot 1")

    tray2 = CopyTray(tmp_path)
    assert tray2.paste_from(1) == "only slot 1"
    for n in range(2, 13):
        assert tray2.paste_from(n) == ""


# ---------------------------------------------------------------------------
# Corrupt JSON — must not raise
# ---------------------------------------------------------------------------


def test_corrupt_json_starts_fresh(tmp_path: Path) -> None:
    bad_file = tmp_path / "copy_tray.json"
    bad_file.write_text("not valid json at all }{", encoding="utf-8")
    tray = CopyTray(tmp_path)  # must not raise
    for n in range(1, 13):
        assert tray.slot(n).is_empty()


def test_truncated_slots_array_handled(tmp_path: Path) -> None:
    # File has only 3 slots — remaining 6 must be empty, no exception.
    bad_data = {
        "version": 1,
        "slots": [
            {"text": "a", "label": "", "copied_at": ""},
            {"text": "b", "label": "", "copied_at": ""},
            {"text": "c", "label": "", "copied_at": ""},
        ],
    }
    (tmp_path / "copy_tray.json").write_text(json.dumps(bad_data), encoding="utf-8")
    tray = CopyTray(tmp_path)
    assert tray.paste_from(1) == "a"
    assert tray.paste_from(2) == "b"
    assert tray.paste_from(3) == "c"
    for n in range(4, 13):
        assert tray.paste_from(n) == ""


# ---------------------------------------------------------------------------
# all_slots helper
# ---------------------------------------------------------------------------


def test_all_slots_returns_twelve_tuples(tmp_path: Path) -> None:
    tray = CopyTray(tmp_path)
    slots = tray.all_slots()
    assert len(slots) == 12
    assert [n for n, _ in slots] == list(range(1, 13))


# ---------------------------------------------------------------------------
# Pinned slots
# ---------------------------------------------------------------------------


def test_pin_slot_sets_pinned_flag(tmp_path: Path) -> None:
    tray = CopyTray(tmp_path)
    tray.copy_to(3, "important")
    tray.pin_slot(3)
    assert tray.slot(3).pinned is True


def test_unpin_slot_clears_pinned_flag(tmp_path: Path) -> None:
    tray = CopyTray(tmp_path)
    tray.copy_to(3, "important")
    tray.pin_slot(3)
    tray.unpin_slot(3)
    assert tray.slot(3).pinned is False


def test_pinned_flag_persists_across_instances(tmp_path: Path) -> None:
    tray1 = CopyTray(tmp_path)
    tray1.copy_to(2, "pinned content")
    tray1.pin_slot(2)

    tray2 = CopyTray(tmp_path)
    assert tray2.slot(2).pinned is True


# ---------------------------------------------------------------------------
# first_empty_slot
# ---------------------------------------------------------------------------


def test_first_empty_slot_returns_one_when_all_empty(tmp_path: Path) -> None:
    tray = CopyTray(tmp_path)
    assert tray.first_empty_slot() == 1


def test_first_empty_slot_skips_occupied(tmp_path: Path) -> None:
    tray = CopyTray(tmp_path)
    tray.copy_to(1, "a")
    tray.copy_to(2, "b")
    assert tray.first_empty_slot() == 3


def test_first_empty_slot_skips_pinned(tmp_path: Path) -> None:
    tray = CopyTray(tmp_path)
    tray.pin_slot(1)  # pinned but empty — still skipped
    assert tray.first_empty_slot() == 2


def test_first_empty_slot_returns_none_when_all_occupied_or_pinned(tmp_path: Path) -> None:
    tray = CopyTray(tmp_path)
    for n in range(1, 13):
        tray.copy_to(n, f"data {n}")
    assert tray.first_empty_slot() is None


# ---------------------------------------------------------------------------
# search_slots
# ---------------------------------------------------------------------------


def test_search_slots_finds_by_text(tmp_path: Path) -> None:
    tray = CopyTray(tmp_path)
    tray.copy_to(1, "the quick brown fox")
    tray.copy_to(2, "lazy dog")
    results = tray.search_slots("quick")
    assert len(results) == 1
    assert results[0][0] == 1


def test_search_slots_finds_by_label(tmp_path: Path) -> None:
    tray = CopyTray(tmp_path)
    tray.copy_to(5, "some content")
    tray.set_label(5, "contract clause")
    results = tray.search_slots("contract")
    assert len(results) == 1
    assert results[0][0] == 5


def test_search_slots_case_insensitive(tmp_path: Path) -> None:
    tray = CopyTray(tmp_path)
    tray.copy_to(1, "The Agreement is")
    results = tray.search_slots("agreement")
    assert len(results) == 1


def test_search_slots_empty_slot_excluded(tmp_path: Path) -> None:
    tray = CopyTray(tmp_path)
    tray.copy_to(1, "hello")
    results = tray.search_slots("hello")
    assert len(results) == 1
    tray.clear_slot(1)
    results = tray.search_slots("hello")
    assert len(results) == 0


def test_search_slots_no_match_returns_empty(tmp_path: Path) -> None:
    tray = CopyTray(tmp_path)
    tray.copy_to(1, "unrelated content")
    assert tray.search_slots("nomatch") == []
