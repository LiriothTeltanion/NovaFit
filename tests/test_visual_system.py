"""
Module: visual-system tests
Purpose: Protect efficient canvas motion, responsive chart density, and the
    theme-aware icon contract without requiring a desktop display.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-16 | TZ: Asia/Jerusalem
"""

from __future__ import annotations

import inspect
import unittest

from novafit.charts import _figure_scale, _format_steps
from novafit.icon_factory import ICON_NAMES, IconFactory
from novafit.motivation_panel import MotivationCenterPanel
from novafit.recommendations_panel import RecommendationsPanel
from novafit.themes import get_theme
from novafit.ui_components import (
    ActivityOrbitCanvas,
    FocusBreathingCanvas,
    MotivationGalaxyCanvas,
    NovaPulseCanvas,
    UltimateHeroCanvas,
    _MotionCanvas,
)


class _FigureStub:
    def __init__(self, width: float, height: float) -> None:
        self.width = width
        self.height = height

    def get_figwidth(self) -> float:
        return self.width

    def get_figheight(self) -> float:
        return self.height


class VisualSystemTests(unittest.TestCase):
    """Keep motion lightweight and visual APIs deterministic."""

    def test_every_animated_canvas_uses_shared_lifecycle(self) -> None:
        canvases = (
            NovaPulseCanvas,
            MotivationGalaxyCanvas,
            FocusBreathingCanvas,
            UltimateHeroCanvas,
            ActivityOrbitCanvas,
        )
        for canvas in canvases:
            with self.subTest(canvas=canvas.__name__):
                self.assertTrue(issubclass(canvas, _MotionCanvas))
                self.assertTrue(callable(getattr(canvas, "set_active")))
                self.assertTrue(callable(getattr(canvas, "set_reduced_motion")))

    def test_motion_frames_update_items_instead_of_rebuilding_scene(self) -> None:
        canvases = (
            NovaPulseCanvas,
            MotivationGalaxyCanvas,
            FocusBreathingCanvas,
            UltimateHeroCanvas,
            ActivityOrbitCanvas,
        )
        for canvas in canvases:
            with self.subTest(canvas=canvas.__name__):
                source = inspect.getsource(canvas._render_motion)
                self.assertNotIn("delete(", source)
                self.assertIn("coords(", source)

    def test_chart_typography_scales_but_keeps_accessible_floor(self) -> None:
        compact = _figure_scale(_FigureStub(7.2, 4.1))
        standard = _figure_scale(_FigureStub(14.8, 8.5))
        oversized = _figure_scale(_FigureStub(30.0, 20.0))
        self.assertEqual(compact, 0.78)
        self.assertAlmostEqual(standard, 1.0)
        self.assertEqual(oversized, 1.08)

    def test_step_axis_labels_keep_small_values_meaningful(self) -> None:
        self.assertEqual(_format_steps(750), "750")
        self.assertEqual(_format_steps(1_250), "1.2k")
        self.assertEqual(_format_steps(12_500), "12k")

    def test_every_icon_renders_as_antialiased_rgba(self) -> None:
        palette = get_theme("midnight").ui
        for name in ICON_NAMES:
            with self.subTest(icon=name):
                image = IconFactory.render(name, palette, 28)
                self.assertEqual(image.mode, "RGBA")
                self.assertEqual(image.size, (28, 28))
                self.assertIsNotNone(image.getbbox())

    def test_icon_aliases_and_invalid_values_are_explicit(self) -> None:
        self.assertEqual(IconFactory._validate("user", 28, "default"), "profiles")
        self.assertEqual(IconFactory._validate("analytics", 28, "active"), "dashboard")
        with self.assertRaisesRegex(ValueError, "Unsupported icon"):
            IconFactory._validate("mystery", 28, "default")
        with self.assertRaisesRegex(ValueError, "Icon state"):
            IconFactory._validate("dashboard", 28, "hovered")

    def test_panel_canvases_receive_the_active_language_at_construction(self) -> None:
        motivation_source = inspect.getsource(MotivationCenterPanel._build_content)
        recommendations_source = inspect.getsource(RecommendationsPanel._build)
        self.assertIn("language=self.language", motivation_source)
        self.assertIn("language=language", recommendations_source)


if __name__ == "__main__":
    unittest.main()
