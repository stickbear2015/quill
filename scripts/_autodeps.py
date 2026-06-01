"""Reinstall Quill's requirements only when requirements.txt has changed.

Called by run-from-source.bat / run-from-source.sh with the repo root as
argv[1] (defaults to the current directory). It hashes requirements.txt,
compares to ``.quill-reqs.sha256``, and runs
``<this-python> -m pip install -r requirements.txt`` when they differ —
writing the new hash only after a successful install.

All of the logic lives here, in Python, on purpose: doing the hashing/compare
inline in cmd.exe meant the parentheses in ``open(...).read()`` were parsed as
batch block delimiters, which crashed run-from-source.bat with
``.read( was unexpected at this time.`` A single ``python script.py`` call has
nothing for cmd (or bash) to mis-quote.

Set QUILL_NO_AUTO_DEPS=1 to skip the check entirely. Always exits 0 so a
dependency hiccup never blocks launching Quill with the existing environment.
"""

import hashlib
import os
import subprocess
import sys


def main() -> int:
    if os.environ.get("QUILL_NO_AUTO_DEPS"):
        return 0

    root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    requirements = os.path.join(root, "requirements.txt")
    stamp = os.path.join(root, ".quill-reqs.sha256")
    if not os.path.isfile(requirements):
        return 0

    with open(requirements, "rb") as handle:
        new_hash = hashlib.sha256(handle.read()).hexdigest()

    old_hash = ""
    try:
        with open(stamp, encoding="utf-8") as handle:
            old_hash = handle.read().strip()
    except OSError:
        pass

    if new_hash == old_hash:
        return 0

    print("Requirements changed - installing dependencies...", flush=True)
    result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements])
    if result.returncode == 0:
        try:
            with open(stamp, "w", encoding="utf-8") as handle:
                handle.write(new_hash)
        except OSError:
            pass
    else:
        print(
            "Dependency install failed; launching with the existing environment.",
            file=sys.stderr,
            flush=True,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
