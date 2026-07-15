"""
Module: icon factory
Purpose: Draw crisp, theme-aware icons for Tkinter without a platform-specific
    icon font or unreliable emoji rendering.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-16 | TZ: Asia/Jerusalem
Notes: Pillow only; navigation icons remain paired with readable labels.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any


ICON_NAMES: tuple[str, ...] = (
    "app",
    "dashboard",
    "motivation",
    "recommendations",
    "add",
    "records",
    "profiles",
    "tools",
    "language",
    "theme",
)

_ALIASES = {
    "analytics": "dashboard",
    "coach": "recommendations",
    "entry": "add",
    "history": "records",
    "profile": "profiles",
    "user": "profiles",
    "settings": "tools",
}


class IconFactory:
    """Create and cache antialiased, vector-like Tkinter icons with Pillow."""

    def __init__(self, root: Any) -> None:
        self.root = root
        self._cache: dict[tuple[str, str, str, str, str, int, str], Any] = {}

    def get(
        self,
        name: str,
        palette: Mapping[str, str],
        size: int = 30,
        *,
        state: str = "default",
    ) -> Any:
        """Return one retained ``ImageTk.PhotoImage``.

        Args:
            name: Stable icon name or documented alias.
            palette: Active UI palette.
            size: Square image size in pixels, from 16 to 96.
            state: ``default``, ``active``, or ``muted``.

        Raises:
            ImportError: If Pillow is unavailable.
            ValueError: If the size, name, or state is unsupported.
        """
        canonical_name = self._validate(name, size, state)
        key = (
            canonical_name,
            palette["accent"],
            palette["accent_alt"],
            palette["panel_alt"],
            palette["border"],
            size,
            state,
        )
        if key in self._cache:
            return self._cache[key]

        from PIL import ImageTk

        image = self.render(canonical_name, palette, size, state=state)
        photo = ImageTk.PhotoImage(image=image, master=self.root)
        self._cache[key] = photo
        return photo

    @classmethod
    def render(
        cls,
        name: str,
        palette: Mapping[str, str],
        size: int = 30,
        *,
        state: str = "default",
    ) -> Any:
        """Return a headless-testable Pillow image for one icon."""
        canonical_name = cls._validate(name, size, state)
        from PIL import Image, ImageDraw

        scale = 4
        canvas_size = size * scale
        image = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        accent = palette["muted"] if state == "muted" else palette["accent"]
        accent_alt = palette["muted"] if state == "muted" else palette["accent_alt"]
        panel = palette["panel_alt"]
        border = palette["accent"] if state == "active" else palette["border"]
        pad = 2 * scale
        radius = max(5, round(size * 0.24)) * scale
        draw.rounded_rectangle(
            (pad, pad, canvas_size - pad - 1, canvas_size - pad - 1),
            radius=radius,
            fill=panel,
            outline=border,
            width=(2 if state == "active" else 1) * scale,
        )
        cls._draw_symbol(draw, canonical_name, canvas_size, accent, accent_alt, scale)
        return image.resize((size, size), Image.Resampling.LANCZOS)

    def clear(self) -> None:
        """Release cached PhotoImage references after a major theme reset."""
        self._cache.clear()

    @staticmethod
    def _validate(name: str, size: int, state: str) -> str:
        if not 16 <= size <= 96:
            raise ValueError("Icon size must be between 16 and 96 pixels.")
        if state not in {"default", "active", "muted"}:
            raise ValueError("Icon state must be default, active, or muted.")
        canonical_name = _ALIASES.get(name.strip().lower(), name.strip().lower())
        if canonical_name not in ICON_NAMES:
            choices = ", ".join(ICON_NAMES)
            raise ValueError(f"Unsupported icon: {name}. Choose one of: {choices}.")
        return canonical_name

    @staticmethod
    def _draw_symbol(
        draw: Any,
        name: str,
        size: int,
        accent: str,
        accent_alt: str,
        scale: int,
    ) -> None:
        """Draw one optically balanced symbol on a shared 24-style grid."""
        cx = cy = size / 2
        stroke = max(2 * scale, round(size * 0.045))
        thin = max(scale, round(size * 0.028))

        if name == "app":
            draw.ellipse((size * 0.27, size * 0.25, size * 0.53, size * 0.52), fill=accent)
            draw.ellipse((size * 0.47, size * 0.25, size * 0.73, size * 0.52), fill=accent)
            draw.polygon(
                (
                    (size * 0.27, size * 0.40),
                    (size * 0.73, size * 0.40),
                    (size * 0.50, size * 0.76),
                ),
                fill=accent,
            )
            draw.line(
                (
                    size * 0.24,
                    size * 0.50,
                    size * 0.39,
                    size * 0.50,
                    size * 0.45,
                    size * 0.38,
                    size * 0.53,
                    size * 0.62,
                    size * 0.60,
                    size * 0.50,
                    size * 0.76,
                    size * 0.50,
                ),
                fill=accent_alt,
                width=thin,
                joint="curve",
            )
        elif name == "dashboard":
            boxes = (
                (0.25, 0.25, 0.46, 0.47),
                (0.54, 0.25, 0.75, 0.60),
                (0.25, 0.55, 0.46, 0.75),
                (0.54, 0.68, 0.75, 0.75),
            )
            for index, box in enumerate(boxes):
                draw.rounded_rectangle(
                    tuple(size * value for value in box),
                    radius=2 * scale,
                    fill=accent if index in {0, 3} else accent_alt,
                )
        elif name == "motivation":
            points: list[tuple[float, float]] = []
            for index in range(10):
                angle = -math.pi / 2 + index * math.pi / 5
                radius = size * (0.29 if index % 2 == 0 else 0.13)
                points.append((cx + math.cos(angle) * radius, cy + math.sin(angle) * radius))
            draw.polygon(points, fill=accent)
            draw.ellipse((size * 0.44, size * 0.44, size * 0.56, size * 0.56), fill=accent_alt)
        elif name == "recommendations":
            draw.ellipse((size * 0.30, size * 0.23, size * 0.70, size * 0.63), outline=accent, width=stroke)
            draw.line((size * 0.40, size * 0.69, size * 0.60, size * 0.69), fill=accent, width=stroke)
            draw.line((size * 0.43, size * 0.76, size * 0.57, size * 0.76), fill=accent, width=thin)
            draw.line(
                (size * 0.39, size * 0.48, size * 0.48, size * 0.56, size * 0.63, size * 0.39),
                fill=accent_alt,
                width=stroke,
                joint="curve",
            )
        elif name == "add":
            draw.ellipse((size * 0.23, size * 0.23, size * 0.77, size * 0.77), outline=accent, width=stroke)
            draw.line((cx, size * 0.35, cx, size * 0.65), fill=accent_alt, width=stroke)
            draw.line((size * 0.35, cy, size * 0.65, cy), fill=accent_alt, width=stroke)
        elif name == "records":
            draw.rounded_rectangle(
                (size * 0.25, size * 0.22, size * 0.75, size * 0.79),
                radius=3 * scale,
                outline=accent,
                width=thin,
            )
            draw.rounded_rectangle(
                (size * 0.39, size * 0.18, size * 0.61, size * 0.29),
                radius=2 * scale,
                fill=accent_alt,
            )
            for y in (0.41, 0.55, 0.69):
                draw.ellipse(
                    (size * 0.33, size * (y - 0.025), size * 0.38, size * (y + 0.025)),
                    fill=accent_alt,
                )
                draw.line((size * 0.43, size * y, size * 0.67, size * y), fill=accent, width=thin)
        elif name == "profiles":
            draw.ellipse((size * 0.37, size * 0.22, size * 0.63, size * 0.48), fill=accent)
            draw.rounded_rectangle(
                (size * 0.25, size * 0.53, size * 0.75, size * 0.77),
                radius=7 * scale,
                fill=accent_alt,
            )
            draw.ellipse((size * 0.65, size * 0.31, size * 0.77, size * 0.43), fill=accent_alt)
        elif name == "tools":
            draw.ellipse((size * 0.33, size * 0.33, size * 0.67, size * 0.67), outline=accent, width=stroke)
            draw.ellipse((size * 0.43, size * 0.43, size * 0.57, size * 0.57), fill=accent_alt)
            for angle in range(0, 360, 45):
                radians = math.radians(angle)
                x1 = cx + math.cos(radians) * size * 0.19
                y1 = cy + math.sin(radians) * size * 0.19
                x2 = cx + math.cos(radians) * size * 0.29
                y2 = cy + math.sin(radians) * size * 0.29
                draw.line((x1, y1, x2, y2), fill=accent, width=stroke)
        elif name == "language":
            draw.ellipse((size * 0.22, size * 0.22, size * 0.78, size * 0.78), outline=accent, width=stroke)
            globe = (size * 0.35, size * 0.22, size * 0.65, size * 0.78)
            draw.arc(globe, 90, 270, fill=accent_alt, width=thin)
            draw.arc(globe, -90, 90, fill=accent_alt, width=thin)
            draw.line((size * 0.24, cy, size * 0.76, cy), fill=accent, width=thin)
        elif name == "theme":
            draw.pieslice((size * 0.22, size * 0.22, size * 0.78, size * 0.78), 90, 270, fill=accent)
            draw.pieslice((size * 0.22, size * 0.22, size * 0.78, size * 0.78), 270, 450, fill=accent_alt)
            draw.ellipse((size * 0.41, size * 0.33, size * 0.50, size * 0.42), fill=accent_alt)
            draw.ellipse((size * 0.50, size * 0.58, size * 0.59, size * 0.67), fill=accent)
