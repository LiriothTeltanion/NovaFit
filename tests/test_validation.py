"""
Module: validation tests
Purpose: Protect NovaFit user-input boundaries and date parsing behavior.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Minimal deps; comments in ENGLISH; emojis sparingly.
"""

from __future__ import annotations

import unittest

from novafit.models import HealthEntry
from novafit.validation import parse_iso_date


class ValidationTests(unittest.TestCase):
    """Verify accepted values and actionable validation failures."""

    def test_build_valid_entry(self) -> None:
        entry = HealthEntry.build("2026-07-15", "8500", "2.4", "2000", " Focused ", " Good day ")
        self.assertEqual(entry.steps, 8500)
        self.assertEqual(entry.water_l, 2.4)
        self.assertEqual(entry.mood, "Focused")
        self.assertEqual(entry.note, "Good day")

    def test_rejects_invalid_date(self) -> None:
        with self.assertRaisesRegex(ValueError, "YYYY-MM-DD"):
            parse_iso_date("15/07/2026")

    def test_rejects_negative_steps(self) -> None:
        with self.assertRaisesRegex(ValueError, "cannot be negative"):
            HealthEntry.build("2026-07-15", -1, 2.0)

    def test_optional_values_can_be_empty(self) -> None:
        entry = HealthEntry.build("2026-07-15", 0, 0, "", "", "")
        self.assertIsNone(entry.calories)
        self.assertIsNone(entry.mood)
        self.assertIsNone(entry.note)


if __name__ == "__main__":
    unittest.main()
