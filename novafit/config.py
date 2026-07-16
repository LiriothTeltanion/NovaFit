"""
Module: application configuration
Purpose: Manage portable paths, user goals, themes, analytics views, motivation
    preferences, and city coordinates with safe backward-compatible defaults.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Standard-library persistence; comments in ENGLISH; emojis sparingly.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Any, Mapping

from . import __version__
from .i18n import normalize_language
from .themes import normalize_theme_id, theme_ids
from .validation import validate_non_negative_float, validate_non_negative_int

LOGGER = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _resolve_default_data_dir(
    *,
    frozen: bool | None = None,
    environment: Mapping[str, str] | None = None,
    home: Path | None = None,
) -> Path:
    """Return the source or installed application's durable data directory.

    A source checkout intentionally keeps its historical ``data`` directory.
    A frozen Windows build must never write inside the executable bundle, which
    may live under a read-only installation directory or be replaced during an
    update. It therefore uses ``%LOCALAPPDATA%/NovaFit``. Environment overrides
    remain available for portable/test deployments.

    Args:
        frozen: Explicit frozen state for tests; auto-detected when omitted.
        environment: Environment mapping used to resolve Windows app data.
        home: Home-directory fallback used when Windows variables are absent.

    Returns:
        Absolute default data directory before ``NOVAFIT_DATA_DIR`` overrides.
    """
    is_frozen = bool(getattr(sys, "frozen", False)) if frozen is None else frozen
    if not is_frozen:
        return PROJECT_ROOT / "data"

    variables = os.environ if environment is None else environment
    windows_root = variables.get("LOCALAPPDATA") or variables.get("APPDATA")
    if windows_root:
        return Path(windows_root).expanduser() / "NovaFit"
    return (home if home is not None else Path.home()) / ".novafit"


DEFAULT_DATA_DIR = _resolve_default_data_dir()
DATA_DIR = Path(os.getenv("NOVAFIT_DATA_DIR", str(DEFAULT_DATA_DIR))).expanduser().resolve()
DB_PATH = Path(os.getenv("NOVAFIT_DB_PATH", str(DATA_DIR / "novafit.db"))).expanduser().resolve()
CONFIG_PATH = Path(os.getenv("NOVAFIT_CONFIG_PATH", str(DATA_DIR / "config.json"))).expanduser().resolve()
LOG_PATH = Path(os.getenv("NOVAFIT_LOG_PATH", str(DATA_DIR / "novafit.log"))).expanduser().resolve()
EXPORT_PATH = DATA_DIR / "novafit_export.json"
CSV_EXPORT_PATH = DATA_DIR / "novafit_export.csv"
APP_VERSION = __version__
TIMEZONE_NAME = "Asia/Jerusalem"

CITY_COORDS: dict[str, tuple[float, float]] = {
    "beersheba": (31.2529, 34.7915),
    "beer sheva": (31.2529, 34.7915),
    "be'er sheva": (31.2529, 34.7915),
    "tel aviv": (32.0853, 34.7818),
    "jerusalem": (31.7683, 35.2137),
    "haifa": (32.7940, 34.9896),
    "eilat": (29.5581, 34.9482),
    "ashdod": (31.8014, 34.6435),
    "netanya": (32.3215, 34.8532),
}


@dataclass(slots=True)
class AppSettings:
    """Store user preferences that are safe to persist locally.

    Args:
        step_goal: Daily walking target.
        water_goal_l: Daily hydration target in liters.
        calorie_goal: Optional daily calorie reference target.
        default_city: City used by the weather tool.
        theme: Stable theme identifier from ``novafit.themes``.
        show_achievements: Whether the GUI displays celebration messages.
        chart_days: Number of recent days displayed in charts.
        chart_view: Default analytics view identifier.
        reduce_motion: Disable optional decorative GUI animation.
        personal_why: Private short statement shown in Motivation Center.
        weekly_focus: Optional custom weekly challenge.
        reward_note: Recovery or reward reminder.
        language: Active interface language.
        active_profile_id: Last selected local profile.
        ui_scale: Optional GUI scale multiplier.

    Example:
        >>> AppSettings(step_goal=8000).step_goal
        8000
    """

    step_goal: int = 10_000
    water_goal_l: float = 2.0
    calorie_goal: int = 2_000
    default_city: str = "beersheba"
    theme: str = "aurora"
    show_achievements: bool = True
    chart_days: int = 30
    chart_view: str = "command_center"
    reduce_motion: bool = False
    personal_why: str = "Build steady energy for learning, work, and the people I care about."
    weekly_focus: str = ""
    reward_note: str = "Protect recovery time after meaningful progress."
    language: str = "en"
    active_profile_id: int = 1
    ui_scale: float = 1.0

    def validate(self) -> "AppSettings":
        """Validate settings and normalize the theme identifier.

        Returns:
            The validated settings instance.

        Raises:
            ValueError: If a goal, theme, city, view, chart range, or text field
                is invalid.

        Example:
            >>> AppSettings(theme="dark").validate().theme
            'midnight'
        """
        self.step_goal = validate_non_negative_int(self.step_goal, "Step goal", 200_000)
        self.water_goal_l = validate_non_negative_float(self.water_goal_l, "Water goal", 20.0)
        self.calorie_goal = validate_non_negative_int(self.calorie_goal, "Calorie goal", 20_000)
        if self.step_goal <= 0:
            raise ValueError("Step goal must be greater than zero.")
        if self.water_goal_l <= 0:
            raise ValueError("Water goal must be greater than zero.")
        if self.calorie_goal <= 0:
            raise ValueError("Calorie goal must be greater than zero.")
        self.theme = normalize_theme_id(self.theme)
        if self.theme not in theme_ids():
            raise ValueError(f"Unsupported theme: {self.theme}")
        if self.default_city.lower().strip() not in CITY_COORDS:
            raise ValueError(f"Unsupported default city: {self.default_city}")
        self.chart_days = validate_non_negative_int(self.chart_days, "Chart days", 365)
        if not 7 <= self.chart_days <= 365:
            raise ValueError("Chart days must be between 7 and 365.")
        if self.chart_view not in {"command_center", "trend_lab", "consistency_map", "training_atlas"}:
            raise ValueError(
                "Chart view must be command_center, trend_lab, consistency_map, or training_atlas."
            )
        self.language = normalize_language(self.language)
        self.active_profile_id = validate_non_negative_int(
            self.active_profile_id, "Active profile id", 2_147_483_647
        )
        if self.active_profile_id <= 0:
            raise ValueError("Active profile id must be greater than zero.")
        self.ui_scale = validate_non_negative_float(self.ui_scale, "UI scale", 1.5)
        if not 0.8 <= self.ui_scale <= 1.5:
            raise ValueError("UI scale must be between 0.8 and 1.5.")
        for label, value, maximum in (
            ("Personal why", self.personal_why, 240),
            ("Weekly focus", self.weekly_focus, 180),
            ("Reward note", self.reward_note, 180),
        ):
            if len(value) > maximum:
                raise ValueError(f"{label} must be {maximum} characters or fewer.")
        return self


def ensure_data_dir() -> Path:
    """Create and return the configured data directory.

    Returns:
        The absolute data directory path.

    Raises:
        OSError: If the directory cannot be created.

    Example:
        >>> ensure_data_dir().name
        'data'
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR


