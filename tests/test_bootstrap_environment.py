"""Tests for safe, OneDrive-tolerant generated-environment repair."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.bootstrap_environment import remove_generated_environment


class BootstrapEnvironmentTests(unittest.TestCase):
    """Protect generated-directory cleanup without risking source or data."""

    def test_generated_venv_can_be_removed(self) -> None:
        """A positively identified external venv is a valid repair target."""
        with tempfile.TemporaryDirectory() as temp_dir:
            environment = Path(temp_dir) / "generated-venv"
            cache = environment / "Lib" / "site-packages" / "demo" / "__pycache__"
            cache.mkdir(parents=True)
            (environment / "pyvenv.cfg").write_text("version = 3.14\n", encoding="utf-8")
            (cache / "demo.pyc").write_bytes(b"generated")

            remove_generated_environment(environment)

            self.assertFalse(environment.exists())

    def test_arbitrary_directory_is_never_removed(self) -> None:
        """A directory without a venv marker remains untouched."""
        with tempfile.TemporaryDirectory() as temp_dir:
            arbitrary = Path(temp_dir) / "personal-data"
            arbitrary.mkdir()
            marker = arbitrary / "keep.txt"
            marker.write_text("keep", encoding="utf-8")

            with self.assertRaises(RuntimeError):
                remove_generated_environment(arbitrary)

            self.assertEqual(marker.read_text(encoding="utf-8"), "keep")


if __name__ == "__main__":
    unittest.main()
