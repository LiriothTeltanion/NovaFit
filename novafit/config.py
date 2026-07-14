"""Configuration and constants for NovaFit.

NovaFit intentionally relies on the operating system and ``requests`` default
certificate store. The project must never disable TLS verification globally.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path("./data")
DB_PATH = DATA_DIR / "novafit.db"
EXPORT_PATH = DATA_DIR / "novafit_export.json"
CSV_EXPORT_PATH = DATA_DIR / "novafit_export.csv"
CONFIG_PATH = DATA_DIR / "config.json"

CITY_COORDS: dict[str, tuple[float, float]] = {
    "beersheba": (31.2529, 34.7915),
    "tel aviv": (32.0853, 34.7818),
    "jerusalem": (31.7683, 35.2137),
    "haifa": (32.7940, 34.9896),
    "eilat": (29.5581, 34.9482),
}


def configure_ssl() -> None:
    """Compatibility hook retained for older callers.

    Older NovaFit revisions disabled certificate verification globally. That
    behavior was unsafe and has been removed. HTTPS requests now use the normal
    verified defaults supplied by Python and ``requests``.
    """


class Colors:
    """ANSI color codes used by the CLI."""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    WARNING = "\033[93m"
    YELLOW = WARNING  # Backward-compatible alias used by older formatting code.
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


DEFAULT_CONFIG: dict[str, Any] = {
    "step_goal": 10_000,
    "water_goal": 2.0,
    "default_city": "beersheba",
    "theme": "dark",
    "show_achievements": True,
    "db_path": str(DB_PATH),
}


def load_config() -> dict[str, Any]:
    """Load user preferences, falling back safely to defaults."""

    config = DEFAULT_CONFIG.copy()
    if not CONFIG_PATH.exists():
        return config

    try:
        with CONFIG_PATH.open("r", encoding="utf-8") as handle:
            saved = json.load(handle)
        if isinstance(saved, dict):
            config.update(saved)
    except (OSError, json.JSONDecodeError):
        # A damaged optional preferences file should not prevent startup.
        pass
    return config


def save_config(config: dict[str, Any]) -> bool:
    """Persist user preferences to ``data/config.json``."""

    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with CONFIG_PATH.open("w", encoding="utf-8") as handle:
            json.dump(config, handle, indent=2, ensure_ascii=False)
        return True
    except OSError as exc:
        print(f"Error saving config: {exc}")
        return False


CONFIG = load_config()
