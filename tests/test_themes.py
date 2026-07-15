"""
Module: theme tests
Purpose: Verify every curated UI/chart theme and legacy alias remains valid.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Standard-library assertions; comments in ENGLISH; emojis sparingly.
"""

from __future__ import annotations

import unittest

from novafit.charts import resolve_chart_theme
from novafit.config import AppSettings
from novafit.themes import (
    accessible_text_color,
    contrast_ratio,
    get_theme,
    next_theme,
    normalize_theme_id,
    theme_ids,
    theme_labels,
)


class ThemeTests(unittest.TestCase):
    """Protect the eight-theme public contract."""

    def test_all_theme_palettes_are_complete(self) -> None:
        required_ui = {
            "bg",
            "panel",
            "panel_alt",
            "text",
            "muted",
            "accent",
            "accent_alt",
            "success",
            "warning",
            "danger",
            "border",
            "blue",
            "pink",
        }
        required_chart = {
            "background",
            "panel",
            "panel_alt",
            "text",
            "muted",
            "grid",
            "cyan",
            "blue",
            "purple",
            "green",
            "amber",
            "pink",
            "red",
        }
        self.assertGreaterEqual(len(theme_ids()), 8)
        for theme_id in theme_ids():
            theme = get_theme(theme_id)
            self.assertTrue(required_ui.issubset(theme.ui))
            self.assertTrue(required_chart.issubset(theme.chart))
            self.assertTrue(theme.label)

    def test_legacy_dark_and_light_aliases_migrate(self) -> None:
        self.assertEqual(normalize_theme_id("dark"), "midnight")
        self.assertEqual(normalize_theme_id("light"), "cloud")
        self.assertEqual(AppSettings(theme="dark").validate().theme, "midnight")
        self.assertNotEqual(resolve_chart_theme("dark").background, resolve_chart_theme("light").background)

    def test_display_labels_and_cycle(self) -> None:
        self.assertIn("Aurora Borealis", theme_labels())
        self.assertEqual(next_theme("midnight"), "aurora")
        self.assertEqual(normalize_theme_id("Negev Sunrise"), "desert")

    def test_action_surfaces_always_receive_accessible_text(self) -> None:
        for theme_id in theme_ids():
            palette = get_theme(theme_id).ui
            for role in ("accent", "accent_alt", "danger", "warning"):
                foreground = accessible_text_color(palette[role])
                self.assertGreaterEqual(
                    contrast_ratio(palette[role], foreground),
                    4.5,
                    f"{theme_id}.{role}",
                )


if __name__ == "__main__":
    unittest.main()
