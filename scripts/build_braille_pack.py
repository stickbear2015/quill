"""Build a signed-ready QUILL Braille Pack archive (BR-020 deployment).

This is the deterministic half of braille-pack deployment: given a directory of
already-vendored liblouis runtime files and tables, it writes a ``manifest.json``
(pack version, liblouis version, per-file SHA-256) and zips everything into
``quill-braille-pack-<version>-<platform>.zip``, then prints the archive's
SHA-256 so it can be pinned in QUILL's ``install_braille_pack`` and published as a
GitHub release asset.

Vendoring liblouis itself (downloading a pinned upstream build + the UEB tables
into the input directory) is a separate, audited step described in
``docs/braille.md``; this script never touches the network.

Usage::

    python scripts/build_braille_pack.py \
        --input vendor/braille-pack \
        --version 1.0.0 \
        --liblouis 3.30.0 \
        --platform win64 \
        --out dist

The input directory is expected to contain the runtime (e.g. ``lou_translate.exe``
or ``liblouis.dll``), a ``tables/`` directory, and the upstream ``LICENSE`` files.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

MANIFEST_NAME = "manifest.json"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _pack_files(input_dir: Path) -> list[Path]:
    return sorted(p for p in input_dir.rglob("*") if p.is_file() and p.name != MANIFEST_NAME)


def build_manifest(
    input_dir: Path, *, version: str, liblouis_version: str, platform: str
) -> dict[str, object]:
    """Return the pack manifest: version metadata plus per-file SHA-256."""
    files = {
        p.relative_to(input_dir).as_posix(): {"sha256": _sha256(p), "bytes": p.stat().st_size}
        for p in _pack_files(input_dir)
    }
    return {
        "pack": "quill-braille-pack",
        "version": version,
        "liblouis_version": liblouis_version,
        "platform": platform,
        "files": files,
    }


def build_pack(
    input_dir: Path,
    out_dir: Path,
    *,
    version: str,
    liblouis_version: str,
    platform: str,
) -> tuple[Path, str]:
    """Write the manifest, zip the pack, and return ``(archive_path, sha256)``."""
    if not input_dir.is_dir():
        raise SystemExit(f"input directory not found: {input_dir}")
    manifest = build_manifest(
        input_dir, version=version, liblouis_version=liblouis_version, platform=platform
    )
    (input_dir / MANIFEST_NAME).write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    archive = out_dir / f"quill-braille-pack-{version}-{platform}.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(input_dir / MANIFEST_NAME, MANIFEST_NAME)
        for path in _pack_files(input_dir):
            zf.write(path, path.relative_to(input_dir).as_posix())
    return archive, _sha256(archive)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a QUILL Braille Pack archive.")
    parser.add_argument("--input", required=True, type=Path, help="vendored pack directory")
    parser.add_argument("--version", required=True, help="pack version, e.g. 1.0.0")
    parser.add_argument("--liblouis", required=True, help="bundled liblouis version")
    parser.add_argument(
        "--platform", required=True, help="platform tag, e.g. win64 / macos / linux"
    )
    parser.add_argument("--out", type=Path, default=Path("dist"), help="output directory")
    args = parser.parse_args(argv)

    archive, sha = build_pack(
        args.input,
        args.out,
        version=args.version,
        liblouis_version=args.liblouis,
        platform=args.platform,
    )
    print(f"Built {archive}")
    print(f"SHA-256 {sha}")
    print("Pin this SHA-256 in quill.core.braille_pack and publish the archive as a release asset.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
