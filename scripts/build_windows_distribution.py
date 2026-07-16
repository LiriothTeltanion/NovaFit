"""Build, smoke-test, audit, and archive NovaFit's official Windows bundle."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from novafit import __version__  # noqa: E402
from tools.standalone_audit import audit_standalone, sha256_file, write_manifest  # noqa: E402

SPEC = ROOT / "packaging" / "novafit.spec"
ICON = ROOT / "assets" / "novafit.ico"


def build_parser() -> argparse.ArgumentParser:
    """Build the standalone distribution parser."""
    parser = argparse.ArgumentParser(
        description="Build and audit NovaFit's PyInstaller onedir Windows distribution."
    )
    parser.add_argument("--output-dir", type=Path, default=ROOT / "dist")
    parser.add_argument("--work-dir", type=Path, default=ROOT / "build" / "windows-standalone")
    parser.add_argument("--skip-smoke", action="store_true", help="Skip the frozen CLI smoke test.")
    return parser


def package_basename(version: str) -> str:
    """Return the stable public standalone artifact basename."""
    return f"NovaFit-v{version}-Windows-x64-Standalone"


def _safe_remove(path: Path, allowed_parent: Path) -> None:
    """Remove one generated path only when it remains inside its declared parent."""
    path = path.resolve()
    allowed_parent = allowed_parent.resolve()
    if path == allowed_parent or allowed_parent not in path.parents:
        raise ValueError(f"Refusing to remove path outside generated output: {path}")
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def _run(command: list[str], *, env: dict[str, str] | None = None, timeout: int = 900) -> None:
    """Run a visible build command and fail immediately on errors."""
    print(f"[standalone] {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=ROOT, env=env, timeout=timeout, check=True)


def _source_commit() -> str:
    """Resolve the CI or local source commit without making Git mandatory."""
    if os.getenv("GITHUB_SHA"):
        return os.environ["GITHUB_SHA"]
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def _build_info() -> dict[str, Any]:
    """Return public provenance and storage metadata for the exact bundle."""
    import PyInstaller

    return {
        "schema_version": 1,
        "product": "NovaFit",
        "version": __version__,
        "architecture": platform.machine(),
        "python": platform.python_version(),
        "pyinstaller": PyInstaller.__version__,
        "bundle_layout": "pyinstaller-onedir",
        "data_directory": "%LOCALAPPDATA%/NovaFit",
        "source_commit": _source_commit(),
    }


def _write_companion_files(stage: Path) -> None:
    """Add human-readable launch, privacy, license, and provenance files."""
    (stage / "LICENSE.txt").write_text(
        (ROOT / "LICENSE").read_text(encoding="utf-8"), encoding="utf-8", newline="\n"
    )
    (stage / "README_FIRST.txt").write_text(
        "NovaFit standalone for Windows 10/11\n"
        "=====================================\n\n"
        "1. Double-click START_NOVAFIT.bat or NovaFit.exe.\n"
        "2. No Python installation is required.\n"
        "3. Your private database, settings, logs, exports and backups live in:\n"
        "   %LOCALAPPDATA%\\NovaFit\n\n"
        "Upgrades: close NovaFit, extract the new release to a fresh folder, and launch it.\n"
        "Your data remains in Local AppData and is not bundled with the program.\n\n"
        "CLI/automation: open NovaFit-CLI.exe --help in Windows Terminal.\n"
        "Integrity: STANDALONE_MANIFEST.json hashes every bundled payload file.\n",
        encoding="utf-8",
        newline="\n",
    )
    (stage / "START_NOVAFIT.bat").write_bytes(
        b"@echo off\r\nsetlocal\r\ncd /d \"%~dp0\"\r\nstart \"NovaFit\" \"%~dp0NovaFit.exe\"\r\n"
    )
    (stage / "OPEN_DATA_FOLDER.bat").write_bytes(
        b"@echo off\r\nsetlocal\r\nif not exist \"%LOCALAPPDATA%\\NovaFit\" mkdir \"%LOCALAPPDATA%\\NovaFit\"\r\n"
        b"start \"NovaFit data\" \"%LOCALAPPDATA%\\NovaFit\"\r\n"
    )
    (stage / "BUILD_INFO.json").write_text(
        json.dumps(_build_info(), indent=2) + "\n", encoding="utf-8", newline="\n"
    )


def _smoke_frozen_cli(stage: Path) -> None:
    """Exercise the packaged interpreter against isolated disposable data."""
    executable = stage / "NovaFit-CLI.exe"
    with tempfile.TemporaryDirectory(prefix="novafit-frozen-smoke-") as temp_dir:
        data_dir = Path(temp_dir) / "data"
        env = os.environ.copy()
        env.update(
            {
                "NOVAFIT_DATA_DIR": str(data_dir),
                "NOVAFIT_DB_PATH": str(data_dir / "smoke.db"),
                "MPLBACKEND": "Agg",
                "NO_COLOR": "1",
                "PYTHONUTF8": "1",
            }
        )
        _run([str(executable), "--version"], env=env, timeout=120)
        _run([str(executable), "--sample"], env=env, timeout=180)
        _run([str(executable), "--dashboard"], env=env, timeout=180)
        database = data_dir / "smoke.db"
        if not database.is_file() or database.read_bytes()[:16] != b"SQLite format 3\x00":
            raise RuntimeError("Frozen CLI smoke test did not create a valid isolated SQLite database.")


def _write_checksum(path: Path) -> Path:
    """Write a standard sha256sum-compatible sidecar for one artifact."""
    sidecar = path.with_suffix(path.suffix + ".sha256")
    sidecar.write_text(f"{sha256_file(path)}  {path.name}\n", encoding="ascii", newline="\n")
    return sidecar


def build_distribution(output_dir: Path, work_dir: Path, *, smoke: bool) -> tuple[Path, Path]:
    """Build the onedir folder, audit it, ZIP it, and return ZIP/checksum paths."""
    if sys.platform != "win32":
        raise RuntimeError("The standalone distribution must be built on 64-bit Windows.")
    if platform.machine().lower() not in {"amd64", "x86_64"}:
        raise RuntimeError(f"Unsupported Windows architecture: {platform.machine()}")
    for required in (SPEC, ICON):
        if not required.is_file():
            raise FileNotFoundError(f"Required build input is missing: {required}")

    output_dir = output_dir.expanduser().resolve()
    work_dir = work_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)
    raw_dist = work_dir / "pyinstaller-dist"
    pyinstaller_work = work_dir / "pyinstaller-work"
    stage = output_dir / package_basename(__version__)
    archive = output_dir / f"{package_basename(__version__)}.zip"
    checksum = archive.with_suffix(archive.suffix + ".sha256")
    for generated, parent in (
        (raw_dist, work_dir),
        (pyinstaller_work, work_dir),
        (stage, output_dir),
        (archive, output_dir),
        (checksum, output_dir),
    ):
        _safe_remove(generated, parent)

    _run(
        [
            sys.executable,
            "-m",
            "PyInstaller",
            "--clean",
            "--noconfirm",
            "--distpath",
            str(raw_dist),
            "--workpath",
            str(pyinstaller_work),
            str(SPEC),
        ]
    )
    built = raw_dist / "NovaFit"
    if not built.is_dir():
        raise RuntimeError(f"PyInstaller did not produce the expected onedir folder: {built}")
    shutil.move(str(built), str(stage))
    _write_companion_files(stage)
    write_manifest(stage, __version__)

    audit = audit_standalone(stage, __version__)
    if not audit.ok:
        raise RuntimeError("Standalone audit failed:\n- " + "\n- ".join(audit.errors))
    print(f"[standalone] audited {audit.checked_files} bundled files", flush=True)
    if smoke:
        _smoke_frozen_cli(stage)

    archive_path = Path(
        shutil.make_archive(
            str(output_dir / package_basename(__version__)),
            "zip",
            root_dir=output_dir,
            base_dir=stage.name,
        )
    )
    checksum_path = _write_checksum(archive_path)
    print(
        f"[standalone] created {archive_path.name} ({archive_path.stat().st_size / 1024 / 1024:.2f} MiB)",
        flush=True,
    )
    return archive_path, checksum_path


def main(argv: list[str] | None = None) -> int:
    """Build the exact standalone artifact and expose paths to GitHub Actions."""
    args = build_parser().parse_args(argv)
    archive, checksum = build_distribution(
        args.output_dir,
        args.work_dir,
        smoke=not args.skip_smoke,
    )
    if github_output := os.getenv("GITHUB_OUTPUT"):
        with Path(github_output).open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(f"standalone_zip={archive}\n")
            handle.write(f"standalone_checksum={checksum}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
