"""
Module: timezone helpers
Purpose: Produce Asia/Jerusalem timestamps on every platform while failing softly
    when Windows has not yet installed the IANA timezone database.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Uses tzdata when available and a safe local-time fallback otherwise.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone, tzinfo
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .config import TIMEZONE_NAME

LOGGER = logging.getLogger(__name__)


def application_timezone() -> tzinfo:
    """Return the configured timezone with a cross-platform fallback.

    Returns:
        ``Asia/Jerusalem`` when IANA data is available; otherwise the operating
        system's current local timezone, then UTC as a final fallback.

    Raises:
        None. Missing Windows timezone data is recoverable.

    Example:
        >>> application_timezone() is not None
        True
    """
    try:
        return ZoneInfo(TIMEZONE_NAME)
    except ZoneInfoNotFoundError:
        local = datetime.now().astimezone().tzinfo
        if local is not None:
            LOGGER.warning(
                "IANA timezone data is unavailable; using the operating-system local timezone. "
                "Install the 'tzdata' package for exact Asia/Jerusalem rules."
            )
            return local
        return timezone.utc


def now_local() -> datetime:
    """Return an aware current timestamp for application metadata.

    Returns:
        Timezone-aware current datetime.

    Raises:
        None.

    Example:
        >>> now_local().tzinfo is not None
        True
    """
    return datetime.now(application_timezone())


def timestamp_label() -> str:
    """Return a human-readable timezone label for reports.

    Returns:
        Configured IANA name when available, otherwise an explicit local fallback.

    Example:
        >>> isinstance(timestamp_label(), str)
        True
    """
    try:
        ZoneInfo(TIMEZONE_NAME)
        return TIMEZONE_NAME
    except ZoneInfoNotFoundError:
        name = now_local().tzname() or "local time"
        return f"{name} (local fallback)"
