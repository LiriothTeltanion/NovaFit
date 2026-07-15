"""
Module: input validation
Purpose: Keep user-input rules reusable across CLI, GUI, imports, and tests.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Minimal deps; comments in ENGLISH; emojis sparingly.
"""

from __future__ import annotations

import math
from decimal import Decimal, InvalidOperation
from datetime import date, datetime
from typing import Any

DATE_FORMAT = "%Y-%m-%d"
MAX_NOTE_LENGTH = 500
MAX_MOOD_LENGTH = 32


def parse_iso_date(value: str) -> date:
    """Parse and validate an ISO ``YYYY-MM-DD`` date.

    Args:
        value: Date text supplied by a user or import file.

    Returns:
        A ``datetime.date`` instance.

    Raises:
        ValueError: If the value is missing or not a valid ISO date.

    Example:
        >>> parse_iso_date('2026-07-15').isoformat()
        '2026-07-15'
    """
    normalized = value.strip()
    if not normalized:
        raise ValueError("Date is required in YYYY-MM-DD format.")
    try:
        return datetime.strptime(normalized, DATE_FORMAT).date()
    except ValueError as exc:
        raise ValueError("Date must use YYYY-MM-DD and be a real calendar date.") from exc


def validate_non_negative_int(value: Any, field_name: str, maximum: int) -> int:
    """Convert a value to a bounded non-negative integer.

    Args:
        value: Raw value to convert.
        field_name: Friendly field name for errors.
        maximum: Inclusive upper safety bound.

    Returns:
        The validated integer.

    Raises:
        ValueError: If conversion fails or the value is outside the range.

    Example:
        >>> validate_non_negative_int('8500', 'Steps', 200000)
        8500
    """
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be a whole number.")
    try:
        converted_decimal = Decimal(str(value).strip())
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a whole number.") from exc
    if not converted_decimal.is_finite() or converted_decimal != converted_decimal.to_integral_value():
        raise ValueError(f"{field_name} must be a whole number.")
    converted = int(converted_decimal)
    if converted < 0:
        raise ValueError(f"{field_name} cannot be negative.")
    if converted > maximum:
        raise ValueError(f"{field_name} cannot exceed {maximum:,}.")
    return converted


def validate_non_negative_float(value: Any, field_name: str, maximum: float) -> float:
    """Convert a value to a bounded non-negative float.

    Args:
        value: Raw value to convert.
        field_name: Friendly field name for errors.
        maximum: Inclusive upper safety bound.

    Returns:
        The validated float rounded to two decimals.

    Raises:
        ValueError: If conversion fails or the value is outside the range.

    Example:
        >>> validate_non_negative_float('2.5', 'Water', 20.0)
        2.5
    """
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be a number.")
    try:
        converted = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a number.") from exc
    if not math.isfinite(converted):
        raise ValueError(f"{field_name} must be a finite number.")
    if converted < 0:
        raise ValueError(f"{field_name} cannot be negative.")
    if converted > maximum:
        raise ValueError(f"{field_name} cannot exceed {maximum:g}.")
    return round(converted, 2)


def validate_optional_int(value: Any, field_name: str, maximum: int) -> int | None:
    """Validate an optional integer represented by empty text or ``None``.

    Args:
        value: Raw optional value.
        field_name: Friendly field name for errors.
        maximum: Inclusive upper safety bound.

    Returns:
        A validated integer or ``None``.

    Raises:
        ValueError: If a supplied value is invalid.

    Example:
        >>> validate_optional_int('', 'Calories', 20000) is None
        True
    """
    if value is None or str(value).strip() == "":
        return None
    return validate_non_negative_int(value, field_name, maximum)


def clean_text(value: Any, field_name: str, maximum_length: int) -> str | None:
    """Normalize optional text and enforce a length boundary.

    Args:
        value: Raw text or ``None``.
        field_name: Friendly field name for errors.
        maximum_length: Maximum number of characters.

    Returns:
        Trimmed text or ``None`` when empty.

    Raises:
        ValueError: If the normalized text is too long.

    Example:
        >>> clean_text('  Focused  ', 'Mood', 32)
        'Focused'
    """
    if value is None:
        return None
    normalized = " ".join(str(value).strip().split())
    if not normalized:
        return None
    if len(normalized) > maximum_length:
        raise ValueError(f"{field_name} must be {maximum_length} characters or fewer.")
    return normalized
