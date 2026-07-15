"""Behavioral tests for workspace-safe and release-strict package audits."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from tools.package_audit import audit_distribution_files

ROOT = Path(__file__).resolve().parent.parent


class DistributionContractTests(unittest.TestCase):
    """Validate workspace-safe and release-strict audit behavior."""

    def test_runtime_database_is_preserved_in_workspace_mode(self) -> None:
        """A workspace audit must report but never reject or delete user data."""
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            database = root / "data" / "novafit.db"
            database.parent.mkdir()
            database.write_bytes(b"SQLite format 3\x00")

            report = audit_distribution_files(root, strict_distribution=False)

            self.assertFalse(report.errors)
            self.assertTrue(database.exists())
            self.assertTrue(any("preserved" in finding.message for finding in report.findings))

    def test_runtime_database_is_rejected_in_strict_distribution_mode(self) -> None:
        """A copied release-staging tree must not contain mutable user data."""
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            database = root / "data" / "novafit.db"
            database.parent.mkdir()
            database.write_bytes(b"SQLite format 3\x00")

            report = audit_distribution_files(root, strict_distribution=True)

            self.assertEqual(len(report.errors), 1)
            self.assertIn("runtime files", report.errors[0].message)
            self.assertTrue(database.exists(), "Audits must never delete user data.")

    def test_credentials_are_rejected_in_every_mode(self) -> None:
        """A credential-like file is unsafe even outside release staging."""
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            secret = root / ".env"
            secret.write_text("TOKEN=not-a-real-token\n", encoding="utf-8")

            report = audit_distribution_files(root, strict_distribution=False)

            self.assertEqual(len(report.errors), 1)
            self.assertIn("Credential/private", report.errors[0].message)

    def test_default_checker_does_not_run_strict_mode_on_user_workspace(self) -> None:
        """Ensure VERIFY_ALL preserves an existing local database."""
        launcher = (ROOT / "VERIFY_ALL.bat").read_text(encoding="utf-8")
        self.assertIn("tools\\package_audit.py", launcher)
        self.assertNotIn("--strict-distribution", launcher)


if __name__ == "__main__":
    unittest.main()
