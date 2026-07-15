"""
Module: domain models
Purpose: Represent health records and local user profiles through validated,
    serializable data contracts.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Minimal deps; comments in ENGLISH; emojis sparingly.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from typing import Any, Mapping

from .i18n import normalize_language
from .themes import normalize_theme_id
from .validation import (
    MAX_MOOD_LENGTH,
    MAX_NOTE_LENGTH,
    clean_text,
    parse_iso_date,
    validate_non_negative_float,
    validate_non_negative_int,
    validate_optional_int,
)

PROFILE_AVATARS = ("nova", "runner", "walker", "cyclist", "strength", "focus", "sun", "moon")
ACTIVITY_LEVELS = ("beginner", "balanced", "active")
SPORT_FOCUSES = ("walking", "strength", "mobility", "running", "cycling", "mixed")


@dataclass(frozen=True, slots=True)
class HealthEntry:
    """Represent one day of locally stored wellness metrics.

    Attributes:
        entry_date: Calendar day for the measurements.
        steps: Non-negative step count.
        water_l: Liters of water consumed.
        calories: Optional calorie count.
        mood: Optional short mood label or emoji.
        note: Optional private local note.

    Example:
        >>> HealthEntry.build('2026-07-15', 8000, 2.0).steps
        8000
    """

    entry_date: date
    steps: int
    water_l: float
    calories: int | None = None
    mood: str | None = None
    note: str | None = None

    @classmethod
    def build(
        cls,
        entry_date: str | date,
        steps: Any,
        water_l: Any,
        calories: Any = None,
        mood: Any = None,
        note: Any = None,
    ) -> "HealthEntry":
        """Create a validated health entry from user-facing values.

        Args:
            entry_date: ISO date text or a ``date`` object.
            steps: Step count, convertible to an integer.
            water_l: Water intake, convertible to a float.
            calories: Optional calorie count.
            mood: Optional short mood label.
            note: Optional local note.

        Returns:
            A validated immutable entry.

        Raises:
            ValueError: If any value is malformed or outside safe bounds.

        Example:
            >>> HealthEntry.build('2026-07-15', '9000', '2.3').water_l
            2.3
        """
        parsed_date = entry_date if isinstance(entry_date, date) else parse_iso_date(str(entry_date))
        return cls(
            entry_date=parsed_date,
            steps=validate_non_negative_int(steps, "Steps", 200_000),
            water_l=validate_non_negative_float(water_l, "Water", 20.0),
            calories=validate_optional_int(calories, "Calories", 20_000),
            mood=clean_text(mood, "Mood", MAX_MOOD_LENGTH),
            note=clean_text(note, "Note", MAX_NOTE_LENGTH),
        )

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> "HealthEntry":
        """Create an entry from JSON, CSV, or database-style field names.

        Args:
            raw: Mapping containing date, steps, water, and optional fields.

        Returns:
            A validated health entry.

        Raises:
            ValueError: If required values are missing or invalid.

        Example:
            >>> HealthEntry.from_mapping({'date': '2026-07-15', 'steps': 5, 'water_l': 1}).steps
            5
        """
        date_value = raw.get("date", raw.get("entry_date"))
        water_value = raw.get("water_l", raw.get("water", raw.get("Water (L)")))
        if date_value is None:
            raise ValueError("Date is required.")
        if raw.get("steps") is None and raw.get("Steps") is None:
            raise ValueError("Steps are required.")
        if water_value is None:
            raise ValueError("Water is required.")
        return cls.build(
            date_value,
            raw.get("steps", raw.get("Steps")),
            water_value,
            raw.get("calories", raw.get("Calories")),
            raw.get("mood", raw.get("Mood")),
            raw.get("note", raw.get("Note")),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the entry to a stable JSON-compatible dictionary.

        Returns:
            Dictionary using public import/export field names.

        Example:
            >>> HealthEntry.build('2026-07-15', 1, 1).to_dict()['date']
            '2026-07-15'
        """
        raw = asdict(self)
        raw["date"] = self.entry_date.isoformat()
        raw.pop("entry_date")
        return raw


@dataclass(frozen=True, slots=True)
class UserProfile:
    """Represent one local NovaFit user and their recommendation preferences.

    Attributes:
        profile_id: Database identifier, or ``None`` before insertion.
        display_name: Human-friendly profile name.
        avatar: Stable visual avatar key.
        language: ``en``, ``es``, or ``he``.
        theme: Stable NovaFit theme key.
        step_goal: Daily step target.
        water_goal_l: Daily hydration target.
        calorie_goal: Descriptive calorie reference.
        activity_level: Gentle, balanced, or active preference.
        sport_focus: Preferred general activity category.

    Example:
        >>> UserProfile.build('Kevin').language
        'en'
    """

    profile_id: int | None
    display_name: str
    avatar: str = "nova"
    language: str = "en"
    theme: str = "aurora"
    step_goal: int = 10_000
    water_goal_l: float = 2.0
    calorie_goal: int = 2_000
    activity_level: str = "balanced"
    sport_focus: str = "mixed"

    @classmethod
    def build(
        cls,
        display_name: Any,
        *,
        profile_id: int | None = None,
        avatar: str = "nova",
        language: str = "en",
        theme: str = "aurora",
        step_goal: Any = 10_000,
        water_goal_l: Any = 2.0,
        calorie_goal: Any = 2_000,
        activity_level: str = "balanced",
        sport_focus: str = "mixed",
    ) -> "UserProfile":
        """Create a validated user profile.

        Args:
            display_name: Name shown in selectors and reports.
            profile_id: Existing database identifier.
            avatar: Stable avatar key.
            language: Interface language.
            theme: Visual theme.
            step_goal: Daily step target.
            water_goal_l: Hydration target.
            calorie_goal: Descriptive calorie reference.
            activity_level: Gentle, balanced, or active preference.
            sport_focus: Preferred activity category.

        Returns:
            Validated immutable profile.

        Raises:
            ValueError: If a field is unsupported or outside safe bounds.

        Example:
            >>> UserProfile.build('Lirioth', sport_focus='walking').sport_focus
            'walking'
        """
        name = clean_text(display_name, "Display name", 48)
        if not name:
            raise ValueError("Display name is required.")
        avatar_key = avatar.strip().lower()
        if avatar_key not in PROFILE_AVATARS:
            raise ValueError(f"Unsupported avatar: {avatar}")
        level = activity_level.strip().lower()
        if level not in ACTIVITY_LEVELS:
            raise ValueError(f"Unsupported activity level: {activity_level}")
        focus = sport_focus.strip().lower()
        if focus not in SPORT_FOCUSES:
            raise ValueError(f"Unsupported sport focus: {sport_focus}")
        return cls(
            profile_id=profile_id,
            display_name=name,
            avatar=avatar_key,
            language=normalize_language(language),
            theme=normalize_theme_id(theme),
            step_goal=validate_non_negative_int(step_goal, "Step goal", 200_000) or 1,
            water_goal_l=validate_non_negative_float(water_goal_l, "Water goal", 20.0) or 0.1,
            calorie_goal=validate_non_negative_int(calorie_goal, "Calorie goal", 20_000) or 1,
            activity_level=level,
            sport_focus=focus,
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible profile dictionary.

        Returns:
            Serializable dictionary.

        Example:
            >>> UserProfile.build('Kevin').to_dict()['display_name']
            'Kevin'
        """
        return asdict(self)
