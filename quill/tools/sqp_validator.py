"""Skill Quill Pack (.sqp) format validator.

Usage::

    python -m quill.tools.sqp_validator path/to/skill.sqp
    python -m quill.tools.sqp_validator path/to/directory/
    python -m quill.tools.sqp_validator path/to/skill.sqp --strict

Exit codes:
    0  All files valid (or no .sqp files found when scanning a directory).
    1  One or more validation errors.
    2  File/directory not found or unreadable.

``--strict`` also reports warnings (unknown parameters, missing description,
missing author).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from quill.core.skill_pack import SkillValidationError, parse_skill, validate_skill


def _validate_file(path: Path, strict: bool) -> list[str]:
    """Return a list of error/warning strings for the given .sqp file."""
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"cannot read: {exc}"]

    try:
        pack = parse_skill(source)
    except SkillValidationError as exc:
        return [f"parse error: {e}" for e in exc.errors]

    errors = validate_skill(pack)

    if strict:
        if not pack.description:
            errors.append("warning: no description in front matter")
        if not pack.author:
            errors.append("warning: no author in front matter")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m quill.tools.sqp_validator",
        description="Validate .sqp (Skill Quill Pack) files.",
    )
    parser.add_argument("path", help="Path to a .sqp file or a directory to scan recursively.")
    parser.add_argument("--strict", action="store_true", help="Also report warnings.")
    args = parser.parse_args(argv)

    target = Path(args.path)
    if not target.exists():
        print(f"Error: '{target}' not found.", file=sys.stderr)
        return 2

    if target.is_dir():
        files = sorted(target.rglob("*.sqp"))
        if not files:
            print("No .sqp files found.")
            return 0
    else:
        files = [target]

    any_errors = False
    for f in files:
        issues = _validate_file(f, args.strict)
        if issues:
            any_errors = True
            print(f"{f}: {len(issues)} issue{'s' if len(issues) != 1 else ''}")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print(f"{f}: OK")

    return 1 if any_errors else 0


if __name__ == "__main__":
    sys.exit(main())
