"""Generate and verify NovaFit's public project facts and asset manifest."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import struct
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT / "assets"
ASSET_MANIFEST = ASSETS_DIR / "manifest.json"
FACTS_DOCUMENT = ROOT / "docs" / "PROJECT_FACTS.md"
PROJECT_MANIFEST = ROOT / "portfolio" / "project.json"

sys.path.insert(0, str(ROOT))
from novafit import __version__  # noqa: E402
from novafit.i18n import LANGUAGES  # noqa: E402
from novafit.themes import theme_ids  # noqa: E402


def verify_version_source() -> None:
    """Require package metadata and ``pyproject.toml`` to share one version."""
    content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    project = re.search(
        r"(?ms)^\[project\]\s*(.*?)(?=^\[|\Z)",
        content,
    )
    version = re.search(r'^version\s*=\s*"([^"]+)"\s*$', project.group(1), re.MULTILINE) if project else None
    if version is None:
        raise ValueError("pyproject.toml is missing [project].version")
    if version.group(1) != __version__:
        raise ValueError(
            "Version drift: "
            f"novafit.__version__={__version__!r}, pyproject project.version={version.group(1)!r}"
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Keep README-facing project facts and visual assets synchronized."
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="Update generated files.")
    mode.add_argument("--check", action="store_true", help="Fail when generated files drift.")
    return parser


def discover_test_count() -> int:
    """Count unittest/pytest-style test functions without importing test modules."""
    total = 0
    for path in sorted((ROOT / "tests").glob("test_*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        total += sum(
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")
            for node in ast.walk(tree)
        )
    return total


def build_asset_manifest() -> dict[str, Any]:
    markdown = {
        path.relative_to(ROOT).as_posix(): path.read_text(encoding="utf-8")
        for path in sorted(ROOT.rglob("*.md"))
        if ".venv" not in path.parts
    }
    assets: list[dict[str, Any]] = []
    for path in sorted(item for item in ASSETS_DIR.rglob("*") if item.is_file()):
        if path == ASSET_MANIFEST:
            continue
        relative = path.relative_to(ROOT).as_posix()
        width, height = _dimensions(path)
        references = [name for name, content in markdown.items() if path.name in content]
        assets.append(
            {
                "path": relative,
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
                "media_type": _media_type(path),
                "width": width,
                "height": height,
                "animated": path.suffix.lower() == ".gif"
                or (path.suffix.lower() == ".svg" and "@keyframes" in path.read_text(encoding="utf-8")),
                "referenced_by": references,
                "status": "current" if references else "gallery",
                "privacy": "public-demo",
            }
        )
    return {
        "schema": "novafit-asset-manifest-v1",
        "asset_count": len(assets),
        "total_bytes": sum(item["bytes"] for item in assets),
        "assets": assets,
    }


def build_project_manifest(asset_manifest: dict[str, Any], test_count: int) -> dict[str, Any]:
    return {
        "schema": "nova-portfolio-project-v1",
        "slug": "novafit",
        "name": "NovaFit",
        "version": __version__,
        "status": "active",
        "default_branch": "main",
        "repository": "https://github.com/LiriothTeltanion/NovaFit",
        "summary": (
            "A local-first Windows wellness intelligence studio with isolated profiles, "
            "English, Spanish and Hebrew RTL, efficient motion, explainable analytics, "
            "complete verified backups and one-click self-repair."
        ),
        "platforms": ["Windows desktop", "Python CLI"],
        "languages": list(LANGUAGES),
        "theme_count": len(theme_ids()),
        "quality": {
            "workflow": ".github/workflows/quality.yml",
            "automated_tests_discovered": test_count,
            "verification_command": "VERIFY_ALL.bat",
            "release_audit": "python tools/package_audit.py --strict-distribution",
        },
        "automation": {
            "documentation": "python scripts/sync_docs.py --write",
            "quality_workflow": ".github/workflows/quality.yml",
            "tag_release_workflow": ".github/workflows/release.yml",
            "profile_source": "portfolio/project.json",
        },
        "capabilities": [
            "multi-profile SQLite isolation",
            "Hebrew right-to-left interface",
            "four analytics studios",
            "purposeful reduced-motion-aware animation",
            "complete all-profile ZIP backups with SHA-256",
            "JSON, CSV, PNG and offline HTML exports",
            "one-click Windows setup, launch and verification",
        ],
        "privacy": {
            "local_first": True,
            "tracked_runtime_data": False,
            "weather_sends_health_records": False,
        },
        "assets": {
            "count": asset_manifest["asset_count"],
            "total_bytes": asset_manifest["total_bytes"],
            "hero": "assets/novafit-ultimate-banner-animated.svg",
            "poster": "assets/novafit-ultimate-gui.png",
            "hebrew": "assets/hebrew-rtl-command-center.png",
            "manifest": "assets/manifest.json",
        },
    }


def render_facts(project: dict[str, Any]) -> str:
    quality = project["quality"]
    assets = project["assets"]
    return (
        "# NovaFit verified project facts 🤖\n\n"
        "> Generated by `python scripts/sync_docs.py --write`. Do not edit factual values manually.\n\n"
        f"- **Version:** `{project['version']}`\n"
        f"- **Default branch:** `{project['default_branch']}`\n"
        f"- **Automated tests discovered:** {quality['automated_tests_discovered']}\n"
        f"- **Interface languages:** {', '.join(project['languages'])}\n"
        f"- **Themes:** {project['theme_count']}\n"
        f"- **Public visual assets:** {assets['count']} ({assets['total_bytes'] / (1024 * 1024):.2f} MiB)\n"
        f"- **Complete verification:** `{quality['verification_command']}`\n"
        f"- **Strict release audit:** `{quality['release_audit']}`\n"
        "- **Automated GitHub release:** `.github/workflows/release.yml`\n"
        "- **Profile synchronization source:** `portfolio/project.json`\n"
        "- **Runtime data policy:** SQLite, config, logs, exports and backups stay outside Git tracking.\n\n"
        "The GitHub Actions badge is the source of truth for whether the current remote commit is green.\n"
    )


def generated_files() -> dict[Path, str]:
    verify_version_source()
    assets = build_asset_manifest()
    tests = discover_test_count()
    project = build_project_manifest(assets, tests)
    return {
        ASSET_MANIFEST: json.dumps(assets, ensure_ascii=False, indent=2) + "\n",
        PROJECT_MANIFEST: json.dumps(project, ensure_ascii=False, indent=2) + "\n",
        FACTS_DOCUMENT: render_facts(project),
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    files = generated_files()
    if args.write:
        for path, content in files.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
            print(f"updated {path.relative_to(ROOT)}")
        return 0

    drift = []
    for path, expected in files.items():
        actual = path.read_text(encoding="utf-8") if path.exists() else None
        if actual != expected:
            drift.append(path.relative_to(ROOT).as_posix())
    if drift:
        print("Generated documentation is out of date:")
        for path in drift:
            print(f"  - {path}")
        print("Run: python scripts/sync_docs.py --write")
        return 1
    print("Generated documentation and asset metadata are synchronized. [OK]")
    return 0


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _media_type(path: Path) -> str:
    return {
        ".gif": "image/gif",
        ".png": "image/png",
        ".svg": "image/svg+xml",
        ".html": "text/html",
    }.get(path.suffix.lower(), "application/octet-stream")


def _dimensions(path: Path) -> tuple[int | None, int | None]:
    try:
        if path.suffix.lower() == ".png":
            with path.open("rb") as handle:
                header = handle.read(24)
            if header.startswith(b"\x89PNG\r\n\x1a\n"):
                return struct.unpack(">II", header[16:24])
        if path.suffix.lower() == ".gif":
            with path.open("rb") as handle:
                header = handle.read(10)
            if header.startswith((b"GIF87a", b"GIF89a")):
                return struct.unpack("<HH", header[6:10])
        if path.suffix.lower() == ".svg":
            root = ET.parse(path).getroot()
            view_box = root.attrib.get("viewBox", "").split()
            if len(view_box) == 4:
                return round(float(view_box[2])), round(float(view_box[3]))
    except (OSError, ValueError, ET.ParseError, struct.error):
        return None, None
    return None, None


if __name__ == "__main__":
    raise SystemExit(main())
