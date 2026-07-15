"""
Module: advanced analytics tests
Purpose: Verify consistency, goal streaks, calendar matrices, weekday rhythms,
    mood summaries, rolling averages, and evidence-based observations.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Minimal deps; comments in ENGLISH; emojis sparingly.
"""

from __future__ import annotations

import unittest
from datetime import date, timedelta

from novafit.analytics import (
    build_calendar_matrix,
    build_insight_lines,
    build_mood_distribution,
    build_weekday_profile,
    calculate_dashboard,
    calculate_longest_goal_streak,
    calculate_longest_tracking_streak,
    rolling_average,
)
from novafit.config import AppSettings
from novafit.models import HealthEntry


class AdvancedAnalyticsTests(unittest.TestCase):
    """Protect deterministic values used by the definitive dashboard."""

    def setUp(self) -> None:
        start = date(2026, 7, 1)
        self.rows = [
            HealthEntry.build(
                start + timedelta(days=index),
                7000 + index * 500,
                1.5 + index * 0.1,
                1800 + index * 20,
                "Focused" if index % 2 == 0 else "Calm",
            )
            for index in range(14)
        ]
        self.settings = AppSettings(step_goal=9000, water_goal_l=2.0)

    def test_longest_tracking_streak_uses_all_history(self) -> None:
        broken = self.rows[:5] + [HealthEntry.build("2026-07-10", 1, 1)]
        self.assertEqual(calculate_longest_tracking_streak(broken), 5)

    def test_longest_goal_streak_uses_both_goals(self) -> None:
        rows = [
            HealthEntry.build("2026-07-01", 10000, 2.0),
            HealthEntry.build("2026-07-02", 10000, 2.0),
            HealthEntry.build("2026-07-03", 1000, 2.0),
        ]
        self.assertEqual(calculate_longest_goal_streak(rows, AppSettings()), 2)

    def test_rolling_average_keeps_leading_gaps(self) -> None:
        self.assertEqual(rolling_average([1, 2, 3, 4], 3), [None, None, 2, 3])

    def test_weekday_profile_always_has_seven_rows(self) -> None:
        profile = build_weekday_profile(self.rows)
        self.assertEqual(len(profile), 7)
        self.assertEqual(profile[0]["weekday"], "Mon")

    def test_calendar_matrix_has_monday_first_rows(self) -> None:
        matrix = build_calendar_matrix(self.rows, self.settings, days=42)
        self.assertEqual(len(matrix.values), 7)
        self.assertEqual(matrix.weekday_labels[0], "Mon")
        self.assertGreaterEqual(len(matrix.week_labels), 6)

    def test_mood_distribution_is_frequency_sorted(self) -> None:
        distribution = build_mood_distribution(self.rows)
        self.assertEqual(distribution[0][1], 7)

    def test_dashboard_exposes_definitive_metrics(self) -> None:
        stats = calculate_dashboard(self.rows, self.settings)
        self.assertEqual(stats.longest_tracking_streak_days, 14)
        self.assertGreater(stats.consistency_score, 0)
        self.assertGreater(stats.tracking_coverage_pct, 0)
        self.assertEqual(stats.latest_date, self.rows[-1].entry_date.isoformat())
        self.assertGreaterEqual(stats.perfect_goal_days, 1)

    def test_insights_are_grounded_and_nonempty(self) -> None:
        stats = calculate_dashboard(self.rows, self.settings)
        lines = build_insight_lines(stats, self.settings)
        self.assertEqual(len(lines), 4)
        self.assertTrue(any("coverage" in line.lower() for line in lines))


if __name__ == "__main__":
    unittest.main()
