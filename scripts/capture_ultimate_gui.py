"""
Module: ultimate GUI capture
Purpose: Produce truthful portfolio screenshots from the real Tkinter interface
    using deterministic, anonymized multi-profile demonstration data.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Requires a display server and ImageMagick; comments in ENGLISH.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import tempfile
import time
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
DEFAULT_OUTPUT = ROOT / "assets"


def build_parser() -> argparse.ArgumentParser:
    """Build the screenshot-generator parser.

    Returns:
        Configured argument parser.

    Example:
        >>> build_parser().prog
        'capture_ultimate_gui'
    """
    parser = argparse.ArgumentParser(
        prog="capture_ultimate_gui",
        description="Capture the real NovaFit Ultimate Tkinter workspaces.",
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def capture_window(window: object, destination: Path) -> Path:
    """Capture one visible Tk window through Pillow ImageGrab.

    Args:
        window: Tk root window with geometry methods.
        destination: PNG path to write.

    Returns:
        Written PNG path.

    Raises:
        OSError: If the display cannot be captured.

    Example:
        >>> capture_window(object(), Path("capture.png"))  # doctest: +SKIP
        PosixPath("capture.png")
    """
    from PIL import ImageGrab

    destination.parent.mkdir(parents=True, exist_ok=True)
    window.update_idletasks()
    x = window.winfo_rootx()
    y = window.winfo_rooty()
    width = window.winfo_width()
    height = window.winfo_height()
    image = ImageGrab.grab(
        bbox=(x, y, x + width, y + height),
        xdisplay=os.environ.get("DISPLAY"),
    )
    image.save(destination, optimize=True)
    return destination


def seed_profiles(database_path: Path) -> None:
    """Create three isolated demo profiles with anonymized records.

    Args:
        database_path: Temporary SQLite destination.

    Returns:
        None.

    Example:
        >>> seed_profiles(Path('demo.db'))  # doctest: +SKIP
    """
    from novafit.database import NovaFitDatabase
    from novafit.models import HealthEntry, UserProfile
    from scripts.generate_showcase import build_demo_entries

    database = NovaFitDatabase(database_path)
    database.initialize()
    primary = database.get_profile(1)
    if primary is None:
        raise RuntimeError("Primary demo profile was not created.")
    database.update_profile(
        UserProfile.build(
            "Kevin / Lirioth",
            profile_id=1,
            avatar="nova",
            language="en",
            theme="aurora",
            step_goal=10_000,
            water_goal_l=2.2,
            calorie_goal=2_050,
            activity_level="balanced",
            sport_focus="mixed",
        )
    )
    database.set_active_profile(1)
    for entry in build_demo_entries(90):
        database.upsert(entry)

    lucia = database.create_profile(
        UserProfile.build(
            "Lucía Demo",
            avatar="sun",
            language="es",
            theme="arcade",
            step_goal=8_500,
            water_goal_l=2.0,
            calorie_goal=1_850,
            activity_level="beginner",
            sport_focus="walking",
        )
    )
    database.set_active_profile(lucia.profile_id or 1)
    for entry in build_demo_entries(50)[::2]:
        database.upsert(
            HealthEntry.build(
                entry.entry_date,
                max(2_500, int(entry.steps * 0.78)),
                round(max(1.0, entry.water_l * 0.9), 2),
                entry.calories,
                entry.mood,
                "Anonymized Spanish-profile demonstration record.",
            )
        )

    noa = database.create_profile(
        UserProfile.build(
            "נועה Demo",
            avatar="moon",
            language="he",
            theme="sapphire",
            step_goal=7_500,
            water_goal_l=2.1,
            calorie_goal=1_900,
            activity_level="balanced",
            sport_focus="mobility",
        )
    )
    database.set_active_profile(noa.profile_id or 1)
    for entry in build_demo_entries(42)[::2]:
        database.upsert(
            HealthEntry.build(
                entry.entry_date,
                max(2_000, int(entry.steps * 0.68)),
                round(max(1.0, entry.water_l * 0.95), 2),
                entry.calories,
                entry.mood,
                "Anonymized Hebrew-profile demonstration record.",
            )
        )
    database.set_active_profile(1)


def settle(window: object, seconds: float = 0.9) -> None:
    """Process Tk events for a bounded settling period.

    Args:
        window: Active Tk root.
        seconds: Event-processing duration.

    Returns:
        None.

    Example:
        >>> settle(object(), 0.1)  # doctest: +SKIP
    """
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        window.update_idletasks()
        window.update()
        time.sleep(0.04)


def run_capture(output: Path) -> list[Path]:
    """Launch the real application and capture four major workspaces.

    Args:
        output: Asset destination directory.

    Returns:
        Written screenshot paths.

    Raises:
        RuntimeError: If Tk cannot open a display.
        subprocess.CalledProcessError: If a screenshot cannot be captured.

    Example:
        >>> run_capture(Path('assets'))  # doctest: +SKIP
        [PosixPath('assets/novafit-ultimate-gui.png'), ...]
    """
    with tempfile.TemporaryDirectory(prefix="novafit-capture-") as temporary:
        data_dir = Path(temporary)
        database_path = data_dir / "showcase.db"
        os.environ["NOVAFIT_DATA_DIR"] = str(data_dir)
        os.environ["NOVAFIT_DB_PATH"] = str(database_path)
        os.environ["NOVAFIT_CONFIG_PATH"] = str(data_dir / "config.json")
        os.environ["NOVAFIT_LOG_PATH"] = str(data_dir / "capture.log")

        seed_profiles(database_path)
        from novafit.gui import NovaFitApp

        app = NovaFitApp(database_path)
        app.geometry("1580x980+0+0")
        settle(app, 1.4)
        written: list[Path] = []
        captures = (
            ("analytics", "novafit-ultimate-gui.png"),
            ("recommendations", "sport-data-coach-real.png"),
            ("profiles", "multi-profile-language-center.png"),
            ("motivation", "motivation-center-ultimate.png"),
        )
        for page, filename in captures:
            app._select_page(page)  # Portfolio-only deterministic capture route.
            settle(app, 1.0)
            written.append(capture_window(app, output / filename))

        # Demonstrate that language and direction are bound to isolated profiles.
        app.profile_choice_var.set("2 · Lucía Demo")
        app._profile_combo_changed()
        settle(app, 1.2)
        app._select_page("recommendations")
        settle(app, 0.8)
        written.append(capture_window(app, output / "spanish-sport-data-coach.png"))

        app.profile_choice_var.set("3 · נועה Demo")
        app._profile_combo_changed()
        settle(app, 1.2)
        app._select_page("analytics")
        settle(app, 0.8)
        written.append(capture_window(app, output / "hebrew-rtl-command-center.png"))
        app.destroy()
        return written


def main() -> int:
    """Capture and report all GUI screenshots.

    Returns:
        Zero after successful capture.

    Example:
        >>> main()  # doctest: +SKIP
        0
    """
    args = build_parser().parse_args()
    for path in run_capture(args.output.resolve()):
        print(f"Captured {path} ✅")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
