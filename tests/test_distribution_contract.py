"""
Module: distribution contract tests
Purpose: Protect the checker behavior that preserves user databases in a
    workspace while enforcing clean release archives.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Source-contract tests prevent regression of the reported Windows failure.
"""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class DistributionContractTests(unittest.TestCase):
    """Validate workspace-safe and release-strict audit behavior."""

    def test_package_audit_has_explicit_strict_distribution_mode(self) -> None:
        """Require an explicit release-staging safety flag."""
        source = (ROOT / "tools" / "package_audit.py").read_text(encoding="utf-8")
        self.assertIn("--strict-distribution", source)
        self.assertIn("strict_distribution=args.strict_distribution", source)

    def test_runtime_database_is_allowed_only_in_workspace_mode(self) -> None:
        """Protect the distinction between user workspace and release staging."""
        source = (ROOT / "tools" / "package_audit.py").read_text(encoding="utf-8")
        self.assertIn('RUNTIME_ROOTS = {NOVAFIT / "data"}', source)
        self.assertIn("if is_runtime and not strict_distribution", source)
        self.assertIn("Release packaging excludes NovaFit/data runtime files", source)

    def test_default_checker_does_not_run_strict_mode_on_user_workspace(self) -> None:
        """Ensure VERIFY_ALL preserves an existing local database."""
        launcher = (ROOT / "VERIFY_ALL.bat").read_text(encoding="utf-8")
        self.assertIn("tools\\package_audit.py", launcher)
        self.assertNotIn("--strict-distribution", launcher)


if __name__ == "__main__":
    unittest.main()
