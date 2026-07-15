"""
Module: analytics tests
Purpose: Verify dashboard goals, streaks, trends, and gap-aware chart series.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Minimal deps; comments in ENGLISH; emojis sparingly.
"""

from __future__ import annotations

import unittest
from datetime import date, timedelta

from novafit.analytics import build_daily_series, calculate_dashboard, calculate_tracking_streak
from novafit.config import AppSettings
from novafit.models import HealthEntry


class AnalyticsTests(unittest.TestCase):
    """Protect deterministic calculations used by CLI and GUI."""

    def test_dashboard_goal_and_best_day(self) -> None:
        rows = [
            HealthEntry.build("2026-07-14", 8000, 1.5, 1800, "Calm"),
            HealthEntry.build("2026-07-15", 12000, 2.5, 2200, "Focused"),
        ]
        stats = calculate_dashboard(rows, AppSettings(step_goal=10000, water_goal_l=2.0))
        self.assertEqual(stats.entry_count, 2)
        self.assertEqual(stats.step_goal_days, 1)
        self.assertEqual(stats.water_goal_days, 1)
        self.assertEqual(stats.best_steps, 12000)
        self.assertEqual(stats.current_streak_days, 2)

    def test_streak_breaks_on_missing_day(self) -> None:
        rows = [
            HealthEntry.build("2026-07-13", 1, 1),
            HealthEntry.build("2026-07-15", 1, 1),
        ]
        self.assertEqual(calculate_tracking_streak(rows), 1)

    def test_recent_change_uses_two_seven_record_windows(self) -> None:
        first = date(2026, 7, 1)
        rows = [
            HealthEntry.build(first + timedelta(days=index), 1000 if index < 7 else 2000, 1)
            for index in range(14)
        ]
        stats = calculate_dashboard(rows)
        self.assertEqual(stats.recent_step_change_pct, 100.0)

    def test_daily_series_fills_missing_dates(self) -> None:
        rows = [HealthEntry.build("2026-07-15", 5000, 2)]
        series = build_daily_series(rows, 3, end_date=date(2026, 7, 15))
        self.assertEqual([item["steps"] for item in series], [0, 0, 5000])


if __name__ == "__main__":
    unittest.main()
