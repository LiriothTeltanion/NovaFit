"""
Module: motivation tests
Purpose: Protect grounded copy, milestones, achievements, and non-empty CLI output.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Deterministic fixtures; comments in ENGLISH; emojis sparingly.
"""

from __future__ import annotations

import unittest
from datetime import date, timedelta

from novafit.config import AppSettings
from novafit.models import HealthEntry
from novafit.motivation import build_motivation_snapshot, format_motivation


class MotivationTests(unittest.TestCase):
    """Verify motivation stays grounded in active records."""

    def test_empty_archive_invites_one_record(self) -> None:
        settings = AppSettings()
        snapshot = build_motivation_snapshot([], settings, today=date(2026, 7, 15))
        self.assertEqual(snapshot.headline, "Begin with one honest record.")
        self.assertEqual(snapshot.celebration_level, 0)
        self.assertIn("first", snapshot.next_milestone.lower())

    def test_progress_snapshot_uses_real_counts(self) -> None:
        today = date(2026, 7, 15)
        rows = [
            HealthEntry.build((today - timedelta(days=index)).isoformat(), 12_000, 2.5, 2_000, "Focused")
            for index in range(7)
        ]
        snapshot = build_motivation_snapshot(rows, AppSettings(), today=today)
        earned = {item.title for item in snapshot.achievements if item.earned}
        self.assertIn("Week Builder", earned)
        self.assertIn("Rhythm Keeper", earned)
        self.assertIn("7", snapshot.message)
        self.assertGreaterEqual(snapshot.celebration_level, 1)

    def test_spark_rotation_is_deterministic(self) -> None:
        settings = AppSettings()
        first = build_motivation_snapshot([], settings, today=date(2026, 7, 15), spark_offset=0)
        second = build_motivation_snapshot([], settings, today=date(2026, 7, 15), spark_offset=1)
        self.assertNotEqual(first.daily_spark, second.daily_spark)

    def test_terminal_output_includes_personal_why(self) -> None:
        settings = AppSettings(personal_why="Learn steadily for a stronger future.")
        output = format_motivation(build_motivation_snapshot([], settings), settings)
        self.assertIn("MOTIVATION CENTER", output)
        self.assertIn("Learn steadily", output)
        self.assertIn("not medical advice", output)

    def test_hebrew_snapshot_localizes_dynamic_motivation_copy(self) -> None:
        settings = AppSettings(language="he")
        snapshot = build_motivation_snapshot([], settings, today=date(2026, 7, 15))
        self.assertIn("רישום", snapshot.headline)
        self.assertIn("ימים", snapshot.weekly_challenge)
        self.assertTrue(
            all(
                any("\u0590" <= character <= "\u05ff" for character in badge.title)
                for badge in snapshot.achievements
            )
        )

    def test_hebrew_terminal_output_keeps_safety_scope(self) -> None:
        settings = AppSettings(language="he", personal_why="לבנות שגרה יציבה")
        snapshot = build_motivation_snapshot([], settings, today=date(2026, 7, 15))
        output = format_motivation(snapshot, settings)
        self.assertIn("מרכז המוטיבציה", output)
        self.assertIn("לבנות שגרה יציבה", output)
        self.assertIn("אינו ייעוץ רפואי", output)


if __name__ == "__main__":
    unittest.main()
