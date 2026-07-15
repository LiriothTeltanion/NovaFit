"""
Module: visual themes
Purpose: Centralize accessible UI and chart palettes so every NovaFit surface
    can share the same theme identity without duplicating color constants.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Standard library only; comments in ENGLISH; emojis sparingly.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True, slots=True)
class ThemeDefinition:
    """Describe one complete NovaFit visual theme.

    Args:
        theme_id: Stable identifier stored in configuration.
        label: Human-friendly label displayed in the GUI.
        mode: Broad light/dark classification.
        ui: Tkinter palette.
        chart: Matplotlib/HTML palette.

    Example:
        >>> get_theme("aurora").label
        'Aurora Borealis'
    """

    theme_id: str
    label: str
    mode: str
    ui: Mapping[str, str]
    chart: Mapping[str, str]


def _theme(
    theme_id: str,
    label: str,
    mode: str,
    *,
    bg: str,
    panel: str,
    panel_alt: str,
    text: str,
    muted: str,
    accent: str,
    accent_alt: str,
    success: str,
    warning: str,
    danger: str,
    border: str,
    blue: str,
    pink: str,
) -> ThemeDefinition:
    """Build one normalized theme definition.

    Args:
        theme_id: Stable theme key.
        label: Display label.
        mode: ``dark`` or ``light``.
        bg: Main background.
        panel: Primary panel surface.
        panel_alt: Raised-card surface.
        text: Primary text.
        muted: Secondary text.
        accent: Main accent.
        accent_alt: Secondary accent.
        success: Positive signal.
        warning: Caution signal.
        danger: Error signal.
        border: Divider color.
        blue: Additional chart accent.
        pink: Additional chart accent.

    Returns:
        Complete theme definition.

    Example:
        >>> _theme("x", "X", "dark", bg="#000", panel="#111", panel_alt="#222", text="#fff", muted="#aaa", accent="#0ff", accent_alt="#f0f", success="#0f0", warning="#ff0", danger="#f00", border="#333", blue="#00f", pink="#f0a").theme_id
        'x'
    """
    return ThemeDefinition(
        theme_id=theme_id,
        label=label,
        mode=mode,
        ui={
            "bg": bg,
            "panel": panel,
            "panel_alt": panel_alt,
            "text": text,
            "muted": muted,
            "accent": accent,
            "accent_alt": accent_alt,
            "success": success,
            "warning": warning,
            "danger": danger,
            "border": border,
            "blue": blue,
            "pink": pink,
        },
        chart={
            "background": bg,
            "panel": panel,
            "panel_alt": panel_alt,
            "text": text,
            "muted": muted,
            "grid": border,
            "cyan": accent,
            "blue": blue,
            "purple": accent_alt,
            "green": success,
            "amber": warning,
            "pink": pink,
            "red": danger,
        },
    )


THEMES: dict[str, ThemeDefinition] = {
    "midnight": _theme(
        "midnight", "Midnight Neon", "dark",
        bg="#050b16", panel="#0b1828", panel_alt="#10243a", text="#e8f5ff",
        muted="#91a8bd", accent="#22d3ee", accent_alt="#a78bfa",
        success="#34d399", warning="#fbbf24", danger="#fb7185",
        border="#28445f", blue="#38bdf8", pink="#f472b6",
    ),
    "aurora": _theme(
        "aurora", "Aurora Borealis", "dark",
        bg="#061314", panel="#0a2223", panel_alt="#103334", text="#ecfffb",
        muted="#95c6bf", accent="#2dd4bf", accent_alt="#c084fc",
        success="#4ade80", warning="#facc15", danger="#fb7185",
        border="#255b58", blue="#38bdf8", pink="#f0abfc",
    ),
    "desert": _theme(
        "desert", "Negev Sunrise", "dark",
        bg="#1a0d08", panel="#2a1710", panel_alt="#3a2117", text="#fff7ed",
        muted="#d6b49f", accent="#fb923c", accent_alt="#f472b6",
        success="#84cc16", warning="#fbbf24", danger="#f87171",
        border="#6b3c25", blue="#60a5fa", pink="#fb7185",
    ),
    "ocean": _theme(
        "ocean", "Ocean Depth", "dark",
        bg="#03111f", panel="#07233b", panel_alt="#0c3150", text="#ecfeff",
        muted="#8cc5d9", accent="#38bdf8", accent_alt="#818cf8",
        success="#2dd4bf", warning="#fbbf24", danger="#f43f5e",
        border="#1b5578", blue="#60a5fa", pink="#e879f9",
    ),
    "forest": _theme(
        "forest", "Forest Focus", "dark",
        bg="#07140d", panel="#0d2417", panel_alt="#163522", text="#f0fdf4",
        muted="#9ac4a7", accent="#4ade80", accent_alt="#22d3ee",
        success="#86efac", warning="#facc15", danger="#fb7185",
        border="#2f6040", blue="#38bdf8", pink="#f9a8d4",
    ),
    "rose": _theme(
        "rose", "Rose Quartz", "dark",
        bg="#180a14", panel="#2a1022", panel_alt="#3a1730", text="#fff1f7",
        muted="#d5a4bf", accent="#f472b6", accent_alt="#c084fc",
        success="#34d399", warning="#fbbf24", danger="#fb7185",
        border="#6a2e52", blue="#60a5fa", pink="#f9a8d4",
    ),
    "cloud": _theme(
        "cloud", "Cloud Day", "light",
        bg="#edf7fb", panel="#ffffff", panel_alt="#e5f3f8", text="#102a43",
        muted="#526d82", accent="#0891b2", accent_alt="#7c3aed",
        success="#059669", warning="#b45309", danger="#be123c",
        border="#bfd8e2", blue="#0284c7", pink="#be185d",
    ),
    "solar": _theme(
        "solar", "Solar Paper", "light",
        bg="#fff8e7", panel="#fffdf7", panel_alt="#f7ecd0", text="#3d2b1f",
        muted="#786554", accent="#d97706", accent_alt="#7c3aed",
        success="#15803d", warning="#a16207", danger="#be123c",
        border="#ddc99f", blue="#0369a1", pink="#be185d",
    ),
    "contrast": _theme(
        "contrast", "High Contrast", "dark",
        bg="#000000", panel="#0a0a0a", panel_alt="#171717", text="#ffffff",
        muted="#d4d4d4", accent="#facc15", accent_alt="#22d3ee",
        success="#4ade80", warning="#fde047", danger="#fb7185",
        border="#737373", blue="#60a5fa", pink="#f472b6",
    ),
    "sapphire": _theme(
        "sapphire", "Royal Sapphire", "dark",
        bg="#050818", panel="#0b1230", panel_alt="#111d47", text="#eef4ff",
        muted="#9eacd8", accent="#4f8cff", accent_alt="#8b5cf6",
        success="#22c55e", warning="#f59e0b", danger="#fb7185",
        border="#2b3f7d", blue="#38bdf8", pink="#ec4899",
    ),
    "lime": _theme(
        "lime", "Cyber Lime", "dark",
        bg="#071007", panel="#0d1c0d", panel_alt="#152b15", text="#f6ffe8",
        muted="#a9c795", accent="#a3e635", accent_alt="#22d3ee",
        success="#4ade80", warning="#fde047", danger="#fb7185",
        border="#3f6330", blue="#38bdf8", pink="#f472b6",
    ),
    "arcade": _theme(
        "arcade", "Sunset Arcade", "dark",
        bg="#16071f", panel="#261033", panel_alt="#381347", text="#fff2fb",
        muted="#d4a4cf", accent="#fb7185", accent_alt="#f97316",
        success="#2dd4bf", warning="#facc15", danger="#ef4444",
        border="#713260", blue="#60a5fa", pink="#f0abfc",
    ),
}

THEME_ALIASES = {
    "dark": "midnight",
    "light": "cloud",
    "neon": "midnight",
    "borealis": "aurora",
    "negev": "desert",
    "high_contrast": "contrast",
    "royal": "sapphire",
    "cyber": "lime",
    "sunset": "arcade",
}


def normalize_theme_id(value: str) -> str:
    """Normalize a theme key or display label.

    Args:
        value: Theme identifier, legacy alias, or display label.

    Returns:
        Stable theme identifier.

    Raises:
        ValueError: If the theme is unsupported.

    Example:
        >>> normalize_theme_id("Cloud Day")
        'cloud'
    """
    normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
    normalized = THEME_ALIASES.get(normalized, normalized)
    if normalized in THEMES:
        return normalized
    for theme_id, definition in THEMES.items():
        if normalized == definition.label.lower().replace(" ", "_"):
            return theme_id
    raise ValueError(f"Unsupported theme: {value}")


def get_theme(value: str) -> ThemeDefinition:
    """Return a normalized theme definition.

    Args:
        value: Theme key, alias, or display label.

    Returns:
        Theme definition.

    Raises:
        ValueError: If the theme is unsupported.

    Example:
        >>> get_theme("dark").theme_id
        'midnight'
    """
    return THEMES[normalize_theme_id(value)]


def theme_labels() -> tuple[str, ...]:
    """Return theme labels in curated display order.

    Returns:
        Ordered labels for a GUI combobox.

    Example:
        >>> "Aurora Borealis" in theme_labels()
        True
    """
    return tuple(theme.label for theme in THEMES.values())


def theme_ids() -> tuple[str, ...]:
    """Return stable theme identifiers.

    Returns:
        Ordered identifiers.

    Example:
        >>> "midnight" in theme_ids()
        True
    """
    return tuple(THEMES)


def theme_label(value: str) -> str:
    """Return the display label for a theme value.

    Args:
        value: Theme key, alias, or label.

    Returns:
        Human-friendly label.

    Example:
        >>> theme_label("desert")
        'Negev Sunrise'
    """
    return get_theme(value).label


def next_theme(value: str) -> str:
    """Cycle to the next curated theme.

    Args:
        value: Current theme value.

    Returns:
        Next stable theme identifier.

    Example:
        >>> next_theme("midnight")
        'aurora'
    """
    keys = theme_ids()
    current = normalize_theme_id(value)
    return keys[(keys.index(current) + 1) % len(keys)]