def load_settings(path: Path = CONFIG_PATH) -> AppSettings:
    """Load settings from JSON while preserving safe defaults and old themes.

    Args:
        path: Configuration file to read.

    Returns:
        Validated settings. Defaults are returned for missing or invalid files.

    Raises:
        None. Recoverable file and validation problems are logged as warnings.

    Example:
        >>> isinstance(load_settings(Path('missing-config.json')), AppSettings)
        True
    """
    defaults = AppSettings()
    if not path.exists():
        return defaults

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, Mapping):
            raise ValueError("Configuration root must be an object.")

        allowed = {item.name for item in fields(AppSettings)}
        values: dict[str, Any] = asdict(defaults)
        values.update({key: value for key, value in raw.items() if key in allowed})
        if "theme" in values:
            values["theme"] = normalize_theme_id(str(values["theme"]))
        return AppSettings(**values).validate()
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        LOGGER.warning("Invalid settings file; defaults loaded: %s", exc)
        return defaults


def save_settings(settings: AppSettings, path: Path = CONFIG_PATH) -> Path:
    """Persist validated settings atomically as UTF-8 JSON.

    Args:
        settings: Preferences to validate and store.
        path: Destination JSON file.

    Returns:
        The written path.

    Raises:
        ValueError: If the settings are invalid.
        OSError: If the destination cannot be written.

    Example:
        >>> save_settings(AppSettings(), Path('data/example-config.json')).suffix
        '.json'
    """
    settings.validate()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(asdict(settings), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)
    return path
