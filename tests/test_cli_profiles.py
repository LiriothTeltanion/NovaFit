"""
Module: profile CLI tests
Purpose: Verify user creation, selection, listing, and recommendation commands.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Uses temporary SQLite files and captured stdout.
"""

from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from novafit.cli import main


class ProfileCliTests(unittest.TestCase):
    """Protect expanded CLI profile workflows."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db = Path(self.temp_dir.name) / "cli.db"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_cli(self, *args: str) -> tuple[int, str]:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            result = main(["--db", str(self.db), *args])
        return result, buffer.getvalue()

    def test_create_and_list_profile(self) -> None:
        result, _ = self.run_cli("--create-user", "Guest", "--language", "es", "--theme", "sapphire")
        self.assertEqual(result, 0)
        result, output = self.run_cli("--profiles")
        self.assertEqual(result, 0)
        self.assertIn("Guest", output)

    def test_profile_records_are_selected_by_name(self) -> None:
        self.run_cli("--create-user", "Guest")
        result, _ = self.run_cli("--user", "Guest", "--sample")
        self.assertEqual(result, 0)
        _, primary = self.run_cli("--user", "Primary User", "--dashboard")
        self.assertIn("No health entries yet", primary)

    def test_recommendations_command(self) -> None:
        result, output = self.run_cli("--recommendations")
        self.assertEqual(result, 0)
        self.assertIn("SPORT & DATA COACH", output)

    def test_training_atlas_cli_export(self) -> None:
        path = Path(self.temp_dir.name) / "atlas.png"
        self.run_cli("--sample")
        result, _ = self.run_cli("--chart", str(path), "--chart-view", "atlas", "--chart-theme", "lime")
        self.assertEqual(result, 0)
        self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()
