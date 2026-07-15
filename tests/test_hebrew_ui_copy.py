"""
Module: Hebrew UI copy tests
Purpose: Protect localized analytics insights and stable localized profile values.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-16 | TZ: Asia/Jerusalem
Notes: No display server is required; panel helpers are exercised without Tk setup.
"""

from __future__ import annotations

import unittest

from novafit.analytics import DashboardStats
from novafit.config import AppSettings
from novafit.dashboard_panel import DashboardPanel
from novafit.profile_panel import ProfileManagerPanel


class HebrewUiCopyTests(unittest.TestCase):
    """Verify RTL-facing helpers without constructing desktop windows."""

    def test_empty_dashboard_insights_are_fully_hebrew(self) -> None:
        panel = object.__new__(DashboardPanel)
        panel.language = "he"
        panel._stats = DashboardStats.empty()
        lines = panel._localized_insight_lines()
        self.assertEqual(len(lines), 4)
        self.assertTrue(all(any("\u0590" <= character <= "\u05ff" for character in line) for line in lines))

    def test_localized_profile_label_resolves_to_stable_value(self) -> None:
        labels = {"beginner": "התחלה מתונה", "balanced": "מאוזנת", "active": "פעילה"}
        self.assertEqual(ProfileManagerPanel._value_from_label("מאוזנת", labels), "balanced")
        self.assertEqual(ProfileManagerPanel._value_from_label("custom", labels), "custom")

    def test_hebrew_dashboard_insight_translates_weekday_and_mood(self) -> None:
        panel = object.__new__(DashboardPanel)
        panel.language = "he"
        panel.settings = AppSettings(language="he")
        panel._stats = DashboardStats.empty()
        self.assertEqual(panel._localized_option("weekday", "Sunday"), "יום ראשון")
        self.assertEqual(panel._localized_option("mood", "Focused"), "ממוקד")


if __name__ == "__main__":
    unittest.main()
