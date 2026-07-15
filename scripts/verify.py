"""
Module: repository verification
Purpose: Compile, preflight dependencies, test, and smoke-check NovaFit with one
    friendly cross-platform command.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Run through verify_windows.bat so the local environment self-repairs first.
"""

from __future__ import annotations

import argparse
import compileall
import importlib.util
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

ROOT = Path(__file__).resolve().parent.parent
REQUIRED_FILES = (
    "README.md",
    "requirements.txt",
    "pyproject.toml",
    "novafit/__main__.py",
    "novafit/cli.py",
    "novafit/gui.py",
    "novafit/backup.py",
    "novafit/database.py",
    "novafit/analytics.py",
    "novafit/charts.py",
    "novafit/themes.py",
    "novafit/motivation.py",
    "novafit/motivation_panel.py",
    "novafit/recommendations.py",
    "novafit/recommendations_panel.py",
    "novafit/profile_panel.py",
    "novafit/i18n.py",
    "novafit/icon_factory.py",
    "novafit/time_utils.py",
    "run_novafit.bat",
    "REPAIR_AND_VERIFY.bat",
    "VERIFY_ALL.bat",
    "tools/package_audit.py",
    "scripts/sync_docs.py",
    "docs/PROJECT_FACTS.md",
    "portfolio/project.json",
    "assets/manifest.json",
)
REQUIRED_IMPORTS = {
    "matplotlib": "matplotlib",
    "PIL": "Pillow",
    "requests": "requests",
    "faker": "Faker",
    "tzdata": "tzdata",
}


def build_parser() -> argparse.ArgumentParser:
    """Build verification flags.

    Returns:
        Configured parser.

    Example:
        >>> build_parser().prog
        'verify'
    """
    parser = argparse.ArgumentParser(prog="verify", description="Verify the NovaFit release package.")
    parser.add_argument("--debug", action="store_true", help="Show full Python tracebacks on failure.")
    parser.add_argument(
        "--quality",
        action="store_true",
        help="Require and run Ruff plus Pyright in addition to runtime verification.",
    )
    parser.add_argument(
        "--skip-tests", action="store_true", help="Skip unit tests (intended for split CI jobs)."
    )
    parser.add_argument("--skip-smoke", action="store_true", help="Skip isolated CLI/export smoke tests.")
    return parser


def run_command(command: list[str], env: dict[str, str] | None = None) -> None:
    """Run a verification command and fail on a non-zero status.

    Args:
        command: Executable and arguments.
        env: Optional environment overrides.

    Returns:
        None.

    Raises:
        subprocess.CalledProcessError: If the command fails.

    Example:
        >>> run_command([sys.executable, '--version'])
    """
    print(f"[verify] {' '.join(command)}")
    subprocess.run(command, cwd=ROOT, env=env, check=True)


def verify_required_files() -> None:
    """Ensure release-critical files are present.

    Returns:
        None.

    Raises:
        FileNotFoundError: If a required package file is missing.

    Example:
        >>> verify_required_files()
    """
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).exists()]
    if missing:
        raise FileNotFoundError(f"Missing required files: {', '.join(missing)}")


def verify_runtime_dependencies() -> None:
    """Fail early with an actionable dependency message.

    Returns:
        None.

    Raises:
        RuntimeError: If a package is missing or Asia/Jerusalem timezone data is
            unavailable.

    Example:
        >>> verify_runtime_dependencies()  # doctest: +SKIP
    """
    missing = [
        distribution
        for module, distribution in REQUIRED_IMPORTS.items()
        if importlib.util.find_spec(module) is None
    ]
    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(
            f"Missing runtime dependencies: {joined}. Run setup_windows.bat or REPAIR_AND_VERIFY.bat."
        )
    try:
        ZoneInfo("Asia/Jerusalem")
    except ZoneInfoNotFoundError as exc:
        raise RuntimeError(
            "Asia/Jerusalem timezone data is unavailable. Run setup_windows.bat to install tzdata."
        ) from exc


def verify_requirements() -> None:
    """Reject duplicate dependency names in ``requirements.txt``.

    Returns:
        None.

    Raises:
        ValueError: If the same dependency appears more than once.

    Example:
        >>> verify_requirements()
    """
    names: list[str] = []
    for raw_line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        name = line.split(";")[0].split("<")[0].split(">")[0].split("=")[0].strip().lower()
        names.append(name)
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise ValueError(f"Duplicate dependencies: {', '.join(duplicates)}")


