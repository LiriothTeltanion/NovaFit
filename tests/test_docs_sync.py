"""Protect generated project metadata from documentation drift."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class DocumentationSyncTests(unittest.TestCase):
    def test_generated_project_facts_are_current(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/sync_docs.py", "--check"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout)

    def test_generated_text_artifacts_use_portable_lf_endings(self) -> None:
        """Keep hashes and byte sizes identical on Windows and Linux checkouts."""
        paths = (
            ROOT / "assets" / "novafit-ultimate-banner-animated.svg",
            ROOT / "assets" / "manifest.json",
            ROOT / "portfolio" / "project.json",
            ROOT / "docs" / "PROJECT_FACTS.md",
        )
        for path in paths:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertNotIn(b"\r\n", path.read_bytes())


if __name__ == "__main__":
    unittest.main()
