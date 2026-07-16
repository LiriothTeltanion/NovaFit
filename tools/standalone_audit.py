"""Audit the exact NovaFit PyInstaller onedir bundle before publication."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

MANIFEST_NAME = "STANDALONE_MANIFEST.json"
REQUIRED_FILES = (
    "NovaFit.exe",
    "NovaFit-CLI.exe",
    "START_NOVAFIT.bat",
    "OPEN_DATA_FOLDER.bat",
    "README_FIRST.txt",
    "LICENSE.txt",
    "BUILD_INFO.json",
    MANIFEST_NAME,
)
FORBIDDEN_NAMES = {".env", "id_dsa", "id_ed25519", "id_rsa"}
FORBIDDEN_SUFFIXES = {".db", ".log", ".sqlite", ".sqlite3"}


@dataclass(slots=True)
class StandaloneAuditReport:
    """Collect exact-bundle validation findings."""

    errors: list[str] = field(default_factory=list)
    checked_files: int = 0

    @property
    def ok(self) -> bool:
        """Return whether the bundle passed every release check."""
        return not self.errors


def sha256_file(path: Path) -> str:
    """Return one file's streaming SHA-256 digest."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def bundle_inventory(root: Path) -> list[dict[str, Any]]:
    """Build the stable manifest inventory, excluding the manifest itself."""
    inventory: list[dict[str, Any]] = []
    paths = sorted(
        (path for path in root.rglob("*") if path.is_file() and path.name != MANIFEST_NAME),
        key=lambda path: path.relative_to(root).as_posix().casefold(),
    )
    for path in paths:
        inventory.append(
            {
                "path": path.relative_to(root).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return inventory


def write_manifest(root: Path, version: str) -> Path:
    """Write an integrity manifest for every payload file in the bundle."""
    root = root.expanduser().resolve()
    manifest = root / MANIFEST_NAME
    payload = {
        "schema_version": 1,
        "product": "NovaFit",
        "version": version,
        "format": "windows-x64-pyinstaller-onedir",
        "files": bundle_inventory(root),
    }
    manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
    return manifest


def _read_json(path: Path, report: StandaloneAuditReport) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        report.errors.append(f"Invalid JSON file {path.name}: {exc}")
        return None
    if not isinstance(payload, dict):
        report.errors.append(f"JSON root must be an object: {path.name}")
        return None
    return payload


def audit_standalone(root: Path, expected_version: str) -> StandaloneAuditReport:
    """Verify contents, privacy boundaries, metadata, executables, and hashes."""
    root = root.expanduser().resolve()
    report = StandaloneAuditReport()
    if not root.is_dir():
        report.errors.append(f"Standalone root does not exist: {root}")
        return report

    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            report.errors.append(f"Required standalone file is missing: {relative}")
    if not (root / "_internal").is_dir():
        report.errors.append("PyInstaller _internal directory is missing (expected onedir layout).")

    files = [path for path in root.rglob("*") if path.is_file()]
    report.checked_files = len(files)
    for path in files:
        relative = path.relative_to(root).as_posix()
        name = path.name.lower()
        if name in FORBIDDEN_NAMES or name.startswith(".env."):
            report.errors.append(f"Credential-like file is forbidden: {relative}")
        if path.suffix.lower() in FORBIDDEN_SUFFIXES or name.endswith((".db-wal", ".db-shm")):
            report.errors.append(f"Mutable runtime data is forbidden: {relative}")

    for executable_name in ("NovaFit.exe", "NovaFit-CLI.exe"):
        executable = root / executable_name
        if not executable.is_file():
            continue
        if executable.stat().st_size < 100_000:
            report.errors.append(f"Executable is unexpectedly small: {executable_name}")
        elif executable.read_bytes()[:2] != b"MZ":
            report.errors.append(f"Executable lacks a Windows PE header: {executable_name}")

    build_info_path = root / "BUILD_INFO.json"
    if build_info_path.is_file():
        build_info = _read_json(build_info_path, report)
        if build_info is not None:
            if build_info.get("version") != expected_version:
                report.errors.append("BUILD_INFO.json version does not match the release version.")
            if build_info.get("bundle_layout") != "pyinstaller-onedir":
                report.errors.append("BUILD_INFO.json does not declare the onedir layout.")
            if build_info.get("data_directory") != "%LOCALAPPDATA%/NovaFit":
                report.errors.append("BUILD_INFO.json does not declare the durable app-data location.")

    manifest_path = root / MANIFEST_NAME
    if manifest_path.is_file():
        manifest = _read_json(manifest_path, report)
        if manifest is not None:
            if manifest.get("version") != expected_version:
                report.errors.append("Standalone manifest version does not match the release version.")
            expected_files = manifest.get("files")
            if expected_files != bundle_inventory(root):
                report.errors.append("Standalone payload differs from STANDALONE_MANIFEST.json.")
    return report


def build_parser() -> argparse.ArgumentParser:
    """Build the standalone audit parser."""
    parser = argparse.ArgumentParser(description="Audit an exact NovaFit standalone directory.")
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--version", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Audit one staged bundle and return a shell-friendly status."""
    args = build_parser().parse_args(argv)
    report = audit_standalone(args.root, args.version)
    print("NovaFit standalone audit")
    print("=" * 56)
    for error in report.errors:
        print(f"[ERROR] {error}")
    print(f"Checked {report.checked_files} files · {len(report.errors)} errors")
    if not report.ok:
        return 1
    print("Standalone bundle is complete, private-data-free, and hash-verified. [OK]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
