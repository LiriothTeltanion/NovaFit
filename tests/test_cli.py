"""
Module: CLI tests
Purpose: Verify parser defaults and key automation actions without launching Tkinter.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Minimal deps; comments in ENGLISH; emojis sparingly.
"""

from __future__ import annotations

import tempfile
import unittest

import matplotlib

matplotlib.use("Agg")
from pathlib import Path

from novafit.cli import build_parser, main
from novafit.backup import inspect_complete_backup


class CliTests(unittest.TestCase):
    """Protect the documented command-line contract."""

    def test_parser_accepts_add_contract(self) -> None:
        args = build_parser().parse_args(["--add", "2026-07-15", "--steps", "9000", "--water", "2.5"])
        self.assertEqual(args.add, "2026-07-15")
        self.assertEqual(args.steps, 9000)

    def test_sample_and_dashboard_commands(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "cli.db"
            self.assertEqual(main(["--db", str(db_path), "--sample"]), 0)
            self.assertEqual(main(["--db", str(db_path), "--dashboard"]), 0)

    def test_motivation_command(self) -> None:
        """Verify the Motivation Center CLI route succeeds."""
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "cli.db"
            self.assertEqual(main(["--db", str(db_path), "--sample"]), 0)
            self.assertEqual(main(["--db", str(db_path), "--motivation"]), 0)

    def test_chart_and_html_report_commands(self) -> None:
        """Verify documented analytics exports through the CLI."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            db_path = root / "cli.db"
            chart_path = root / "trends.png"
            report_path = root / "report.html"
            self.assertEqual(main(["--db", str(db_path), "--sample"]), 0)
            self.assertEqual(
                main(
                    [
                        "--db",
                        str(db_path),
                        "--chart",
                        str(chart_path),
                        "--chart-view",
                        "trends",
                        "--chart-days",
                        "30",
                    ]
                ),
                0,
            )
            self.assertEqual(
                main(
                    [
                        "--db",
                        str(db_path),
                        "--report-html",
                        str(report_path),
                        "--chart-view",
                        "consistency",
                        "--chart-days",
                        "30",
                    ]
                ),
                0,
            )
            self.assertGreater(chart_path.stat().st_size, 20_000)
            self.assertIn("data:image/png;base64,", report_path.read_text(encoding="utf-8"))

    def test_complete_backup_command(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            database = root / "cli.db"
            backup = root / "complete.zip"
            self.assertEqual(main(["--db", str(database), "--sample"]), 0)
            self.assertEqual(main(["--db", str(database), "--backup", str(backup)]), 0)
            self.assertEqual(
                inspect_complete_backup(backup)["schema"],
                "novafit-complete-backup-v3",
            )


if __name__ == "__main__":
    unittest.main()
