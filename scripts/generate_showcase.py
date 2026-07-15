"""
Module: showcase generator
Purpose: Build deterministic portfolio analytics, a light-theme preview, and an offline HTML report without using private data.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Minimal deps; comments in ENGLISH; emojis sparingly.
"""

from __future__ import annotations

import argparse
import math
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from novafit.charts import CHART_VIEWS, save_analytics_chart
from novafit.config import AppSettings
from novafit.models import HealthEntry
from novafit.reporting import export_html_report
from novafit.themes import theme_ids, theme_label

DEFAULT_OUTPUT = ROOT / "assets"


def build_parser() -> argparse.ArgumentParser:
    """Create the deterministic showcase generator parser.

    Returns:
        Configured argument parser.

    Example:
        >>> build_parser().prog
        'generate_showcase'
    """
    parser = argparse.ArgumentParser(
        prog="generate_showcase",
        description="Generate NovaFit portfolio assets from anonymized deterministic records.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Asset output directory.")
    parser.add_argument("--days", type=int, default=90, help="Number of calendar days to model (42–365).")
    return parser


def build_demo_entries(days: int = 90) -> list[HealthEntry]:
    """Create stable, culturally neutral demo records for screenshots and docs.

    Args:
        days: Number of calendar days to model.

    Returns:
        Chronological health entries with a few intentional missing dates.

    Raises:
        ValueError: If days is outside the supported showcase range.

    Example:
        >>> len(build_demo_entries(42)) >= 35
        True
    """
    if not 42 <= days <= 365:
        raise ValueError("Showcase days must be between 42 and 365.")

    end = date(2026, 7, 15)
    moods = ("Focused", "Calm", "Energetic", "Happy", "Motivated", "Tired")
    missing_offsets = {5, 12, 31, 46, 68, 83}
    entries: list[HealthEntry] = []

    for offset in range(days):
        if offset in missing_offsets:
            continue
        entry_date = end - timedelta(days=days - offset - 1)
        weekday_wave = (entry_date.weekday() - 3) * 170
        long_wave = math.sin(offset / 4.2) * 1_250
        short_wave = math.cos(offset / 2.1) * 620
        growth = offset * 18
        steps = max(2_500, int(8_050 + weekday_wave + long_wave + short_wave + growth))
        water = round(max(1.1, 1.82 + math.sin(offset / 5.0) * 0.31 + (offset % 5) * 0.12), 2)
        calories = int(1_780 + (offset % 7) * 76 + math.sin(offset / 3.0) * 90)
        mood = moods[(offset + entry_date.weekday()) % len(moods)]
        entries.append(
            HealthEntry.build(
                entry_date,
                steps,
                water,
                calories,
                mood,
                "Anonymized portfolio demonstration record.",
            )
        )
    return entries



def build_animated_tour(screenshots: list[Path], destination: Path) -> Path:
    """Build a smooth looping GIF from the three deterministic dashboards.

    Args:
        screenshots: Ordered PNG dashboard paths.
        destination: GIF output path.

    Returns:
        Written animated GIF path.

    Raises:
        ImportError: If Pillow is unavailable.
        ValueError: If fewer than two screenshots are supplied.
        OSError: If an image cannot be read or the GIF cannot be written.

    Example:
        >>> build_animated_tour([Path('a.png'), Path('b.png')], Path('tour.gif'))  # doctest: +SKIP
        PosixPath('tour.gif')
    """
    if len(screenshots) < 2:
        raise ValueError("At least two dashboard screenshots are required for the tour.")

    from PIL import Image

    target_size = (1100, 609)
    base_frames = [
        Image.open(path).convert("RGB").resize(target_size, Image.Resampling.LANCZOS)
        for path in screenshots
    ]
    frames: list[Image.Image] = []
    durations: list[int] = []
    for index, current in enumerate(base_frames):
        following = base_frames[(index + 1) % len(base_frames)]
        frames.append(current)
        durations.append(1800)
        for step in range(1, 6):
            frames.append(Image.blend(current, following, step / 6))
            durations.append(110)

    quantized = [
        frame.quantize(
            colors=128,
            method=Image.Quantize.MEDIANCUT,
            dither=Image.Dither.FLOYDSTEINBERG,
        )
        for frame in frames
    ]
    destination.parent.mkdir(parents=True, exist_ok=True)
    quantized[0].save(
        destination,
        save_all=True,
        append_images=quantized[1:],
        duration=durations,
        loop=0,
        optimize=True,
        disposal=2,
    )
    return destination

