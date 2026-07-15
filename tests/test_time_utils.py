"""
Module: timezone tests
Purpose: Ensure export timestamps remain aware and Windows fallback stays safe.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Standard-library tests; comments in ENGLISH; emojis sparingly.
"""

from __future__ import annotations

import unittest
from unittest.mock import patch
from zoneinfo import ZoneInfoNotFoundError

from novafit.time_utils import application_timezone, now_local, timestamp_label


class TimeUtilsTests(unittest.TestCase):
    """Protect timezone behavior with and without the tzdata package."""

    def test_normal_timestamp_is_timezone_aware(self) -> None:
        self.assertIsNotNone(now_local().tzinfo)
        self.assertTrue(timestamp_label())

    def test_missing_iana_database_falls_back_softly(self) -> None:
        with patch("novafit.time_utils.ZoneInfo", side_effect=ZoneInfoNotFoundError("missing")):
            self.assertIsNotNone(application_timezone())
            self.assertIn("fallback", timestamp_label())


if __name__ == "__main__":
    unittest.main()
