#!/usr/bin/env python3
"""Build a reproducible, skills-only plugin archive from the public source."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import zipfile


def build(root: Path, output: Path | None = None) -> dict:
    manifest = json.loads((root / "plugin.json").read_text(encoding="utf-8"))
    name, version = manifest["name"], manifest["version"]
    output = output or root / ".local/dist" / f"{name}-{version}.zip"
    files = [root / "plugin.json", root / "LICENSE", root / "THIRD_PARTY_NOTICES.md"]
    for directory in (root / "skills", root / "provenance"):
        if directory.is_symlink():
            raise ValueError("Refusing a linked package directory")
        for path in sorted(directory.rglob("*")):
            if path.is_symlink():
                raise ValueError(f"Refusing a symbolic link: {path.relative_to(root)}")
            if path.is_file():
                relative = path.relative_to(root)
                if any(p.startswith(".") or p == "__pycache__" for p in relative.parts):
                    raise ValueError(f"Unexpected private/generated file: {relative}")
                files.append(path)
    skills = sorted(p.parent.name for p in (root / "skills").glob("*/SKILL.md"))
    if len(skills) != 9:
        raise ValueError(f"Expected nine packaged skills, found {len(skills)}")
    if output.resolve() in [p.resolve() for p in files]:
        raise ValueError("Output must not overwrite source")
    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=".pla-plugin-", suffix=".zip.tmp", dir=output.parent,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w+b") as stream:
            with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                for path in sorted(files):
                    if not path.is_file() or path.is_symlink():
                        raise ValueError(f"Invalid package source: {path.name}")
                    info = zipfile.ZipInfo(name + "/" + path.relative_to(root).as_posix(), (1980, 1, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = 0o100644 << 16
                    archive.writestr(info, path.read_bytes())
            stream.seek(0)
            with zipfile.ZipFile(stream) as archive:
                if archive.testzip() is not None:
                    raise ValueError("Archive integrity check failed")
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)
    return {"ok": True, "archive": str(output), "skills": skills,
            "files": len(files), "sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
            "installed": False, "service_connection": "recipient-specific"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = build(Path(__file__).resolve().parents[1], args.output)
    except (OSError, ValueError, KeyError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
