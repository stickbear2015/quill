"""Notebook tab helpers for the Document Navigator (§10.4 Milestone 2).

``_NotebookNode`` is a duck-type–compatible stand-in for the private
``_NavigatorNode`` dataclass in ``main_frame.py``.  Both share the same five
attribute names so ``_show_tree_navigator`` accepts either without knowing the
concrete type.  Importing ``_NavigatorNode`` from ``main_frame`` would create a
circular dependency; the duck-type approach avoids that entirely.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class _NotebookNode:
    label: str
    preview: str
    payload: object
    action_label: str
    children: list[_NotebookNode] = field(default_factory=list)


def build_notebook_nodes(notebook: object) -> list[_NotebookNode]:
    """Convert *notebook* entries into a two-level tree for the navigator.

    Top-level nodes represent directories (groups); leaf nodes represent
    individual entries.  Files in the root directory form a synthetic
    ``"(root)"`` group when mixed with subdirectory entries; if all entries
    are flat the root group is omitted and entries appear directly.
    """
    entries = list(getattr(notebook, "entries", []))
    if not entries:
        return []

    # Group entries by their parent directory path.
    groups: dict[str, list[object]] = {}
    for entry in entries:
        path_str = getattr(entry, "path", "")
        parent = str(Path(path_str).parent)
        groups.setdefault(parent, []).append(entry)

    all_flat = set(groups.keys()) == {"."}

    nodes: list[_NotebookNode] = []

    for group_key, group_entries in sorted(groups.items()):
        group_label = "(root)" if group_key == "." else group_key
        children = [
            _NotebookNode(
                label=getattr(e, "title", None) or getattr(e, "path", ""),
                preview=getattr(e, "path", ""),
                payload=e,
                action_label="Open Entry",
                children=[],
            )
            for e in group_entries
        ]
        if all_flat:
            nodes.extend(children)
        else:
            nodes.append(
                _NotebookNode(
                    label=group_label,
                    preview=f"{len(children)} entries",
                    payload=group_entries[0],
                    action_label="Open Entry",
                    children=children,
                )
            )

    return nodes
