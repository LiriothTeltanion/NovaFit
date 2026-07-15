"""
Module: training atlas tests
Purpose: Verify the fourth analytics view and its theme/export compatibility.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Matplotlib uses the non-interactive Agg backend.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

from novafit.charts import create_dashboard_figure, normalize_chart_view, save_dashboard_chart
from novafit.config import AppSettings
from novafit.models import HealthEntry


class TrainingAtlasTests(unittest.TestCase):
    """Protect the new Training Atlas visualization."""

    def setUp(self) -> None:
        self.entries = [HealthEntry.build(f"2026-07-{day:02d}", 6000 + day * 300, 1.4 + day * 0.05, mood="Focused") for day in range(1, 15)]

    def test_atlas_alias_normalizes(self) -> None:
        self.assertEqual(normalize_chart_view("atlas"), "training_atlas")

    def test_training_atlas_has_five_axes(self) -> None:
        figure = create_dashboard_figure(self.entries, AppSettings(), view="training_atlas", theme="sapphire", days=14)
        self.assertGreaterEqual(len(figure.axes), 5)

    def test_training_atlas_exports_png(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "atlas.png"
            save_dashboard_chart(self.entries, AppSettings(), path, view="training_atlas", theme="arcade", days=14)
            self.assertGreater(path.stat().st_size, 20000)


if __name__ == "__main__":
    unittest.main()
