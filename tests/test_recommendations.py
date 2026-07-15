"""
Module: recommendation engine tests
Purpose: Verify grounded, conservative, multilingual sport and data suggestions.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Recommendations remain general and non-medical.
"""

from __future__ import annotations

import unittest

from novafit.config import AppSettings
from novafit.models import HealthEntry, UserProfile
from novafit.recommendations import build_recommendation_plan, format_recommendation_plan


class RecommendationTests(unittest.TestCase):
    """Protect data confidence and safety boundaries."""

    def test_empty_archive_has_zero_confidence(self) -> None:
        plan = build_recommendation_plan([], AppSettings(), UserProfile.build("Demo"))
        self.assertEqual(plan.data_confidence_pct, 0)
        self.assertTrue(any(item.category == "data" for item in plan.items))

    def test_low_steps_produce_gradual_movement_action(self) -> None:
        entries = [HealthEntry.build(f"2026-07-{day:02d}", 2500, 2.0) for day in range(1, 8)]
        plan = build_recommendation_plan(entries, AppSettings(step_goal=10000), UserProfile.build("Demo"))
        movement = next(item for item in plan.items if item.category == "movement")
        self.assertIn("10-minute", movement.action)

    def test_hydration_recommendation_uses_recorded_average(self) -> None:
        entries = [HealthEntry.build(f"2026-07-{day:02d}", 8000, 0.8) for day in range(1, 8)]
        plan = build_recommendation_plan(entries, AppSettings(water_goal_l=2.0), UserProfile.build("Demo"))
        self.assertTrue(any(item.category == "hydration" for item in plan.items))

    def test_spanish_and_hebrew_outputs_are_localized(self) -> None:
        spanish = build_recommendation_plan([], AppSettings(), UserProfile.build("Demo", language="es"), "es")
        hebrew = build_recommendation_plan([], AppSettings(), UserProfile.build("Demo", language="he"), "he")
        self.assertIn("registros", spanish.summary)
        self.assertIn("רישומים", hebrew.summary)

    def test_terminal_report_keeps_scope_boundary(self) -> None:
        profile = UserProfile.build("Demo")
        plan = build_recommendation_plan([], AppSettings(), profile)
        report = format_recommendation_plan(plan, profile)
        self.assertIn("DATA CONFIDENCE", report)
        self.assertIn("not medical advice", report)


if __name__ == "__main__":
    unittest.main()
