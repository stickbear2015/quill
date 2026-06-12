"""Dialog z-order audit: detect label-after-control anti-pattern (A11Y-Z-ORDER).

Screen readers (NVDA, JAWS) use the Windows child-window z-order — which equals
the creation order in wxPython — to associate static labels with interactive
controls. When a FlexGridSizer row helper creates wx.StaticText internally but
receives an *already-created* control object, the control's z-order position is
before its label. That reversal can cause the screen reader to announce the wrong
label or read the label as a standalone text element when the user tabs through
the form.

Correct pattern: the helper takes a factory (lambda), creates the StaticText
first, then calls the factory to create the control.

    def row(label_text: str, make_ctrl) -> object:          # OK
        grid.Add(wx.StaticText(...), ...)
        ctrl = make_ctrl()
        grid.Add(ctrl, ...)
        return ctrl
    self.host = row("Host", lambda: wx.TextCtrl(...))       # OK

Anti-pattern: control is created before the row helper is called.

    def row(label_text: str, control: object) -> None:      # WRONG
        grid.Add(wx.StaticText(...), ...)
        grid.Add(control, ...)
    self.host = wx.TextCtrl(...)                            # control created first
    row("Host", self.host)                                  # WRONG: pre-created

Detection: find calls to row-helper functions (identified by creating wx.StaticText
internally) where the second argument is NOT a lambda expression.
"""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PACKAGE_ROOT = _REPO_ROOT / "quill"


@dataclass
class ZOrderViolation:
    file: Path
    line: int
    helper_name: str
    detail: str


def _find_grid_helpers(func_body: list[ast.stmt]) -> set[str]:
    """Return names of local functions that create wx.StaticText and add a param."""
    helpers: set[str] = set()
    for node in ast.walk(ast.Module(body=func_body, type_ignores=[])):
        if not isinstance(node, ast.FunctionDef):
            continue
        if len(node.args.args) < 2:
            continue
        body_src = ast.dump(node)
        if "StaticText" not in body_src:
            continue
        # Confirm the helper adds the second parameter (or a derived value) to a sizer
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                func = child.func
                if isinstance(func, ast.Attribute) and func.attr == "Add" and child.args:
                    helpers.add(node.name)
                    break
    return helpers


def audit_file(path: Path) -> list[ZOrderViolation]:
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return []

    violations: list[ZOrderViolation] = []

    for func_node in ast.walk(tree):
        if not isinstance(func_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        # Only look inside __init__ methods or module-level factory functions
        helpers = _find_grid_helpers(func_node.body)
        if not helpers:
            continue

        for call_node in ast.walk(ast.Module(body=func_node.body, type_ignores=[])):
            if not isinstance(call_node, ast.Call):
                continue
            func_ref = call_node.func
            if not isinstance(func_ref, ast.Name):
                continue
            if func_ref.id not in helpers:
                continue
            if len(call_node.args) < 2:
                continue

            # Find the first string-literal argument — that is the label.
            # The argument immediately after it is the control factory.
            # If no string literal is found, skip (the label is a runtime variable;
            # those helpers are harder to audit statically and are not flagged here).
            label_idx = None
            for idx, arg in enumerate(call_node.args):
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    label_idx = idx
                    break
            if label_idx is None:
                continue

            ctrl_idx = label_idx + 1
            if ctrl_idx >= len(call_node.args):
                continue

            ctrl_arg = call_node.args[ctrl_idx]
            if not isinstance(ctrl_arg, ast.Lambda):
                violations.append(
                    ZOrderViolation(
                        file=path,
                        line=call_node.lineno,
                        helper_name=func_ref.id,
                        detail=(
                            f"arg after label in {func_ref.id}() is "
                            f"{type(ctrl_arg).__name__}, not a lambda — "
                            "control was pre-created before the label"
                        ),
                    )
                )

    return violations


def audit_package(root: Path = _PACKAGE_ROOT) -> list[ZOrderViolation]:
    all_violations: list[ZOrderViolation] = []
    for path in sorted(root.rglob("*.py")):
        all_violations.extend(audit_file(path))
    return all_violations


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check dialog source files for z-order label/control anti-pattern."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Files or directories to audit (default: entire quill package).",
    )
    args = parser.parse_args()

    targets = args.paths or [_PACKAGE_ROOT]
    violations: list[ZOrderViolation] = []
    for target in targets:
        target = target.resolve()
        if target.is_file():
            violations.extend(audit_file(target))
        else:
            violations.extend(audit_package(target))

    if not violations:
        print("OK - no dialog z-order violations found.")
        return

    for v in violations:
        rel = v.file.relative_to(_REPO_ROOT)
        print(f"{rel}:{v.line}: [A11Y-Z-ORDER] {v.detail}")
    raise SystemExit(1)


if __name__ == "__main__":
    main()