def verify_static_quality() -> None:
    """Run the repository's opt-in lint and basic type-analysis gates.

    Raises:
        RuntimeError: If a development checker is unavailable.
        subprocess.CalledProcessError: If Ruff or Pyright reports an error.
    """
    missing = [module for module in ("ruff", "pyright") if importlib.util.find_spec(module) is None]
    if missing:
        raise RuntimeError(
            "Missing development checks: "
            f"{', '.join(missing)}. Install requirements-dev.txt or run VERIFY_ALL.bat."
        )
    # Start with repository-wide correctness diagnostics that must never be
    # baselined away, then lint/type-check the safety-critical foundation in
    # full. Broader style/type adoption can expand this list incrementally.
    run_command(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            "--select",
            "E9,F63,F7,F82",
            "novafit",
            "scripts",
            "tests",
            "tools",
        ]
    )
    run_command(
        [
            sys.executable,
            "-m",
            "ruff",
            "check",
            "tools",
            "scripts/verify.py",
            "scripts/bootstrap_environment.py",
            "tests/test_bootstrap_environment.py",
            "tests/test_distribution_contract.py",
            "tests/test_backup.py",
        ]
    )
    run_command(
        [
            sys.executable,
            "-m",
            "pyright",
            "--pythonpath",
            sys.executable,
            "novafit/backup.py",
            "novafit/config.py",
            "novafit/validation.py",
            "scripts/bootstrap_environment.py",
            "scripts/verify.py",
            "tools/package_audit.py",
        ]
    )


def smoke_test() -> None:
    """Exercise SQLite, motivation, charts, JSON, and HTML in isolation.

    Returns:
        None.

    Raises:
        RuntimeError: If the smoke workflow produces unexpected results.

    Example:
        >>> smoke_test()  # doctest: +SKIP
    """
    env = os.environ.copy()
    with tempfile.TemporaryDirectory() as temp_dir:
        data_dir = Path(temp_dir) / "data"
        env["NOVAFIT_DATA_DIR"] = str(data_dir)
        env["NOVAFIT_DB_PATH"] = str(data_dir / "smoke.db")
        env["MPLBACKEND"] = "Agg"
        run_command([sys.executable, "-m", "novafit.cli", "--sample"], env)
        run_command([sys.executable, "-m", "novafit.cli", "--dashboard"], env)
        run_command([sys.executable, "-m", "novafit.cli", "--motivation"], env)
        run_command([sys.executable, "-m", "novafit.cli", "--recommendations", "--language", "es"], env)
        run_command(
            [
                sys.executable,
                "-m",
                "novafit.cli",
                "--create-user",
                "Smoke Athlete",
                "--language",
                "he",
                "--theme",
                "sapphire",
                "--avatar",
                "runner",
                "--activity-level",
                "active",
                "--sport-focus",
                "running",
            ],
            env,
        )
        run_command([sys.executable, "-m", "novafit.cli", "--profiles"], env)
        run_command(
            [sys.executable, "-m", "novafit.cli", "--export-json", str(data_dir / "smoke.json")],
            env,
        )
        run_command(
            [sys.executable, "-m", "novafit.cli", "--backup", str(data_dir / "backups")],
            env,
        )
        run_command(
            [
                sys.executable,
                "-m",
                "novafit.cli",
                "--chart",
                str(data_dir / "smoke-dashboard.png"),
                "--chart-view",
                "training_atlas",
                "--chart-days",
                "30",
                "--chart-theme",
                "aurora",
            ],
            env,
        )
        run_command(
            [
                sys.executable,
                "-m",
                "novafit.cli",
                "--report-html",
                str(data_dir / "smoke-report.html"),
                "--chart-view",
                "consistency",
                "--chart-days",
                "30",
                "--chart-theme",
                "desert",
            ],
            env,
        )
        expected = {
            "smoke.json": 100,
            "smoke-dashboard.png": 20_000,
            "smoke-report.html": 20_000,
        }
        for filename, minimum_size in expected.items():
            output = data_dir / filename
            if not output.exists() or output.stat().st_size < minimum_size:
                raise RuntimeError(f"Smoke output is missing or too small: {filename}")
        backup_files = list((data_dir / "backups").glob("novafit-complete-*.zip"))
        if len(backup_files) != 1 or backup_files[0].stat().st_size < 1_000:
            raise RuntimeError("Complete all-profile backup smoke output is missing or too small.")


def main(argv: list[str] | None = None) -> int:
    """Run every release verification step.

    Args:
        argv: Optional verification flags.

    Returns:
        Zero when all checks pass and one for a friendly failure.

    Example:
        >>> main([])  # doctest: +SKIP
        0
    """
    args = build_parser().parse_args(argv)
    try:
        print("NovaFit repository verification")
        print("=" * 56)
        print(f"Interpreter: {sys.executable}")
        print(f"Python: {sys.version.split()[0]}")
        verify_required_files()
        verify_runtime_dependencies()
        verify_requirements()
        if not compileall.compile_dir(ROOT / "novafit", quiet=1):
            raise RuntimeError("Python compilation failed.")
        if not compileall.compile_dir(ROOT / "scripts", quiet=1):
            raise RuntimeError("Script compilation failed.")
        if not compileall.compile_dir(ROOT / "tools", quiet=1):
            raise RuntimeError("Tool compilation failed.")
        run_command([sys.executable, "tools/package_audit.py"])
        run_command([sys.executable, "scripts/sync_docs.py", "--check"])
        if args.quality:
            verify_static_quality()
        if not args.skip_tests:
            run_command([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"])
        if not args.skip_smoke:
            smoke_test()
        print("All NovaFit checks passed. [OK]")
        return 0
    except Exception as exc:
        print(f"NovaFit verification failed: {exc} [ERROR]")
        print("Next step: run REPAIR_AND_VERIFY.bat from this NovaFit folder.")
        if args.debug:
            raise
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
