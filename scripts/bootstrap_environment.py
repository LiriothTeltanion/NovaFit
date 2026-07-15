"""
Module: environment bootstrap
Purpose: Create or repair NovaFit's local virtual environment, install binary
    dependencies, and verify imports before Windows launchers run the test suite.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Cross-platform Python; Windows BAT files call this with the system interpreter.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_VENV = ROOT / ".venv"


def build_parser() -> argparse.ArgumentParser:
    """Build the bootstrap command-line interface.

    Returns:
        Configured argument parser.

    Example:
        >>> build_parser().prog
        'bootstrap_environment'
    """
    parser = argparse.ArgumentParser(
        prog="bootstrap_environment",
        description="Create or repair NovaFit's local virtual environment.",
    )
    parser.add_argument("--venv", type=Path, default=DEFAULT_VENV, help="Virtual environment directory.")
    parser.add_argument("--no-upgrade", action="store_true", help="Skip pip/setuptools/wheel upgrade.")
    parser.add_argument("--offline", action="store_true", help="Do not contact package indexes; validate only.")
    parser.add_argument("--verbose", action="store_true", help="Show full pip command output.")
    parser.add_argument("--force-recreate", action="store_true", help="Rebuild the generated virtual environment before setup.")
    return parser


def venv_python(venv_path: Path) -> Path:
    """Return the interpreter path inside a virtual environment.

    Args:
        venv_path: Virtual environment directory.

    Returns:
        Platform-specific Python executable path.

    Example:
        >>> venv_python(Path('.venv')).name in {'python', 'python.exe'}
        True
    """
    if os.name == "nt":
        return venv_path / "Scripts" / "python.exe"
    return venv_path / "bin" / "python"


def run(command: list[str], *, verbose: bool = False) -> None:
    """Run one bootstrap command with a friendly progress line.

    Args:
        command: Executable and arguments.
        verbose: Whether subprocess output should stream to the terminal.

    Returns:
        None.

    Raises:
        subprocess.CalledProcessError: If the command fails.

    Example:
        >>> run([sys.executable, '--version'])
    """
    print(f"[setup] {' '.join(command)}")
    if verbose:
        subprocess.run(command, cwd=ROOT, check=True)
        return
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if completed.returncode:
        print(completed.stdout.rstrip())
        raise subprocess.CalledProcessError(completed.returncode, command)


def verify_python_version() -> None:
    """Reject unsupported Python versions before creating a venv.

    Returns:
        None.

    Raises:
        RuntimeError: If Python is older than 3.10 or newer than the tested 3.14 line.

    Example:
        >>> verify_python_version()
    """
    if sys.version_info < (3, 10):
        raise RuntimeError("NovaFit requires Python 3.10 or newer.")
    if sys.version_info >= (3, 15):
        raise RuntimeError(
            "This NovaFit release is tested through Python 3.14. Install Python 3.13 or 3.14, then retry."
        )


def ensure_virtual_environment(path: Path, *, force_recreate: bool = False) -> Path:
    """Create a local virtual environment when missing or incomplete.

    Args:
        path: Virtual environment directory.
        force_recreate: Remove an existing generated environment first.

    Returns:
        Interpreter path inside the environment.

    Raises:
        RuntimeError: If the environment cannot be created.

    Example:
        >>> ensure_virtual_environment(Path('.tmp-venv'))  # doctest: +SKIP
    """
    python_path = venv_python(path)
    if force_recreate and path.exists():
        import shutil

        print(f"[setup] Rebuilding generated environment at {path}")
        shutil.rmtree(path)
    if python_path.exists():
        return python_path
    print(f"[setup] Creating local virtual environment at {path}")
    venv.EnvBuilder(with_pip=True, clear=path.exists()).create(path)
    if not python_path.exists():
        raise RuntimeError(f"Virtual environment Python was not created: {python_path}")
    return python_path


def install_dependencies(python_path: Path, *, no_upgrade: bool, offline: bool, verbose: bool) -> None:
    """Install NovaFit and all runtime dependencies into the local environment.

    Args:
        python_path: Virtual environment interpreter.
        no_upgrade: Whether to skip packaging-tool upgrades.
        offline: Validate without downloading packages.
        verbose: Stream pip output.

    Returns:
        None.

    Raises:
        subprocess.CalledProcessError: If pip cannot complete.

    Example:
        >>> install_dependencies(Path('python'), no_upgrade=True, offline=True, verbose=False)  # doctest: +SKIP
    """
    if offline:
        return
    if not no_upgrade:
        run(
            [str(python_path), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"],
            verbose=verbose,
        )
    run(
        [
            str(python_path),
            "-m",
            "pip",
            "install",
            "--upgrade",
            "--prefer-binary",
            "--only-binary=:all:",
            "-r",
            str(ROOT / "requirements.txt"),
        ],
        verbose=verbose,
    )
    run([str(python_path), "-m", "pip", "install", "--editable", str(ROOT)], verbose=verbose)


def verify_imports(python_path: Path, *, verbose: bool = False) -> None:
    """Verify every package that previously caused Windows checker failures.

    Args:
        python_path: Virtual environment interpreter.
        verbose: Stream subprocess output.

    Returns:
        None.

    Raises:
        subprocess.CalledProcessError: If a required import is unavailable.

    Example:
        >>> verify_imports(Path(sys.executable))
    """
    code = (
        "import tkinter; import matplotlib; import PIL; import requests; import faker; import tzdata; "
        "from zoneinfo import ZoneInfo; ZoneInfo('Asia/Jerusalem'); "
        "print('Tkinter', tkinter.TkVersion); "
        "print('Matplotlib', matplotlib.__version__); "
        "print('Pillow', PIL.__version__); "
        "print('Asia/Jerusalem timezone available')"
    )
    run([str(python_path), "-c", code], verbose=verbose)


def main(argv: list[str] | None = None) -> int:
    """Create/repair the environment and verify its runtime imports.

    Args:
        argv: Optional command-line arguments.

    Returns:
        Zero on success and one on a friendly setup failure.

    Example:
        >>> main(['--help'])  # doctest: +SKIP
        0
    """
    args = build_parser().parse_args(argv)
    try:
        verify_python_version()
        python_path = ensure_virtual_environment(
            args.venv.resolve(),
            force_recreate=args.force_recreate,
        )
        install_dependencies(
            python_path,
            no_upgrade=args.no_upgrade,
            offline=args.offline,
            verbose=args.verbose,
        )
        verify_imports(python_path, verbose=True)
        print(f"Environment ready: {python_path} ✅")
        return 0
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"Environment setup failed: {exc} ❌")
        print("Check internet access, then rerun REPAIR_AND_VERIFY.bat. Python 3.13 is the recommended fallback.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
