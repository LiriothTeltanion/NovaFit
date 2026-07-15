"""
Module: multi-profile database tests
Purpose: Verify isolated users, preference persistence, and legacy row migration.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Disposable SQLite files only; no personal data.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from novafit.database import NovaFitDatabase
from novafit.models import HealthEntry, UserProfile


class ProfileDatabaseTests(unittest.TestCase):
    """Exercise multi-profile behavior through a temporary database."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db = NovaFitDatabase(Path(self.temp_dir.name) / "profiles.db")
        self.db.initialize()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_default_profile_exists(self) -> None:
        profiles = self.db.list_profiles()
        self.assertEqual(profiles[0].profile_id, 1)
        self.assertEqual(profiles[0].display_name, "Primary User")

    def test_profiles_keep_same_date_isolated(self) -> None:
        guest = self.db.create_profile(UserProfile.build("Guest", language="es"))
        self.db.upsert(HealthEntry.build("2026-07-15", 1000, 1.0), profile_id=1)
        self.db.upsert(HealthEntry.build("2026-07-15", 9000, 2.5), profile_id=guest.profile_id)
        self.assertEqual(self.db.get("2026-07-15", profile_id=1).steps, 1000)
        self.assertEqual(self.db.get("2026-07-15", profile_id=guest.profile_id).steps, 9000)

    def test_active_profile_scopes_default_crud(self) -> None:
        guest = self.db.create_profile(UserProfile.build("Guest"))
        self.db.set_active_profile(guest.profile_id or 1)
        self.db.upsert(HealthEntry.build("2026-07-15", 7000, 2.0))
        self.assertEqual(self.db.count(), 1)
        self.db.set_active_profile(1)
        self.assertEqual(self.db.count(), 0)

    def test_profile_preferences_round_trip(self) -> None:
        created = self.db.create_profile(
            UserProfile.build(
                "Lirioth",
                language="he",
                theme="sapphire",
                activity_level="active",
                sport_focus="cycling",
                step_goal=12000,
            )
        )
        read = self.db.get_profile(created.profile_id or 0)
        self.assertEqual(read.language, "he")
        self.assertEqual(read.theme, "sapphire")
        self.assertEqual(read.sport_focus, "cycling")
        self.assertEqual(read.step_goal, 12000)

    def test_primary_profile_is_protected(self) -> None:
        with self.assertRaises(ValueError):
            self.db.delete_profile(1)


if __name__ == "__main__":
    unittest.main()
