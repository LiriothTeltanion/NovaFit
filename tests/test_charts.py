"""
Module: chart studio tests
Purpose: Verify every definitive analytics view renders and exports without a display server.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Minimal deps; comments in ENGLISH; emojis sparingly.
"""

from __future__ import annotations

import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

from novafit.charts import SUPPORTED_VIEWS, create_analytics_figure, save_analytics_chart
from novafit.config import AppSettings
from novafit.models import HealthEntry


class ChartStudioTests(unittest.TestCase):
    """Protect the headless rendering contract used by reports and CI."""

    def setUp(self) -> None:
        start = date(2026, 6, 16)
        self.rows = [
            HealthEntry.build(
                start + timedelta(days=index),
                5000 + (index % 10) * 900,
                1.4 + (index % 6) * 0.25,
                1700 + (index % 8) * 90,
                ("Focused", "Calm", "Energetic")[index % 3],
            )
            for index in range(30)
        ]
        self.settings = AppSettings(chart_days=30)

    def test_every_view_creates_multiple_axes(self) -> None:
        for view in SUPPORTED_VIEWS:
            with self.subTest(view=view):
                figure = create_analytics_figure(self.rows, self.settings, view=view, days=30)
                self.assertGreaterEqual(len(figure.axes), 3)

    def test_dark_and_light_themes_render(self) -> None:
        dark = create_analytics_figure(self.rows, self.settings, theme="dark", days=30)
        light = create_analytics_figure(self.rows, self.settings, theme="light", days=30)
        self.assertNotEqual(dark.get_facecolor(), light.get_facecolor())

    def test_png_export_writes_nonempty_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "dashboard.png"
            save_analytics_chart(self.rows, self.settings, destination, view="overview", days=30)
            self.assertTrue(destination.exists())
            self.assertGreater(destination.stat().st_size, 20_000)

    def test_invalid_view_fails_clearly(self) -> None:
        with self.assertRaises(ValueError):
            create_analytics_figure(self.rows, self.settings, view="invalid")  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
