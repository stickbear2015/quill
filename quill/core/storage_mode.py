from __future__ import annotations

import os
from pathlib import Path

from quill.core.storage import read_json, write_json_atomic

_VALID_MODES = {"appdata", "portable"}

# L-9: ``QUILL_PORTABLE_ROOT`` is documented as a *dev-only* override. In
# release builds we ignore it entirely, matching the H-1-core treatment of
# ``QUILL_DATA_DIR``: a tampered environment cannot redirect the user's
# portable installation to an attacker-controlled directory. Development
# builds (CI, local testing) opt in by exporting ``QUILL_DEV_BUILD=1`` in
# the environment, or by setting the module-private ``_DEV_BUILD`` flag
# below to ``True``.
_DEV_BUILD = os.environ.get("QUILL_DEV_BUILD") == "1" or False  # dev override opt-in


def portable_root_dir() -> Path | None:
    override = os.environ.get("QUILL_PORTABLE_ROOT")
    if not override:
        return None
    if not _DEV_BUILD:
        # Release build: ignore the env var entirely.
        return None
    return Path(override).expanduser().resolve()


def storage_mode_path() -> Path | None:
    paths = storage_mode_paths()
    if not paths:
        return None
    return paths[0]


def storage_mode_paths() -> tuple[Path, ...]:
    root = portable_root_dir()
    if root is None:
        return ()
    portable_path = root / "storage-mode.json"
    fallback_path = _fallback_storage_mode_path()
    if _portable_path_is_writable(portable_path):
        return (portable_path, fallback_path)
    return (fallback_path, portable_path)


def _fallback_storage_mode_path() -> Path:
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata).expanduser().resolve() / "Quill" / "storage-mode.json"
    return Path.home() / ".quill" / "storage-mode.json"


def _portable_path_is_writable(path: Path) -> bool:
    candidate = path if path.exists() else path.parent
    while not candidate.exists() and candidate != candidate.parent:
        candidate = candidate.parent
    return os.access(candidate, os.W_OK)


def load_storage_mode() -> str | None:
    for path in storage_mode_paths():
        if not path.exists():
            continue
        raw = read_json(path, default={})
        if not isinstance(raw, dict):
            continue
        mode = raw.get("mode")
        if isinstance(mode, str) and mode in _VALID_MODES:
            return mode
    return None


def save_storage_mode(mode: str) -> None:
    if mode not in _VALID_MODES:
        raise ValueError(f"Unknown storage mode: {mode}")
    paths = storage_mode_paths()
    if not paths:
        raise RuntimeError("Portable root is not configured")
    last_error: PermissionError | None = None
    for path in paths:
        try:
            write_json_atomic(path, {"mode": mode})
            return
        except PermissionError as error:
            last_error = error
    assert last_error is not None
    raise last_error
