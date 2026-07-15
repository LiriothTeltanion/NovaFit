"""
Module: internationalization tests
Purpose: Verify language normalization, translated navigation, and Hebrew RTL.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Standard-library tests only.
"""

from __future__ import annotations

import unittest

from novafit.i18n import direction_for, language_labels, normalize_language, tr


class I18nTests(unittest.TestCase):
    """Protect the three-language interface contract."""

    def test_native_labels_are_available(self) -> None:
        self.assertEqual(language_labels(), ("English", "Español", "עברית"))

    def test_language_aliases_normalize(self) -> None:
        self.assertEqual(normalize_language("Spanish"), "es")
        self.assertEqual(normalize_language("עברית"), "he")

    def test_hebrew_is_rtl(self) -> None:
        self.assertEqual(direction_for("he"), "rtl")
        self.assertEqual(direction_for("es"), "ltr")

    def test_translation_fallbacks_are_complete(self) -> None:
        for language in ("en", "es", "he"):
            self.assertTrue(tr(language, "nav_recommendations"))
            self.assertTrue(tr(language, "privacy_body"))


if __name__ == "__main__":
    unittest.main()
