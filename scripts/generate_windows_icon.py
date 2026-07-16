"""Generate the deterministic multi-resolution NovaFit Windows icon."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT = ROOT / "assets" / "novafit.ico"
ICON_SIZES = (16, 24, 32, 48, 64, 96, 128, 256)


def build_parser() -> argparse.ArgumentParser:
    """Build the icon generator command-line parser."""
    parser = argparse.ArgumentParser(description="Generate the NovaFit Windows .ico file.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def render_master(size: int = 1024) -> Any:
    """Render a high-resolution heart-pulse mark with a transparent edge."""
    from PIL import Image, ImageDraw

    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    margin = round(size * 0.055)
    radius = round(size * 0.235)
    draw.rounded_rectangle(
        (margin, margin, size - margin, size - margin),
        radius=radius,
        fill="#071A1F",
        outline="#31E6B3",
        width=round(size * 0.032),
    )

    heart = [
        (size * 0.50, size * 0.79),
        (size * 0.19, size * 0.49),
        (size * 0.19, size * 0.33),
        (size * 0.25, size * 0.22),
        (size * 0.36, size * 0.19),
        (size * 0.50, size * 0.31),
        (size * 0.64, size * 0.19),
        (size * 0.75, size * 0.22),
        (size * 0.81, size * 0.33),
        (size * 0.81, size * 0.49),
    ]
    draw.polygon(heart, fill="#31E6B3")
    draw.line(
        (
            size * 0.13,
            size * 0.50,
            size * 0.32,
            size * 0.50,
            size * 0.40,
            size * 0.36,
            size * 0.50,
            size * 0.66,
            size * 0.59,
            size * 0.50,
            size * 0.87,
            size * 0.50,
        ),
        fill="#A8FF4F",
        width=round(size * 0.045),
        joint="curve",
    )
    return image


def generate_icon(output: Path) -> Path:
    """Write the ICO plus deterministic 192/512-pixel PWA icon companions."""
    from PIL import Image

    output = output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    master = render_master()
    layers = [master.resize((size, size), Image.Resampling.LANCZOS) for size in ICON_SIZES]
    layers[-1].save(
        output,
        format="ICO",
        append_images=layers[:-1],
        sizes=[(size, size) for size in ICON_SIZES],
        bitmap_format="png",
    )
    for size in (192, 512):
        master.resize((size, size), Image.Resampling.LANCZOS).save(
            output.parent / f"novafit-icon-{size}.png",
            format="PNG",
            optimize=True,
        )
    return output


def main(argv: list[str] | None = None) -> int:
    """Generate the icon and print its path."""
    args = build_parser().parse_args(argv)
    output = generate_icon(args.output)
    print(f"Generated {output} ({output.stat().st_size:,} bytes)")
    for size in (192, 512):
        companion = output.parent / f"novafit-icon-{size}.png"
        print(f"Generated {companion} ({companion.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
