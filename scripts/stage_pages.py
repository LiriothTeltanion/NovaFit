"""Build the exact NovaFit GitHub Pages artifact from site/ plus public assets/."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SITE = ROOT / "site"
DEFAULT_ASSETS = ROOT / "assets"
DEFAULT_PROJECT_MANIFEST = ROOT / "portfolio" / "project.json"
DEFAULT_OUTPUT = ROOT / "_site"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Stage the exact NovaFit GitHub Pages artifact.")
    parser.add_argument("--site", type=Path, default=DEFAULT_SITE, help="Tracked static site source.")
    parser.add_argument("--assets", type=Path, default=DEFAULT_ASSETS, help="Tracked public asset source.")
    parser.add_argument(
        "--project-manifest",
        type=Path,
        default=DEFAULT_PROJECT_MANIFEST,
        help="Generated public project facts copied to project.json.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Generated Pages staging path.")
    return parser


def _reject_symlinks(source: Path) -> None:
    for path in source.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"Pages source cannot contain symbolic links: {path}")


def stage_pages(site: Path, assets: Path, output: Path, project_manifest: Path = DEFAULT_PROJECT_MANIFEST) -> Path:
    """Copy site source and existing public media into one deployable tree."""
    site = site.expanduser().resolve()
    assets = assets.expanduser().resolve()
    output = output.expanduser().resolve()
    project_manifest = project_manifest.expanduser().resolve()
    if not site.is_dir():
        raise FileNotFoundError(f"Pages source is missing: {site}")
    if not assets.is_dir():
        raise FileNotFoundError(f"Public asset source is missing: {assets}")
    if not project_manifest.is_file():
        raise FileNotFoundError(f"Generated public project manifest is missing: {project_manifest}")
    overlaps_source = (
        output in site.parents
        or output in assets.parents
        or site in output.parents
        or assets in output.parents
    )
    if output in {ROOT, site, assets} or overlaps_source:
        raise ValueError(f"Unsafe Pages staging destination: {output}")
    if (site / "assets").exists():
        raise ValueError("site/assets must not duplicate tracked root assets; staging supplies them.")
    if (site / "project.json").exists():
        raise ValueError("site/project.json must not duplicate the generated portfolio manifest.")
    _reject_symlinks(site)
    _reject_symlinks(assets)
    if output.exists():
        if output != DEFAULT_OUTPUT.resolve():
            raise ValueError(f"Refusing to replace a non-default existing staging directory: {output}")
        shutil.rmtree(output)
    shutil.copytree(site, output)
    shutil.copytree(assets, output / "assets")
    shutil.copy2(project_manifest, output / "project.json")
    (output / ".nojekyll").write_text("", encoding="utf-8")
    return output


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    destination = stage_pages(args.site, args.assets, args.output, args.project_manifest)
    files = [path for path in destination.rglob("*") if path.is_file()]
    total_bytes = sum(path.stat().st_size for path in files)
    print(f"Staged {len(files)} public files ({total_bytes / (1024 * 1024):.2f} MiB) at {destination} [OK]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
