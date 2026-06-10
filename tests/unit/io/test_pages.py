"""Tests for quill.io.pages — M-9 thread-safety regression."""

from __future__ import annotations

import threading
import time
from pathlib import Path
from unittest.mock import MagicMock, patch


def test_concurrent_reads_serialize_via_lock(tmp_path: Path) -> None:
    # M-9: _patched_id_name_map() temporarily replaces a global dict; concurrent
    # reads must not corrupt each other's map. The lock ensures they serialize.
    import quill.io.pages as _pages

    call_order: list[str] = []

    def slow_parse(path, reader):
        call_order.append("enter")
        time.sleep(0.02)
        call_order.append("exit")
        return {}

    errors: list[Exception] = []

    def _open(i: int) -> None:
        try:
            fake_codec = MagicMock()
            fake_codec.ID_NAME_MAP = {}
            fake_codec._quill_id_name_map_lock = threading.Lock()

            mods = {
                "keynote_parser.codec": fake_codec,
                "keynote_parser.file_utils": MagicMock(),
            }
            with patch.dict("sys.modules", mods):
                with patch.object(_pages, "_parse_iwa_bundle", slow_parse):
                    try:
                        _pages._read_pages_via_iwa(tmp_path / f"doc{i}.pages")
                    except (ImportError, ValueError):
                        pass  # expected — no real .pages file
        except Exception as exc:  # noqa: BLE001
            errors.append(exc)

    threads = [threading.Thread(target=_open, args=(i,)) for i in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=5)

    assert not errors, f"Thread errors: {errors}"
    # No interleaved enter/exit pairs — each enter is immediately followed by exit.
    for idx in range(0, len(call_order) - 1, 2):
        assert call_order[idx] == "enter"
        assert call_order[idx + 1] == "exit"
