"""
Module: logging configuration
Purpose: Centralize concise console and rotating-file logging for NovaFit.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Minimal deps; comments in ENGLISH; emojis sparingly.
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def configure_logging(
    level: str = "INFO",
    *,
    log_file: Path | None = None,
    debug: bool = False,
) -> None:
    """Configure NovaFit logging once per process.

    Args:
        level: Standard logging level name such as ``INFO`` or ``WARNING``.
        log_file: Optional destination for a rotating diagnostic log.
        debug: When true, include source file and line information.

    Returns:
        None.

    Raises:
        ValueError: If ``level`` is not a recognized logging level.

    Example:
        >>> configure_logging("INFO")
    """
    normalized = level.upper().strip()
    numeric_level = getattr(logging, normalized, None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Unsupported log level: {level}")

    root = logging.getLogger()
    # Third-party plotting internals are noisy at INFO and are not user actions.
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    if root.handlers:
        root.setLevel(numeric_level)
        return

    message_format = (
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        if not debug
        else "%(asctime)s | %(levelname)s | %(name)s | %(filename)s:%(lineno)d | %(message)s"
    )
    formatter = logging.Formatter(message_format, datefmt="%Y-%m-%d %H:%M:%S")

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    root.addHandler(console)

    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=512_000,
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

    root.setLevel(numeric_level)
