"""
Module: environment contract tests
Purpose: Protect the Windows repair workflow against the exact missing-package
    and timezone regressions that previously broke verification.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Standard library only; comments in ENGLISH; emojis sparingly.
"""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class EnvironmentContractTests(unittest.TestCase):
    """Verify the distributable dependency and Windows launcher contract.

    Example:
        >>> suite = unittest.defaultTestLoader.loadTestsFromTestCase(EnvironmentContractTests)
        >>> suite.countTestCases()
        3
    """

    def test_requirements_include_chart_and_timezone_dependencies(self) -> None:
        """Require packages implicated by the original Windows failure.

        Returns:
            None.

        Example:
            >>> EnvironmentContractTests('test_requirements_include_chart_and_timezone_dependencies').run().wasSuccessful()
            True
        """
        requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8").lower()
        self.assertIn("matplotlib", requirements)
        self.assertIn("pillow", requirements)
        self.assertIn("tzdata", requirements)

    def test_bootstrap_uses_local_venv_and_supported_fallbacks(self) -> None:
        """Protect local-environment repair and interpreter fallback behavior.

        Returns:
            None.

        Example:
            >>> EnvironmentContractTests('test_bootstrap_uses_local_venv_and_supported_fallbacks').run().wasSuccessful()
            True
        """
        launcher = (ROOT / "bootstrap_windows.bat").read_text(encoding="utf-8").lower()
        self.assertIn(".venv\\scripts\\python.exe", launcher)
        self.assertIn("--force-recreate", launcher)
        self.assertIn("3.13 3.14 3.12 3.11 3.10", launcher)
        self.assertIn("bootstrap_environment.py", launcher)

    def test_verifier_runs_with_the_repaired_interpreter(self) -> None:
        """Ensure tests never silently fall back to the global Python command.

        Returns:
            None.

        Example:
            >>> EnvironmentContractTests('test_verifier_runs_with_the_repaired_interpreter').run().wasSuccessful()
            True
        """
        launcher = (ROOT / "verify_windows.bat").read_text(encoding="utf-8").lower()
        self.assertIn("call bootstrap_windows.bat", launcher)
        self.assertIn('".venv\\scripts\\python.exe" scripts\\verify.py', launcher)
        self.assertNotIn(
            "python scripts\\verify.py",
            launcher.replace('".venv\\scripts\\python.exe" scripts\\verify.py', ""),
        )


if __name__ == "__main__":
    unittest.main()
