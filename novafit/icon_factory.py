"""
Module: icon factory
Purpose: Draw lightweight, theme-aware PNG icons for Tkinter without shipping
    a third-party icon font or relying on platform-specific emoji rendering.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Pillow only; icons are decorative and paired with readable labels.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


class IconFactory:
    """Create and cache small vector-like Tkinter icons with Pillow.

    Args:
        root: Tkinter root used by ``ImageTk.PhotoImage``.

    Example:
        >>> factory = IconFactory(root)  # doctest: +SKIP
        >>> icon = factory.get('dashboard', palette)  # doctest: +SKIP
    """

    def __init__(self, root: Any) -> None:
        self.root = root
        self._cache: dict[tuple[str, str, str, int], Any] = {}

    def get(self, name: str, palette: Mapping[str, str], size: int = 30) -> Any:
        """Return one theme-aware icon image.

        Args:
            name: Stable icon name.
            palette: Active UI palette.
            size: Square image size in pixels.

        Returns:
            ``ImageTk.PhotoImage`` retained in the factory cache.

        Raises:
            ImportError: If Pillow is unavailable.
            ValueError: If size is outside a sensible GUI range.

        Example:
            >>> factory.get('user', palette, 28)  # doctest: +SKIP
        """
        if not 18 <= size <= 96:
            raise ValueError("Icon size must be between 18 and 96 pixels.")
        key = (name, palette["accent"], palette["panel_alt"], size)
        if key in self._cache:
            return self._cache[key]

        from PIL import Image, ImageDraw, ImageTk

        scale = 4
        canvas_size = size * scale
        image = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        accent = palette["accent"]
        accent_alt = palette["accent_alt"]
        panel = palette["panel_alt"]
        border = palette["border"]
        pad = 2 * scale
        radius = 8 * scale
        draw.rounded_rectangle(
            (pad, pad, canvas_size - pad, canvas_size - pad),
            radius=radius,
            fill=panel,
            outline=border,
            width=max(1, scale),
        )
        self._draw_symbol(draw, name, canvas_size, accent, accent_alt, scale)
        image = image.resize((size, size), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image=image, master=self.root)
        self._cache[key] = photo
        return photo

    @staticmethod
    def _draw_symbol(draw: Any, name: str, size: int, accent: str, accent_alt: str, scale: int) -> None:
        """Draw one simple symbol using lines and shapes."""
        cx = cy = size / 2
        width = max(2, 2 * scale)
        if name == "dashboard":
            for x, y, w, h in ((0.26, 0.28, 0.18, 0.18), (0.56, 0.28, 0.18, 0.3), (0.26, 0.56, 0.18, 0.18), (0.56, 0.68, 0.18, 0.06)):
                draw.rounded_rectangle((size*x, size*y, size*(x+w), size*(y+h)), radius=2*scale, fill=accent if y < 0.5 else accent_alt)
        elif name == "motivation":
            points = [(cx, size*0.22), (size*0.58, size*0.42), (size*0.8, size*0.45), (size*0.63, size*0.59), (size*0.68, size*0.8), (cx, size*0.68), (size*0.32, size*0.8), (size*0.37, size*0.59), (size*0.2, size*0.45), (size*0.42, size*0.42)]
            draw.polygon(points, fill=accent)
            draw.ellipse((size*0.43, size*0.39, size*0.57, size*0.53), fill=accent_alt)
        elif name == "recommendations":
            draw.arc((size*0.22, size*0.2, size*0.78, size*0.76), 195, 525, fill=accent, width=width)
            draw.line((size*0.34, size*0.62, size*0.5, size*0.76, size*0.7, size*0.43), fill=accent_alt, width=width, joint="curve")
            draw.ellipse((size*0.45, size*0.23, size*0.57, size*0.35), fill=accent_alt)
        elif name == "add":
            draw.ellipse((size*0.23, size*0.23, size*0.77, size*0.77), outline=accent, width=width)
            draw.line((cx, size*0.35, cx, size*0.65), fill=accent_alt, width=width)
            draw.line((size*0.35, cy, size*0.65, cy), fill=accent_alt, width=width)
        elif name == "records":
            for y in (0.32, 0.5, 0.68):
                draw.ellipse((size*0.24, size*(y-0.035), size*0.31, size*(y+0.035)), fill=accent_alt)
                draw.line((size*0.36, size*y, size*0.75, size*y), fill=accent, width=width)
        elif name == "profiles":
            draw.ellipse((size*0.35, size*0.22, size*0.65, size*0.52), fill=accent)
            draw.rounded_rectangle((size*0.23, size*0.56, size*0.77, size*0.78), radius=8*scale, fill=accent_alt)
        elif name == "tools":
            draw.ellipse((size*0.31, size*0.31, size*0.69, size*0.69), outline=accent, width=width)
            draw.ellipse((size*0.43, size*0.43, size*0.57, size*0.57), fill=accent_alt)
            for angle in range(0, 360, 45):
                import math
                x1 = cx + math.cos(math.radians(angle)) * size * 0.2
                y1 = cy + math.sin(math.radians(angle)) * size * 0.2
                x2 = cx + math.cos(math.radians(angle)) * size * 0.31
                y2 = cy + math.sin(math.radians(angle)) * size * 0.31
                draw.line((x1, y1, x2, y2), fill=accent, width=width)
        elif name == "language":
            draw.ellipse((size*0.22, size*0.22, size*0.78, size*0.78), outline=accent, width=width)
            draw.arc((size*0.35, size*0.22, size*0.65, size*0.78), 90, 270, fill=accent_alt, width=width)
            draw.arc((size*0.35, size*0.22, size*0.65, size*0.78), -90, 90, fill=accent_alt, width=width)
            draw.line((size*0.24, cy, size*0.76, cy), fill=accent, width=width)
        elif name == "theme":
            draw.ellipse((size*0.22, size*0.22, size*0.78, size*0.78), fill=accent)
            draw.pieslice((size*0.22, size*0.22, size*0.78, size*0.78), 90, 210, fill=accent_alt)
            draw.ellipse((size*0.45, size*0.42, size*0.62, size*0.59), fill="#ffffff")
        else:
            draw.ellipse((size*0.3, size*0.3, size*0.7, size*0.7), fill=accent)
            draw.ellipse((size*0.43, size*0.43, size*0.57, size*0.57), fill=accent_alt)
