"""
Module: portable launcher
Purpose: Give editors and non-Windows systems one obvious NovaFit entry point.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Minimal deps; comments in ENGLISH; emojis sparingly.
"""

from __future__ import annotations

from novafit.__main__ import run


if __name__ == "__main__":
    raise SystemExit(run())
