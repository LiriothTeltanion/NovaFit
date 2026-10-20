"""
Module: desktop-to-web export
Purpose: Generate the web app's translation catalogue and theme tokens from the
    Python package, so the desktop and web interfaces never drift apart.
Author: Kevin "Lirioth" Cusnir
Date: 2026-10-19 | TZ: Asia/Jerusalem
Notes: Standard library only. Run from the repository root:
    python web/scripts/export_from_python.py [--check]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "web" / "src" / "generated"
sys.path.insert(0, str(ROOT))

from novafit.i18n import LANGUAGES, TRANSLATIONS  # noqa: E402
from novafit.themes import THEMES  # noqa: E402
from novafit.models import ACTIVITY_LEVELS, UserProfile  # noqa: E402
from novafit.recommendations import _COPY, LOAD_JUMP_RATIO, _weekly_rhythm  # noqa: E402
from novafit.workouts import REFERENCE_WEEKLY_MINUTES, WORKOUT_KINDS  # noqa: E402


def build() -> dict[str, str]:
    """Return the generated files as {file name: JSON text}."""
    i18n = {
        "languages": {
            code: {"label": item.label, "direction": item.direction, "locale": item.locale}
            for code, item in LANGUAGES.items()
        },
        "messages": {code: dict(sorted(TRANSLATIONS[code].items())) for code in LANGUAGES},
    }
    themes = {
        theme_id: {"label": theme.label, "mode": theme.mode, "ui": dict(theme.ui)}
        for theme_id, theme in THEMES.items()
    }
    domain = {"workoutKinds": list(WORKOUT_KINDS), "referenceWeeklyMinutes": REFERENCE_WEEKLY_MINUTES}
    rhythm = {
        code: {
            level: list(_weekly_rhythm(UserProfile.build("Web", activity_level=level), code)[:3])
            for level in ACTIVITY_LEVELS
        }
        for code in LANGUAGES
    }
    # The desktop appends "Preferred focus: <sport>…" to the weekly rhythm; export it as a {focus} template.
    focus_line = {
        code: _weekly_rhythm(UserProfile.build("Web", sport_focus="mixed"), code)[3].replace(
            TRANSLATIONS[code]["sport_mixed"], "{focus}"
        )
        for code in LANGUAGES
    }
    coach = {"copy": _COPY, "weeklyRhythm": rhythm, "focusLine": focus_line, "loadJumpRatio": LOAD_JUMP_RATIO}
    dump = lambda value: json.dumps(value, ensure_ascii=False, indent=1) + "\n"  # noqa: E731
    return {
        "i18n.json": dump(i18n),
        "themes.json": dump(themes),
        "domain.json": dump(domain),
        "coach.json": dump(coach),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail when a generated file is out of date.")
    args = parser.parse_args()
    files = build()
    stale = [name for name, text in files.items() if not (OUT / name).exists() or (OUT / name).read_text(encoding="utf-8") != text]
    if args.check:
        if stale:
            print("Out of date: " + ", ".join(stale) + ". Run: python web/scripts/export_from_python.py")
            return 1
        print("Web catalogue and theme tokens are current. [OK]")
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        (OUT / name).write_text(text, encoding="utf-8", newline="\n")
    print(f"Wrote {len(files)} files to {OUT} ({len(stale)} changed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
