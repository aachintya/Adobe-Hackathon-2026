#!/usr/bin/env python3
"""Build and verify the standalone audit ZIP."""

from __future__ import annotations

import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = "brand-ai-readiness-audit"
# These two validators are runtime dependencies of the report finalizer.
# Development tests, evaluations and change history stay in the repository.
INCLUDED_FILES = ("marketplace.json", "README.md", "LICENSE",
                  "tests/validate_report.py", "tests/report_evidence.py")
INCLUDED_DIRECTORIES = ("skills", "examples")
EXCLUDED_PARTS = {"__pycache__", ".pytest_cache", ".DS_Store", "Thumbs.db", "__MACOSX"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def source_files() -> list[Path]:
    files = [ROOT / name for name in INCLUDED_FILES]
    for directory in INCLUDED_DIRECTORIES:
        files.extend(path for path in (ROOT / directory).rglob("*") if path.is_file())
    return sorted(
        path
        for path in files
        if not EXCLUDED_PARTS.intersection(path.parts)
        and path.suffix.lower() not in EXCLUDED_SUFFIXES
    )


def verify_archive(path: Path) -> dict[str, object]:
    with ZipFile(path) as archive:
        names = archive.namelist()
        if sum(item.file_size for item in archive.infolist()) > 50_000_000:
            raise RuntimeError("Uncompressed package exceeds 50 MB")
        if len(names) != len(set(names)) or any(".." in Path(name).parts for name in names):
            raise RuntimeError("Duplicate or unsafe archive paths")
        prefix = f"{PACKAGE_ROOT}/"
        if not names or any(not name.startswith(prefix) for name in names):
            raise RuntimeError("Archive must contain exactly one marketplace root directory")
        if any(EXCLUDED_PARTS.intersection(Path(name).parts)
               or Path(name).suffix.lower() in EXCLUDED_SUFFIXES for name in names):
            raise RuntimeError("Archive contains generated cache or operating-system files")
        expected = {f"{prefix}{source.relative_to(ROOT).as_posix()}" for source in source_files()}
        if set(names) != expected:
            raise RuntimeError("Archive does not match the submission file allowlist")

        manifest_name = f"{prefix}marketplace.json"
        readme_name = f"{prefix}README.md"
        if manifest_name not in names or readme_name not in names:
            raise RuntimeError("Archive is missing marketplace.json or README.md")

        manifest = json.loads(archive.read(manifest_name))
        skills = manifest.get("skills", [])
        if sum(bool(skill.get("entrypoint")) for skill in skills) != 1:
            raise RuntimeError("Manifest must declare exactly one entrypoint")
        for skill in skills:
            skill_file = f"{prefix}{skill['path']}/SKILL.md"
            if skill_file not in names:
                raise RuntimeError(f"Archive is missing {skill_file}")

    return {
        "archive": str(path),
        "files": len(names),
        "skills": len(skills),
        "entrypoints": 1,
        "size_bytes": path.stat().st_size,
    }


def main() -> None:
    output_directory = ROOT / "dist"
    output_directory.mkdir(exist_ok=True)
    output = output_directory / f"{PACKAGE_ROOT}.zip"

    with ZipFile(output, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
        for path in source_files():
            relative = path.relative_to(ROOT).as_posix()
            archive.write(path, f"{PACKAGE_ROOT}/{relative}")

    result = verify_archive(output)
    if output.stat().st_size > 50_000_000:
        raise RuntimeError("Archive exceeds the 50 MB package limit")
    print(json.dumps({"result": "PASS", **result}, indent=2))


if __name__ == "__main__":
    main()
