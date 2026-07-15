"""
Module: offline report tests
Purpose: Verify the portable HTML report embeds analytics and escapes private text safely.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Minimal deps; comments in ENGLISH; emojis sparingly.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

from novafit.config import AppSettings
from novafit.models import HealthEntry
from novafit.reporting import export_html_report


class ReportingTests(unittest.TestCase):
    """Protect the self-contained offline report contract."""

    def test_report_embeds_chart_and_escapes_note(self) -> None:
        rows = [HealthEntry.build("2026-07-15", 10000, 2.5, 2000, "Focused", "<script>alert(1)</script>")]
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "report.html"
            export_html_report(rows, AppSettings(), destination, days=7)
            content = destination.read_text(encoding="utf-8")
            self.assertIn("data:image/png;base64,", content)
            self.assertIn("&lt;script&gt;", content)
            self.assertNotIn("<script>alert(1)</script>", content)

    def test_empty_report_is_still_valid(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "empty.html"
            export_html_report([], AppSettings(), destination, days=7)
            content = destination.read_text(encoding="utf-8")
            self.assertIn("No health records were available", content)
            self.assertIn("NovaFit", content)


if __name__ == "__main__":
    unittest.main()
