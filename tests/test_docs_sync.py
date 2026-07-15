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


if __name__ == "__main__":
    unittest.main()
