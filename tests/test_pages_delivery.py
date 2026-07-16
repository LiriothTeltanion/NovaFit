"""Behavioral tests for secure NovaFit GitHub Pages staging and auditing."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.stage_pages import stage_pages
from tools.site_audit import CANONICAL_URL, audit_site

ROOT = Path(__file__).resolve().parent.parent


class PagesDeliveryTests(unittest.TestCase):
    """Protect the public-only staging boundary used by GitHub Pages."""

    def _build_valid_source(self, root: Path) -> tuple[Path, Path, Path]:
        site = root / "site"
        assets = root / "assets"
        site.mkdir()
        assets.mkdir()
        (assets / "hero.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><rect width="10" height="10"/></svg>\n',
            encoding="utf-8",
        )
        (site / "index.html").write_text(
            "<!doctype html><html lang=\"en\"><head>"
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta name="description" content="NovaFit public desktop showcase">'
            f'<link rel="canonical" href="{CANONICAL_URL}">'
            '<link rel="manifest" href="manifest.webmanifest">'
            "</head><body><img src=\"assets/hero.svg\" alt=\"NovaFit\"></body></html>\n",
            encoding="utf-8",
        )
        (site / "404.html").write_text(
            '<!doctype html><html lang="en"><body><a href="/NovaFit/">Return home</a></body></html>\n',
            encoding="utf-8",
        )
        manifest = {
            "name": "NovaFit Showcase",
            "short_name": "NovaFit",
            "start_url": "./",
            "scope": "./",
            "display": "standalone",
            "icons": [{"src": "assets/hero.svg", "sizes": "any", "type": "image/svg+xml"}],
        }
        (site / "manifest.webmanifest").write_text(
            json.dumps(manifest) + "\n",
            encoding="utf-8",
        )
        (site / "sw.js").write_text(
            "const CACHE='novafit-showcase-test';\n"
            "const CORE_SHELL=['./','./index.html','./manifest.webmanifest'];\n"
            "self.addEventListener('install',event=>event.waitUntil(caches.open(CACHE)));\n"
            "self.addEventListener('activate',event=>event.waitUntil(self.clients.claim()));\n"
            "self.addEventListener('fetch',event=>event.respondWith(fetch(event.request).catch(()=>caches.match(event.request))));\n",
            encoding="utf-8",
        )
        project_manifest = root / "portfolio-project.json"
        project_manifest.write_text(
            json.dumps(
                {
                    "schema": "nova-portfolio-project-v1",
                    "slug": "novafit",
                    "name": "NovaFit",
                    "version": "4.2.0",
                    "status": "active",
                    "repository": "https://github.com/LiriothTeltanion/NovaFit",
                    "privacy": {"local_first": True, "tracked_runtime_data": False},
                    "website": {"live": CANONICAL_URL},
                }
            )
            + "\n",
            encoding="utf-8",
        )
        return site, assets, project_manifest

    def test_exact_staged_artifact_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            site, assets, project = self._build_valid_source(root)

            staged = stage_pages(site, assets, root / "artifact", project)
            report = audit_site(staged)

            self.assertFalse(report.errors)
            self.assertTrue((staged / ".nojekyll").exists())
            self.assertTrue((staged / "assets" / "hero.svg").exists())

    def test_private_runtime_file_and_absolute_user_path_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            site, assets, project = self._build_valid_source(root)
            staged = stage_pages(site, assets, root / "artifact", project)
            private = staged / "data" / "novafit.db"
            private.parent.mkdir()
            private.write_bytes(b"SQLite format 3\x00")
            (staged / "leak.txt").write_text(
                "C:\\Users\\private-user\\OneDrive\\NovaFit",
                encoding="utf-8",
            )

            report = audit_site(staged)

            messages = "\n".join(finding.message for finding in report.errors)
            self.assertIn("forbidden in Pages", messages)
            self.assertIn("Private absolute computer path", messages)

    def test_broken_local_link_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            site, assets, _ = self._build_valid_source(root)
            with (site / "index.html").open("a", encoding="utf-8") as handle:
                handle.write('<a href="missing.html">Missing</a>\n')

            report = audit_site(site, asset_root=assets)

            self.assertTrue(any("broken local site link" in item.message for item in report.errors))

    def test_manifest_cannot_escape_scope_or_reference_missing_screenshots(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            site, assets, project = self._build_valid_source(root)
            manifest_path = site / "manifest.webmanifest"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["start_url"] = "https://example.com/app"
            manifest["screenshots"] = [{"src": "assets/missing-showcase.png"}]
            manifest_path.write_text(json.dumps(manifest) + "\n", encoding="utf-8")
            staged = stage_pages(site, assets, root / "artifact", project)

            report = audit_site(staged)

            messages = "\n".join(finding.message for finding in report.errors)
            self.assertIn("manifest start_url must stay inside", messages)
            self.assertIn("manifest screenshot 0: broken local site link", messages)

    def test_site_must_not_duplicate_root_assets(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            site, assets, project = self._build_valid_source(root)
            (site / "assets").mkdir()

            with self.assertRaises(ValueError):
                stage_pages(site, assets, root / "artifact", project)

    def test_service_worker_precache_cannot_reference_missing_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            site, assets, project = self._build_valid_source(root)
            sw_path = site / "sw.js"
            source = sw_path.read_text(encoding="utf-8")
            sw_path.write_text(
                source.replace("'./manifest.webmanifest'", "'./missing-offline.html'"),
                encoding="utf-8",
            )
            staged = stage_pages(site, assets, root / "artifact", project)

            report = audit_site(staged)

            self.assertTrue(
                any("sw.js CORE_SHELL: broken local site link" in item.message for item in report.errors)
            )

    def test_workflow_run_accepts_only_verified_pushes_from_this_repository(self) -> None:
        """A fork PR branch named main must never reach the Pages deploy job."""
        workflow = (ROOT / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")

        self.assertIn("workflow_run.event == 'push'", workflow)
        self.assertIn("workflow_run.head_repository.full_name == github.repository", workflow)
        self.assertIn("workflow_run.conclusion == 'success'", workflow)
        self.assertNotIn("workflow_dispatch", workflow)


if __name__ == "__main__":
    unittest.main()
