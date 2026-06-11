"""Tests for quill.core.notebook_store (Milestone 2 data layer)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from quill.core.notebook_store import (
    Notebook,
    NotebookEntry,
    NotebookFormatError,
    NotebookGoal,
    NotebookSnapshot,
    SavedSearch,
    create_notebook,
    create_notebook_from_folder,
    load_notebook,
    save_notebook,
)

# ---------------------------------------------------------------------------
# NotebookEntry
# ---------------------------------------------------------------------------


def test_entry_create_generates_uuid_and_path() -> None:
    e = NotebookEntry.create("chapter1.md", title="Chapter 1")
    assert e.path == "chapter1.md"
    assert e.title == "Chapter 1"
    assert len(e.id) == 36  # UUID4 canonical form


def test_entry_create_unique_ids() -> None:
    a = NotebookEntry.create("a.md")
    b = NotebookEntry.create("b.md")
    assert a.id != b.id


def test_entry_round_trip() -> None:
    e = NotebookEntry.create("docs/intro.md", title="Intro")
    e.tags = ["draft", "featured"]
    e.last_caret_pos = 42
    e.word_count = 300
    restored = NotebookEntry.from_dict(e.to_dict())
    assert restored.id == e.id
    assert restored.path == e.path
    assert restored.title == e.title
    assert restored.tags == e.tags
    assert restored.last_caret_pos == 42
    assert restored.word_count == 300


def test_entry_from_dict_optional_defaults() -> None:
    data = {"id": "abc", "path": "file.txt"}
    e = NotebookEntry.from_dict(data)
    assert e.tags == []
    assert e.last_caret_pos == 0
    assert e.word_count is None
    assert e.title is None


# ---------------------------------------------------------------------------
# NotebookSnapshot
# ---------------------------------------------------------------------------


def test_snapshot_create_sets_timestamps() -> None:
    ids = ["id1", "id2"]
    snap = NotebookSnapshot.create("Morning session", ids, active_entry_id="id1")
    assert snap.name == "Morning session"
    assert snap.open_entry_ids == ids
    assert snap.active_entry_id == "id1"
    assert snap.created  # non-empty ISO timestamp


def test_snapshot_round_trip() -> None:
    snap = NotebookSnapshot.create("Draft review", ["e1", "e2"])
    restored = NotebookSnapshot.from_dict(snap.to_dict())
    assert restored.id == snap.id
    assert restored.name == snap.name
    assert restored.open_entry_ids == snap.open_entry_ids
    assert restored.created == snap.created


# ---------------------------------------------------------------------------
# NotebookGoal
# ---------------------------------------------------------------------------


def test_goal_defaults() -> None:
    g = NotebookGoal()
    assert g.enabled is False
    assert g.daily_target == 500
    assert g.unit == "words"
    assert g.today_count == 0


def test_goal_round_trip() -> None:
    g = NotebookGoal(
        enabled=True, daily_target=1000, unit="characters", today_count=250, today_date="2026-06-10"
    )
    restored = NotebookGoal.from_dict(g.to_dict())
    assert restored.enabled is True
    assert restored.daily_target == 1000
    assert restored.unit == "characters"
    assert restored.today_count == 250
    assert restored.today_date == "2026-06-10"


# ---------------------------------------------------------------------------
# SavedSearch
# ---------------------------------------------------------------------------


def test_saved_search_create() -> None:
    ss = SavedSearch.create("TODOs", "TODO:", is_regex=False)
    assert ss.name == "TODOs"
    assert ss.query == "TODO:"
    assert ss.is_regex is False


def test_saved_search_round_trip() -> None:
    ss = SavedSearch.create("Patterns", r"\b\w+ing\b", is_regex=True, case_sensitive=True)
    restored = SavedSearch.from_dict(ss.to_dict())
    assert restored.id == ss.id
    assert restored.is_regex is True
    assert restored.case_sensitive is True


# ---------------------------------------------------------------------------
# Notebook entry helpers
# ---------------------------------------------------------------------------


def test_notebook_add_entry_idempotent() -> None:
    nb = Notebook(name="Test")
    e1 = nb.add_entry("a.md", title="A")
    e2 = nb.add_entry("a.md", title="B")
    assert e1.id == e2.id
    assert len(nb.entries) == 1


def test_notebook_add_entry_appends_new() -> None:
    nb = Notebook(name="Test")
    nb.add_entry("a.md")
    nb.add_entry("b.md")
    assert len(nb.entries) == 2


def test_notebook_entry_by_id() -> None:
    nb = Notebook(name="Test")
    e = nb.add_entry("x.md")
    assert nb.entry_by_id(e.id) is e
    assert nb.entry_by_id("nonexistent") is None


def test_notebook_entry_by_path() -> None:
    nb = Notebook(name="Test")
    e = nb.add_entry("x.md")
    assert nb.entry_by_path("x.md") is e
    assert nb.entry_by_path("missing.md") is None


def test_notebook_remove_entry_returns_true_on_success() -> None:
    nb = Notebook(name="Test")
    e = nb.add_entry("a.md")
    assert nb.remove_entry(e.id) is True
    assert nb.entries == []


def test_notebook_remove_entry_returns_false_on_miss() -> None:
    nb = Notebook(name="Test")
    assert nb.remove_entry("no-such-id") is False


# ---------------------------------------------------------------------------
# Notebook snapshot helpers
# ---------------------------------------------------------------------------


def test_notebook_save_snapshot_appends() -> None:
    nb = Notebook(name="Test")
    e = nb.add_entry("doc.md")
    snap = nb.save_snapshot("Session 1", [e.id], e.id)
    assert len(nb.snapshots) == 1
    assert nb.snapshot_by_id(snap.id) is snap


def test_notebook_remove_snapshot() -> None:
    nb = Notebook(name="Test")
    snap = nb.save_snapshot("S1", [])
    assert nb.remove_snapshot(snap.id) is True
    assert nb.remove_snapshot(snap.id) is False


# ---------------------------------------------------------------------------
# Notebook serialisation
# ---------------------------------------------------------------------------


def test_notebook_to_dict_has_discriminator() -> None:
    nb = Notebook(name="My Novel")
    d = nb.to_dict()
    assert d["schema"] == "quill.notebook/1"
    assert d["name"] == "My Novel"


def test_notebook_from_dict_wrong_discriminator() -> None:
    bad = {"schema": "quill.notebook/99", "name": "X", "entries": []}
    with pytest.raises(NotebookFormatError, match="Unrecognised schema discriminator"):
        Notebook.from_dict(bad)


def test_notebook_round_trip_dict() -> None:
    nb = Notebook(name="Novel")
    nb.add_entry("ch1.md", title="Chapter 1")
    nb.save_snapshot("Draft", [nb.entries[0].id])
    nb.goal = NotebookGoal(enabled=True, daily_target=750)
    nb.vocabulary = ["weltanschauung"]
    nb.saved_searches.append(SavedSearch.create("Dialogue", '".*"'))
    restored = Notebook.from_dict(nb.to_dict())
    assert restored.name == "Novel"
    assert len(restored.entries) == 1
    assert restored.entries[0].title == "Chapter 1"
    assert len(restored.snapshots) == 1
    assert restored.goal.daily_target == 750
    assert restored.vocabulary == ["weltanschauung"]
    assert len(restored.saved_searches) == 1


# ---------------------------------------------------------------------------
# Store functions: create / save / load
# ---------------------------------------------------------------------------


def test_create_notebook_writes_file(tmp_path: Path) -> None:
    nb_path = tmp_path / "my.quillnotebook"
    nb = create_notebook("Novel", path=nb_path)
    assert nb_path.exists()
    assert nb.path == nb_path
    assert nb.name == "Novel"


def test_save_and_load_round_trip(tmp_path: Path) -> None:
    nb_path = tmp_path / "round_trip.quillnotebook"
    nb = Notebook(name="Draft")
    nb.add_entry("intro.md", title="Introduction")
    nb.vocabulary = ["quillnotebook"]
    save_notebook(nb, nb_path)
    assert nb.path == nb_path

    loaded = load_notebook(nb_path)
    assert loaded.name == "Draft"
    assert loaded.path == nb_path
    assert len(loaded.entries) == 1
    assert loaded.entries[0].title == "Introduction"
    assert loaded.vocabulary == ["quillnotebook"]


def test_load_notebook_bad_json(tmp_path: Path) -> None:
    nb_path = tmp_path / "bad.quillnotebook"
    nb_path.write_text("not json", encoding="utf-8")
    with pytest.raises(NotebookFormatError):
        load_notebook(nb_path)


def test_load_notebook_wrong_discriminator(tmp_path: Path) -> None:
    nb_path = tmp_path / "wrong.quillnotebook"
    nb_path.write_text(
        json.dumps({"schema": "quill.notebook/0", "name": "X", "entries": []}),
        encoding="utf-8",
    )
    with pytest.raises(NotebookFormatError):
        load_notebook(nb_path)


def test_load_notebook_missing_file(tmp_path: Path) -> None:
    nb_path = tmp_path / "missing.quillnotebook"
    with pytest.raises(OSError):
        load_notebook(nb_path)


def test_load_notebook_non_object_json(tmp_path: Path) -> None:
    nb_path = tmp_path / "array.quillnotebook"
    nb_path.write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(NotebookFormatError):
        load_notebook(nb_path)


# ---------------------------------------------------------------------------
# create_notebook_from_folder
# ---------------------------------------------------------------------------


def test_create_from_folder_finds_md_files(tmp_path: Path) -> None:
    folder = tmp_path / "project"
    folder.mkdir()
    (folder / "chapter1.md").write_text("# Chapter 1", encoding="utf-8")
    (folder / "chapter2.md").write_text("# Chapter 2", encoding="utf-8")
    (folder / "notes.txt").write_text("notes", encoding="utf-8")
    (folder / "image.png").write_bytes(b"\x89PNG")

    nb_path = tmp_path / "project.quillnotebook"
    nb = create_notebook_from_folder(folder, path=nb_path)

    paths = {e.path for e in nb.entries}
    assert "chapter1.md" in paths
    assert "chapter2.md" in paths
    assert "notes.txt" in paths
    assert not any("png" in p for p in paths)


def test_create_from_folder_excludes_non_matching_extensions(tmp_path: Path) -> None:
    folder = tmp_path / "proj"
    folder.mkdir()
    (folder / "a.md").write_text("a", encoding="utf-8")
    (folder / "b.rst").write_text("b", encoding="utf-8")
    (folder / "c.docx").write_bytes(b"PK")

    nb_path = tmp_path / "proj.quillnotebook"
    nb = create_notebook_from_folder(folder, path=nb_path, extensions=(".md",))

    assert len(nb.entries) == 1
    assert nb.entries[0].path == "a.md"


def test_create_from_folder_uses_folder_name_by_default(tmp_path: Path) -> None:
    folder = tmp_path / "my_novel"
    folder.mkdir()
    nb_path = tmp_path / "nb.quillnotebook"
    nb = create_notebook_from_folder(folder, path=nb_path)
    assert nb.name == "my_novel"


def test_create_from_folder_custom_name(tmp_path: Path) -> None:
    folder = tmp_path / "src"
    folder.mkdir()
    nb_path = tmp_path / "nb.quillnotebook"
    nb = create_notebook_from_folder(folder, path=nb_path, name="Custom Name")
    assert nb.name == "Custom Name"


def test_create_from_folder_sets_root_dir(tmp_path: Path) -> None:
    folder = tmp_path / "docs"
    folder.mkdir()
    nb_path = tmp_path / "nb.quillnotebook"
    nb = create_notebook_from_folder(folder, path=nb_path)
    assert nb.root_dir == str(folder)


def test_create_from_folder_recursive(tmp_path: Path) -> None:
    folder = tmp_path / "book"
    sub = folder / "part1"
    sub.mkdir(parents=True)
    (folder / "intro.md").write_text("Intro", encoding="utf-8")
    (sub / "chapter1.md").write_text("Ch1", encoding="utf-8")

    nb_path = tmp_path / "book.quillnotebook"
    nb = create_notebook_from_folder(folder, path=nb_path)

    paths = {e.path for e in nb.entries}
    assert "intro.md" in paths
    assert str(Path("part1") / "chapter1.md") in paths


def test_create_from_folder_title_derived_from_filename(tmp_path: Path) -> None:
    folder = tmp_path / "novel"
    folder.mkdir()
    (folder / "my-first-chapter.md").write_text("x", encoding="utf-8")

    nb_path = tmp_path / "n.quillnotebook"
    nb = create_notebook_from_folder(folder, path=nb_path)

    assert nb.entries[0].title == "My First Chapter"
