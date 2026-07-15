"""
Module: internationalization tests
Purpose: Verify language normalization, translated navigation, and Hebrew RTL.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Standard-library tests only.
"""

from __future__ import annotations

import unittest

from novafit.i18n import TRANSLATIONS, direction_for, language_labels, normalize_language, tr


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

    def test_every_supported_language_has_the_same_keys(self) -> None:
        english_keys = set(TRANSLATIONS["en"])
        self.assertEqual(set(TRANSLATIONS["es"]), english_keys)
        self.assertEqual(set(TRANSLATIONS["he"]), english_keys)

    def test_advanced_hebrew_panels_do_not_fall_back_to_english(self) -> None:
        expected_hebrew = {
            "refresh_charts": "רענון",
            "profile_header": "פרופילים",
            "motivation_focus_reset": "איפוס",
            "export_recommendations": "ייצוא",
            "record_rules": "רישום",
            "about_body": "יישום",
        }
        for key, fragment in expected_hebrew.items():
            with self.subTest(key=key):
                self.assertIn(fragment, tr("he", key, profile="קווין", version="4.0"))

    def test_hebrew_dynamic_copy_formats_names_and_paths(self) -> None:
        self.assertEqual(tr("he", "profile_created", name="קווין"), "הפרופיל קווין נוצר בהצלחה ✅")
        self.assertIn("C:/NovaFit", tr("he", "dashboard_saved", path="C:/NovaFit"))


if __name__ == "__main__":
    unittest.main()
