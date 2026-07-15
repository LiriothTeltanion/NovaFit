"""
Module: weather integration
Purpose: Fetch current Open-Meteo conditions without API keys or unsafe SSL changes.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Minimal deps; comments in ENGLISH; emojis sparingly.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Mapping, Protocol

from .config import CITY_COORDS

LOGGER = logging.getLogger(__name__)
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


class HttpResponse(Protocol):
    """Describe the small response interface used by the weather client.

    Example:
        A ``requests.Response`` instance satisfies this protocol at runtime.
    """

    def raise_for_status(self) -> None:
        """Raise an exception for an unsuccessful HTTP response."""

    def json(self) -> Any:
        """Decode and return JSON response data."""


@dataclass(frozen=True, slots=True)
class WeatherReport:
    """Represent successful or recoverable weather lookup results.

    Attributes:
        city: Normalized display city.
        temperature_c: Current temperature, or ``None`` on failure.
        humidity_pct: Current relative humidity, or ``None`` on failure.
        wind_kmh: Current wind speed, or ``None`` on failure.
        weather_code: WMO weather code, or ``None`` on failure.
        status: ``success`` or a concise error category.
        message: Human-readable source or recovery guidance.

    Example:
        >>> WeatherReport('Beersheba', 30, 20, 10, 0, 'success', 'Open-Meteo').ok
        True
    """

    city: str
    temperature_c: float | None
    humidity_pct: float | None
    wind_kmh: float | None
    weather_code: int | None
    status: str
    message: str

    @property
    def ok(self) -> bool:
        """Return whether the lookup succeeded.

        Returns:
            ``True`` for a complete API response.

        Raises:
            None.

        Example:
            >>> WeatherReport('X', None, None, None, None, 'error', 'No').ok
            False
        """
        return self.status == "success"


def normalize_city(city: str) -> str:
    """Normalize city aliases to a configured coordinate key.

    Args:
        city: User-provided city text.

    Returns:
        Coordinate-map key.

    Raises:
        ValueError: If the city is empty or unsupported.

    Example:
        >>> normalize_city("Be'er Sheva")
        "be'er sheva"
    """
    normalized = " ".join(city.lower().strip().split())
    aliases = {
        "beer-sheva": "beersheba",
        "beer sheba": "beersheba",
        "beer sheva": "beer sheva",
        "be'er-sheva": "be'er sheva",
        "tel-aviv": "tel aviv",
    }
    normalized = aliases.get(normalized, normalized)
    if not normalized:
        raise ValueError("City is required.")
    if normalized not in CITY_COORDS:
        supported = ", ".join(sorted({key for key in CITY_COORDS if "'" not in key}))
        raise ValueError(f"Unsupported city. Available: {supported}")
    return normalized


def get_weather(city: str, *, session: Any = None, timeout: float = 10.0) -> WeatherReport:
    """Fetch current conditions from Open-Meteo using verified HTTPS.

    Args:
        city: Supported Israeli city name or alias.
        session: Optional requests-like object used for testing.
        timeout: Request timeout in seconds.

    Returns:
        Weather report. Network failures are represented as recoverable results.

    Raises:
        ValueError: If the city is unsupported or timeout is not positive.

    Example:
        >>> get_weather('beersheba').city
        'Beersheba'
    """
    if timeout <= 0:
        raise ValueError("Timeout must be greater than zero.")
    city_key = normalize_city(city)
    latitude, longitude = CITY_COORDS[city_key]

    if session is None:
        try:
            import requests
        except ImportError:
            return WeatherReport(
                city_key.title(), None, None, None, None,
                "library_error", "Install dependencies with setup_windows.bat.",
            )
        session = requests

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
        "timezone": "Asia/Jerusalem",
    }
    try:
        response: HttpResponse = session.get(OPEN_METEO_URL, params=params, timeout=timeout)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, Mapping):
            raise ValueError("API response root is not an object.")
        current = payload.get("current")
        if not isinstance(current, Mapping):
            raise ValueError("API response does not include current conditions.")
        return WeatherReport(
            city=city_key.title(),
            temperature_c=_number_or_none(current.get("temperature_2m")),
            humidity_pct=_number_or_none(current.get("relative_humidity_2m")),
            wind_kmh=_number_or_none(current.get("wind_speed_10m")),
            weather_code=_int_or_none(current.get("weather_code")),
            status="success",
            message="Open-Meteo",
        )
    except Exception as exc:  # Requests exposes several optional exception classes.
        LOGGER.warning("Weather lookup failed: %s", exc)
        return WeatherReport(
            city=city_key.title(),
            temperature_c=None,
            humidity_pct=None,
            wind_kmh=None,
            weather_code=None,
            status="network_error",
            message="Weather unavailable. Check the connection and try again.",
        )


def weather_emoji(code: int | None) -> str:
    """Map a WMO weather code to a compact visual label.

    Args:
        code: WMO weather code.

    Returns:
        One weather emoji.

    Raises:
        None.

    Example:
        >>> weather_emoji(0)
        '☀️'
    """
    if code is None:
        return "🌡️"
    if code == 0:
        return "☀️"
    if code in {1, 2}:
        return "🌤️"
    if code == 3:
        return "☁️"
    if code in {45, 48}:
        return "🌫️"
    if 51 <= code <= 67:
        return "🌧️"
    if 71 <= code <= 77:
        return "🌨️"
    if code >= 95:
        return "⛈️"
    return "🌡️"


def format_weather(report: WeatherReport) -> str:
    """Format a weather report for CLI or GUI status text.

    Args:
        report: Weather lookup result.

    Returns:
        A single concise status line.

    Raises:
        None.

    Example:
        >>> 'Beersheba' in format_weather(WeatherReport('Beersheba', 30, 20, 5, 0, 'success', 'Open-Meteo'))
        True
    """
    if not report.ok:
        return f"{report.city}: {report.message} ⚠️"
    return (
        f"{weather_emoji(report.weather_code)} {report.city}: "
        f"{report.temperature_c:.1f}°C, {report.humidity_pct:.0f}% humidity, "
        f"{report.wind_kmh:.1f} km/h wind"
    )


def _number_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
