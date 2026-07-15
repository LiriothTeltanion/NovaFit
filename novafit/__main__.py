"""
Module: package launcher
Purpose: Route ``python -m novafit`` to the GUI or CLI without extra setup.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Minimal deps; comments in ENGLISH; emojis sparingly.
"""

from __future__ import annotations

import sys

from .cli import main


def run() -> int:
    """Launch the GUI by default and preserve explicit CLI arguments.

    Returns:
        Process status from the selected interface.

    Raises:
        None. User-facing errors are handled by the CLI dispatcher.

    Example:
        >>> run()  # doctest: +SKIP
        0
    """
    if len(sys.argv) == 1:
        return main(["--gui"])
    return main()


if __name__ == "__main__":
    raise SystemExit(run())