def build_theme_contact_sheet(screenshots: list[tuple[str, Path]], destination: Path) -> Path:
    """Build a labeled two-row theme gallery from dashboard screenshots.

    Args:
        screenshots: Ordered ``(theme_id, png_path)`` pairs.
        destination: Contact-sheet output path.

    Returns:
        Written PNG path.

    Raises:
        ImportError: If Pillow is unavailable.
        ValueError: If no screenshots are supplied.
        OSError: If an image cannot be read or written.

    Example:
        >>> build_theme_contact_sheet([("midnight", Path("a.png"))], Path("sheet.png"))  # doctest: +SKIP
        PosixPath('sheet.png')
    """
    if not screenshots:
        raise ValueError("At least one theme screenshot is required.")
    from PIL import Image, ImageDraw

    thumb_size = (520, 290)
    columns = 2
    rows = (len(screenshots) + columns - 1) // columns
    label_height = 42
    sheet = Image.new("RGB", (columns * thumb_size[0], rows * (thumb_size[1] + label_height)), "#050b16")
    draw = ImageDraw.Draw(sheet)
    for index, (theme_id, path) in enumerate(screenshots):
        image = Image.open(path).convert("RGB").resize(thumb_size, Image.Resampling.LANCZOS)
        x = (index % columns) * thumb_size[0]
        y = (index // columns) * (thumb_size[1] + label_height)
        sheet.paste(image, (x, y))
        draw.rectangle((x, y + thumb_size[1], x + thumb_size[0], y + thumb_size[1] + label_height), fill="#0b1828")
        draw.text((x + 15, y + thumb_size[1] + 12), theme_label(theme_id), fill="#e8f5ff")
    destination.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(destination, optimize=True)
    return destination


def generate_assets(output: Path, days: int) -> list[Path]:
    """Write all portfolio screenshots and the portable report.

    Args:
        output: Destination folder.
        days: Calendar range used by the generated views.

    Returns:
        Paths written successfully.

    Raises:
        ImportError: If Matplotlib is unavailable.
        OSError: If an asset cannot be written.
        ValueError: If the requested range is invalid.

    Example:
        >>> len(generate_assets(Path('assets'), 42)) >= 5  # doctest: +SKIP
        True
    """
    output.mkdir(parents=True, exist_ok=True)
    entries = build_demo_entries(days)
    settings = AppSettings(chart_days=min(90, days), chart_view="command_center", theme="aurora").validate()
    written: list[Path] = []
    primary_paths: list[Path] = []

    for view in CHART_VIEWS:
        path = output / f"analytics-{view.replace('_', '-')}.png"
        rendered = save_analytics_chart(
            entries,
            settings,
            path,
            view=view,
            theme="aurora",
            days=min(days, 90 if view != "consistency_map" else days),
            dpi=150,
        )
        written.append(rendered)
        primary_paths.append(rendered)

    written.append(build_animated_tour(primary_paths, output / "novafit-analytics-tour.gif"))

    light_path = output / "analytics-command-center-light.png"
    written.append(
        save_analytics_chart(
            entries,
            settings,
            light_path,
            view="command_center",
            theme="cloud",
            days=min(days, 60),
            dpi=150,
        )
    )

    gallery_dir = output / "theme-gallery"
    theme_shots: list[tuple[str, Path]] = []
    for theme_id in theme_ids():
        path = gallery_dir / f"command-center-{theme_id}.png"
        rendered = save_analytics_chart(
            entries,
            settings,
            path,
            view="command_center",
            theme=theme_id,
            days=min(days, 45),
            dpi=110,
        )
        written.append(rendered)
        theme_shots.append((theme_id, rendered))

    written.append(build_theme_contact_sheet(theme_shots, output / "theme-spectrum.png"))
    written.append(build_animated_tour([path for _, path in theme_shots], output / "theme-spectrum-tour.gif"))

    report_path = output / "novafit-report-preview.html"
    written.append(
        export_html_report(
            entries,
            settings,
            report_path,
            days=min(days, 90),
            theme="aurora",
            view="command_center",
        )
    )
    return written


def main() -> int:
    """Generate all public, anonymized showcase assets.

    Returns:
        Zero after successful generation.

    Example:
        >>> main()  # doctest: +SKIP
        0
    """
    args = build_parser().parse_args()
    for path in generate_assets(args.output.resolve(), args.days):
        print(f"Generated {path} ✅")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
