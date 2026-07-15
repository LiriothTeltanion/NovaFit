"""
Module: import/export tests
Purpose: Protect JSON/CSV portability, duplicate strategies, and starter data.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Minimal deps; comments in ENGLISH; emojis sparingly.
"""

from __future__ import annotations

import json
import csv
import tempfile
import unittest
from pathlib import Path

from novafit.database import NovaFitDatabase
from novafit.io_utils import export_csv, export_json, import_csv, import_json, initialize_sample_data
from novafit.models import HealthEntry


class ImportExportTests(unittest.TestCase):
    """Round-trip records through temporary JSON and CSV files."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.source = NovaFitDatabase(self.root / "source.db")
        self.target = NovaFitDatabase(self.root / "target.db")
        self.source.initialize()
        self.target.initialize()
        self.source.upsert(HealthEntry.build("2026-07-15", 8500, 2.2, 1900, "Focused", "Test"))

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_json_round_trip_and_metadata(self) -> None:
        path = self.root / "backup.json"
        self.assertEqual(export_json(self.source, path), 1)
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["metadata"]["schema"], "novafit-health-export-v2")
        result = import_json(self.target, path)
        self.assertEqual(result.imported, 1)
        self.assertEqual(self.target.get("2026-07-15").note, "Test")

    def test_csv_round_trip(self) -> None:
        path = self.root / "backup.csv"
        self.assertEqual(export_csv(self.source, path), 1)
        result = import_csv(self.target, path)
        self.assertEqual(result.imported, 1)
        self.assertEqual(self.target.get("2026-07-15").steps, 8500)

    def test_skip_strategy_preserves_existing_date(self) -> None:
        path = self.root / "backup.json"
        export_json(self.source, path)
        self.target.upsert(HealthEntry.build("2026-07-15", 1, 1))
        result = import_json(self.target, path, strategy="skip")
        self.assertEqual(result.skipped, 1)
        self.assertEqual(self.target.get("2026-07-15").steps, 1)

    def test_invalid_rows_are_counted(self) -> None:
        path = self.root / "bad.json"
        path.write_text(json.dumps([{"date": "bad", "steps": 1, "water_l": 1}]), encoding="utf-8")
        result = import_json(self.target, path)
        self.assertEqual(result.invalid, 1)
        self.assertEqual(result.imported, 0)

    def test_starter_data_does_not_duplicate_dates(self) -> None:
        first = initialize_sample_data(self.target)
        second = initialize_sample_data(self.target)
        self.assertEqual(first, 7)
        self.assertEqual(second, 0)

    def test_csv_export_neutralizes_spreadsheet_formulas(self) -> None:
        self.source.upsert(HealthEntry.build("2026-07-16", 1, 1, mood="=HYPERLINK('bad')", note="@danger"))
        path = self.root / "safe.csv"
        export_csv(self.source, path)
        with path.open("r", newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.DictReader(handle))
        risky = next(row for row in rows if row["Date"] == "2026-07-16")
        self.assertTrue(risky["Mood"].startswith("'="))
        self.assertTrue(risky["Note"].startswith("'@"))


if __name__ == "__main__":
    unittest.main()
