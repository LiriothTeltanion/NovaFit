"""Dedicated entry point for the console-enabled frozen NovaFit executable."""

from __future__ import annotations

import os
import sys

from novafit.cli import main


def configure_windows_console() -> None:
    """Make multilingual/emoji CLI output reliable in a frozen Windows app."""
    if os.name == "nt":
        try:
            import ctypes

            ctypes.windll.kernel32.SetConsoleOutputCP(65001)
            ctypes.windll.kernel32.SetConsoleCP(65001)
        except (AttributeError, OSError):
            pass
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


if __name__ == "__main__":
    configure_windows_console()
    raise SystemExit(main())
