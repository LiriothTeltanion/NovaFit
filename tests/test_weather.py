"""
Module: weather tests
Purpose: Verify Open-Meteo parsing and recoverable network failures without internet.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Minimal deps; comments in ENGLISH; emojis sparingly.
"""

from __future__ import annotations

import unittest
from typing import Any

from novafit.weather import format_weather, get_weather, normalize_city


class FakeResponse:
    """Provide a minimal successful requests-compatible response."""

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return {
            "current": {
                "temperature_2m": 31.5,
                "relative_humidity_2m": 24,
                "wind_speed_10m": 12.3,
                "weather_code": 0,
            }
        }


class FakeSession:
    """Return a deterministic response for weather tests."""

    @staticmethod
    def get(*_args: Any, **_kwargs: Any) -> FakeResponse:
        return FakeResponse()


class FailingSession:
    """Raise a deterministic network-like error."""

    @staticmethod
    def get(*_args: Any, **_kwargs: Any) -> FakeResponse:
        raise OSError("offline")


class WeatherTests(unittest.TestCase):
    """Protect city aliases, parsing, and soft-failure behavior."""

    def test_city_alias(self) -> None:
        self.assertEqual(normalize_city("Beer-Sheva"), "beersheba")

    def test_successful_report(self) -> None:
        report = get_weather("beersheba", session=FakeSession())
        self.assertTrue(report.ok)
        self.assertEqual(report.temperature_c, 31.5)
        self.assertIn("Beersheba", format_weather(report))

    def test_failure_returns_recoverable_report(self) -> None:
        report = get_weather("beersheba", session=FailingSession())
        self.assertFalse(report.ok)
        self.assertEqual(report.status, "network_error")


if __name__ == "__main__":
    unittest.main()
