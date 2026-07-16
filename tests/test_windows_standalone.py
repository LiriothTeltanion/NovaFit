"""Regression tests for NovaFit's official frozen Windows distribution."""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from novafit.config import PROJECT_ROOT, _resolve_default_data_dir
from scripts.build_windows_distribution import _safe_remove, package_basename
from tools.standalone_audit import audit_standalone, write_manifest

ROOT = Path(__file__).resolve().parent.parent


class FrozenDataPathTests(unittest.TestCase):
    """Protect user data from application replacement and read-only bundles."""

    def test_source_checkout_keeps_existing_data_directory(self) -> None:
        self.assertEqual(_resolve_default_data_dir(frozen=False), PROJECT_ROOT / "data")

    def test_frozen_windows_app_uses_local_app_data(self) -> None:
        path = _resolve_default_data_dir(
            frozen=True,
            environment={"LOCALAPPDATA": r"C:\Users\Example\AppData\Local"},
        )
        self.assertEqual(path, Path(r"C:\Users\Example\AppData\Local") / "NovaFit")

    def test_frozen_app_has_a_home_directory_fallback(self) -> None:
        self.assertEqual(
            _resolve_default_data_dir(frozen=True, environment={}, home=Path("/home/example")),
            Path("/home/example/.novafit"),
        )


class StandaloneBuildContractTests(unittest.TestCase):
    """Validate artifact names, safe cleanup, icon, and workflow wiring."""

    def test_public_artifact_name_is_versioned_and_unambiguous(self) -> None:
        self.assertEqual(
            package_basename("4.2.0"),
            "NovaFit-v4.2.0-Windows-x64-Standalone",
        )

    def test_generated_cleanup_cannot_escape_declared_parent(self) -> None:
        with TemporaryDirectory() as temp_dir:
            parent = Path(temp_dir)
            with self.assertRaises(ValueError):
                _safe_remove(parent, parent)
            with self.assertRaises(ValueError):
                _safe_remove(parent.parent / "outside", parent)

    def test_icon_contains_multiple_windows_resolutions(self) -> None:
        from PIL import Image

        with Image.open(ROOT / "assets" / "novafit.ico") as icon:
            sizes = icon.ico.sizes()
        self.assertIn((16, 16), sizes)
        self.assertIn((64, 64), sizes)
        self.assertIn((256, 256), sizes)

    def test_pwa_icons_share_the_deterministic_windows_master(self) -> None:
        from PIL import Image

        for size in (192, 512):
            with Image.open(ROOT / "assets" / f"novafit-icon-{size}.png") as icon:
                self.assertEqual(icon.size, (size, size))
                self.assertEqual(icon.mode, "RGBA")

    def test_release_workflow_has_a_windows_onedir_job(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
        self.assertIn("runs-on: windows-latest", workflow)
        self.assertIn("scripts/build_windows_distribution.py", workflow)
        self.assertIn("NovaFit-v*-Windows-x64-Standalone", workflow)
        self.assertIn("permissions:\n  contents: read", workflow)
        publish_job = workflow.split("  publish:", maxsplit=1)[1]
        self.assertIn("permissions:\n      contents: write", publish_job)
        self.assertEqual(workflow.count("persist-credentials: false"), 3)
        self.assertNotIn("workflow_dispatch", workflow)
        self.assertNotIn("--clobber", workflow)

    def test_one_click_builder_runs_quality_before_packaging(self) -> None:
        launcher = (ROOT / "BUILD_WINDOWS_STANDALONE.bat").read_text(encoding="utf-8").lower()
        self.assertLess(launcher.index("scripts\\verify.py --quality"), launcher.index("scripts\\build_windows_distribution.py"))
        self.assertIn("py -3.13 -m venv", launcher)


class StandaloneAuditTests(unittest.TestCase):
    """Exercise exact-file integrity and private-runtime-data rejection."""

    @staticmethod
    def _create_valid_bundle(root: Path, version: str = "4.2.0") -> None:
        (root / "_internal").mkdir(parents=True)
        for name in ("NovaFit.exe", "NovaFit-CLI.exe"):
            (root / name).write_bytes(b"MZ" + b"\x00" * 100_000)
        for name in ("START_NOVAFIT.bat", "OPEN_DATA_FOLDER.bat", "README_FIRST.txt", "LICENSE.txt"):
            (root / name).write_text("public\n", encoding="utf-8")
        (root / "_internal" / "python313.dll").write_bytes(b"runtime")
        (root / "BUILD_INFO.json").write_text(
            json.dumps(
                {
                    "version": version,
                    "bundle_layout": "pyinstaller-onedir",
                    "data_directory": "%LOCALAPPDATA%/NovaFit",
                }
            ),
            encoding="utf-8",
        )
        write_manifest(root, version)

    def test_valid_exact_bundle_passes(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._create_valid_bundle(root)
            report = audit_standalone(root, "4.2.0")
            self.assertTrue(report.ok, report.errors)

    def test_runtime_database_and_post_manifest_mutation_fail(self) -> None:
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._create_valid_bundle(root)
            (root / "private.db").write_bytes(b"SQLite format 3\x00")
            report = audit_standalone(root, "4.2.0")
            self.assertFalse(report.ok)
            self.assertTrue(any("runtime data" in error.lower() for error in report.errors))
            self.assertTrue(any("differs" in error.lower() for error in report.errors))


if __name__ == "__main__":
    unittest.main()
