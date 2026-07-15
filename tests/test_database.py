"""
Module: database tests
Purpose: Verify SQLite CRUD, ranges, upserts, and legacy-compatible initialization.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Minimal deps; comments in ENGLISH; emojis sparingly.
"""

from __future__ import annotations

import sqlite3
import tempfile
from contextlib import closing
import unittest
from pathlib import Path

from novafit.database import NovaFitDatabase
from novafit.models import HealthEntry


class DatabaseTests(unittest.TestCase):
    """Exercise the database through a disposable file per test."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db = NovaFitDatabase(Path(self.temp_dir.name) / "novafit.db")
        self.db.initialize()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_upsert_get_list_and_count(self) -> None:
        self.db.upsert(HealthEntry.build("2026-07-15", 8000, 2.0, 1900, "Calm"))
        self.db.upsert(HealthEntry.build("2026-07-15", 9000, 2.5, 2000, "Focused"))
        entry = self.db.get("2026-07-15")
        self.assertIsNotNone(entry)
        self.assertEqual(entry.steps, 9000)
        self.assertEqual(self.db.count(), 1)
        self.assertEqual(len(self.db.list(None)), 1)

    def test_insert_if_missing_preserves_existing_record(self) -> None:
        first = HealthEntry.build("2026-07-15", 100, 1)
        second = HealthEntry.build("2026-07-15", 999, 9)
        self.assertTrue(self.db.insert_if_missing(first))
        self.assertFalse(self.db.insert_if_missing(second))
        self.assertEqual(self.db.get("2026-07-15").steps, 100)

    def test_search_delete_and_clear(self) -> None:
        for day in ("2026-07-13", "2026-07-14", "2026-07-15"):
            self.db.upsert(HealthEntry.build(day, 1000, 1.0))
        self.assertEqual(len(self.db.search("2026-07-14", "2026-07-15")), 2)
        self.assertTrue(self.db.delete("2026-07-14"))
        self.assertFalse(self.db.delete("2026-07-14"))
        self.assertEqual(self.db.clear(), 2)
        self.assertEqual(self.db.count(), 0)

    def test_migrates_legacy_table_columns(self) -> None:
        legacy_path = Path(self.temp_dir.name) / "legacy.db"
        with closing(sqlite3.connect(legacy_path)) as connection:
            connection.execute(
                "CREATE TABLE logs (id INTEGER PRIMARY KEY, date TEXT UNIQUE, steps INTEGER, water_l REAL, calories INTEGER, mood TEXT)"
            )
            connection.execute(
                "INSERT INTO logs(date, steps, water_l, calories, mood) VALUES('2025-10-14', 8500, 2.1, 1850, 'Happy')"
            )
            connection.commit()
        legacy = NovaFitDatabase(legacy_path)
        legacy.initialize()
        entry = legacy.get("2025-10-14")
        self.assertIsNotNone(entry)
        self.assertEqual(entry.steps, 8500)


if __name__ == "__main__":
    unittest.main()
