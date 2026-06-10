from __future__ import annotations

from pathlib import Path

import pytest

from quill.core import storage_mode
from quill.core.paths import app_data_dir
from quill.core.storage_mode import load_storage_mode, save_storage_mode


@pytest.fixture(autouse=True)
def _enable_dev_build(monkeypatch: pytest.MonkeyPatch) -> None:
    """L-9: portable-root tests run with the dev-override flag on."""
    monkeypatch.setattr(storage_mode, "_DEV_BUILD", True)


def test_storage_mode_uses_portable_root(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("QUILL_PORTABLE_ROOT", str(tmp_path / "portable"))
    assert load_storage_mode() is None

    save_storage_mode("portable")

    assert load_storage_mode() == "portable"
    assert app_data_dir() == (tmp_path / "portable").resolve()


def test_storage_mode_can_prefer_appdata(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("QUILL_PORTABLE_ROOT", str(tmp_path / "portable"))
    monkeypatch.setenv("APPDATA", str(tmp_path / "appdata"))
    save_storage_mode("appdata")

    assert load_storage_mode() == "appdata"
    assert app_data_dir() == (tmp_path / "appdata" / "Quill").resolve()


def test_release_build_ignores_quill_portable_root(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """L-9: a release build ignores QUILL_PORTABLE_ROOT entirely."""
    monkeypatch.setattr(storage_mode, "_DEV_BUILD", False)
    monkeypatch.setenv("QUILL_PORTABLE_ROOT", str(tmp_path / "portable"))
    monkeypatch.delenv("APPDATA", raising=False)
    assert storage_mode.portable_root_dir() is None
    assert load_storage_mode() is None


def test_dev_build_honours_quill_portable_root(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """L-9: a dev build honours QUILL_PORTABLE_ROOT when _DEV_BUILD is on."""
    monkeypatch.setenv("QUILL_PORTABLE_ROOT", str(tmp_path / "portable"))
    resolved = storage_mode.portable_root_dir()
    assert resolved == (tmp_path / "portable").resolve()


def test_storage_mode_falls_back_when_portable_path_is_not_writable(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("QUILL_PORTABLE_ROOT", str(tmp_path / "portable"))
    monkeypatch.setenv("APPDATA", str(tmp_path / "appdata"))
    monkeypatch.setattr("quill.core.storage_mode.os.access", lambda *_args: False)

    save_storage_mode("appdata")

    fallback_path = tmp_path / "appdata" / "Quill" / "storage-mode.json"
    assert fallback_path.exists()
    assert not (tmp_path / "portable" / "storage-mode.json").exists()
    assert load_storage_mode() == "appdata"

    stale_portable_path = tmp_path / "portable" / "storage-mode.json"
    stale_portable_path.parent.mkdir(parents=True, exist_ok=True)
    stale_portable_path.write_text('{"mode":"portable"}', encoding="utf-8")
    assert load_storage_mode() == "appdata"
