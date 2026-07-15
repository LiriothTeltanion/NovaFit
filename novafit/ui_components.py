"""
Module: reusable Tkinter components
Purpose: Provide subtle motion and visual identity without mixing decorative UI code
    into NovaFit's data or analytics layers.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Tkinter stdlib only; comments in ENGLISH; emojis sparingly.
"""

from __future__ import annotations

import math
import tkinter as tk
from collections.abc import Mapping


class NovaPulseCanvas(tk.Canvas):
    """Render a lightweight animated NovaFit pulse-and-orbit header.

    Args:
        master: Parent Tkinter widget.
        palette: Mapping containing ``bg``, ``accent``, ``accent_alt``, and ``muted``.
        reduced_motion: Draw a static frame instead of scheduling animation.

    Example:
        >>> pulse = NovaPulseCanvas(root, palette)  # doctest: +SKIP
    """

    def __init__(
        self,
        master: tk.Misc,
        palette: Mapping[str, str],
        *,
        reduced_motion: bool = False,
    ) -> None:
        super().__init__(
            master,
            width=285,
            height=74,
            highlightthickness=0,
            bd=0,
            background=palette["bg"],
        )
        self._palette = dict(palette)
        self._reduced_motion = reduced_motion
        self._phase = 0.0
        self._after_id: str | None = None
        self.bind("<Destroy>", self._on_destroy, add="+")
        self._draw_frame()
        if not reduced_motion:
            self._schedule()

    def set_palette(self, palette: Mapping[str, str]) -> None:
        """Apply a new light or dark palette and redraw immediately.

        Args:
            palette: NovaFit UI color mapping.

        Returns:
            None.

        Example:
            >>> pulse.set_palette(light_palette)  # doctest: +SKIP
        """
        self._palette = dict(palette)
        self.configure(background=palette["bg"])
        self._draw_frame()

    def set_language(self, language: str) -> None:
        """Update localized hero copy and redraw.

        Args:
            language: Supported ``en``, ``es``, or ``he`` code.

        Returns:
            None.

        Example:
            >>> art.set_language("he")  # doctest: +SKIP
        """
        self._language = language if language in {"en", "es", "he"} else "en"
        self._draw_frame()

    def set_reduced_motion(self, reduced_motion: bool) -> None:
        """Enable or disable decorative animation.

        Args:
            reduced_motion: ``True`` for a static header.

        Returns:
            None.

        Example:
            >>> pulse.set_reduced_motion(True)  # doctest: +SKIP
        """
        self._reduced_motion = reduced_motion
        if reduced_motion and self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None
        elif not reduced_motion and self._after_id is None:
            self._schedule()
        self._draw_frame()

    def _schedule(self) -> None:
        self._after_id = self.after(55, self._animate)

    def _animate(self) -> None:
        self._phase = (self._phase + 0.08) % (math.tau)
        self._draw_frame()
        if not self._reduced_motion:
            self._schedule()

    def _draw_frame(self) -> None:
        self.delete("all")
        palette = self._palette
        center_x, center_y = 226, 37
        pulse = 2.5 + (math.sin(self._phase) + 1) * 1.8

        # A small ECG-like signal reinforces the product purpose without visual noise.
        points = [
            6, 39,
            46, 39,
            61, 29,
            75, 51,
            91, 16,
            108, 45,
            128, 36,
            151, 39,
        ]
        self.create_line(*points, fill=palette["accent"], width=2.2, smooth=True)
        self.create_oval(88 - pulse, 16 - pulse, 88 + pulse, 16 + pulse, fill=palette["accent_alt"], outline="")

        for radius, alpha_color in ((29, palette["border"]), (21, palette["accent_alt"])):
            self.create_oval(
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
                outline=alpha_color,
                width=1.2,
            )

        orbit_x = center_x + math.cos(self._phase) * 27
        orbit_y = center_y + math.sin(self._phase) * 15
        self.create_oval(orbit_x - 4, orbit_y - 4, orbit_x + 4, orbit_y + 4, fill=palette["accent"], outline="")
        self.create_oval(center_x - 8, center_y - 8, center_x + 8, center_y + 8, fill=palette["accent_alt"], outline="")
        self.create_text(
            151,
            62,
            text="LOCAL DATA  •  CLEAR SIGNALS",
            anchor="w",
            fill=palette["muted"],
            font=("Segoe UI", 7, "bold"),
        )

    def _on_destroy(self, _event: tk.Event[tk.Misc]) -> None:
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except tk.TclError:
                pass
            self._after_id = None


class MotivationGalaxyCanvas(tk.Canvas):
    """Render a lightweight animated motivation galaxy.

    Args:
        master: Parent Tkinter widget.
        palette: Active NovaFit UI palette.
        reduced_motion: Draw a static composition when true.

    Example:
        >>> galaxy = MotivationGalaxyCanvas(root, palette)  # doctest: +SKIP
    """

    def __init__(
        self,
        master: tk.Misc,
        palette: Mapping[str, str],
        *,
        reduced_motion: bool = False,
        height: int = 150,
    ) -> None:
        super().__init__(
            master,
            height=height,
            highlightthickness=0,
            bd=0,
            background=palette["panel"],
        )
        self._palette = dict(palette)
        self._reduced_motion = reduced_motion
        self._phase = 0.0
        self._after_id: str | None = None
        self._spark_level = 1
        self.bind("<Configure>", lambda _event: self._draw_frame(), add="+")
        self.bind("<Destroy>", self._on_destroy, add="+")
        self._draw_frame()
        if not reduced_motion:
            self._schedule()

    def set_palette(self, palette: Mapping[str, str]) -> None:
        """Apply a new palette and redraw.

        Args:
            palette: NovaFit UI palette.

        Returns:
            None.

        Example:
            >>> galaxy.set_palette(palette)  # doctest: +SKIP
        """
        self._palette = dict(palette)
        self.configure(background=palette["panel"])
        self._draw_frame()

    def set_language(self, language: str) -> None:
        """Update localized hero copy and redraw.

        Args:
            language: Supported ``en``, ``es``, or ``he`` code.

        Returns:
            None.

        Example:
            >>> art.set_language("he")  # doctest: +SKIP
        """
        self._language = language if language in {"en", "es", "he"} else "en"
        self._draw_frame()

    def set_reduced_motion(self, reduced_motion: bool) -> None:
        """Enable or disable galaxy animation.

        Args:
            reduced_motion: Whether to draw only a static frame.

        Returns:
            None.

        Example:
            >>> galaxy.set_reduced_motion(True)  # doctest: +SKIP
        """
        self._reduced_motion = reduced_motion
        if reduced_motion and self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None
        elif not reduced_motion and self._after_id is None:
            self._schedule()
        self._draw_frame()

    def set_spark_level(self, level: int) -> None:
        """Set celebration intensity from zero to three.

        Args:
            level: Celebration intensity.

        Returns:
            None.

        Raises:
            ValueError: If the level is outside zero to three.

        Example:
            >>> galaxy.set_spark_level(2)  # doctest: +SKIP
        """
        if not 0 <= level <= 3:
            raise ValueError("Spark level must be between 0 and 3.")
        self._spark_level = level
        self._draw_frame()

    def celebrate(self) -> None:
        """Advance the animation and temporarily brighten the galaxy.

        Returns:
            None.

        Example:
            >>> galaxy.celebrate()  # doctest: +SKIP
        """
        self._spark_level = 3
        self._phase += 0.9
        self._draw_frame()
        self.after(1400, lambda: self.set_spark_level(1) if self.winfo_exists() else None)

    def _schedule(self) -> None:
        self._after_id = self.after(65, self._animate)

    def _animate(self) -> None:
        self._phase = (self._phase + 0.045) % math.tau
        self._draw_frame()
        if not self._reduced_motion:
            self._schedule()

    def _draw_frame(self) -> None:
        if not self.winfo_exists():
            return
        self.delete("all")
        palette = self._palette
        width = max(420, self.winfo_width())
        height = max(120, self.winfo_height())

        # Layered bands create a lightweight aurora without image dependencies.
        for index in range(7):
            y = int((index / 7) * height)
            color = palette["panel_alt"] if index % 2 == 0 else palette["panel"]
            self.create_rectangle(0, y, width, y + height / 7 + 2, fill=color, outline="")

        center_x, center_y = width * 0.76, height * 0.52
        orbit_count = 14 + self._spark_level * 5
        for index in range(orbit_count):
            angle = self._phase * (0.35 + (index % 4) * 0.08) + index * 0.78
            radius_x = 35 + (index % 5) * 16
            radius_y = 18 + (index % 4) * 9
            x = center_x + math.cos(angle) * radius_x
            y = center_y + math.sin(angle) * radius_y
            radius = 1.5 + (index % 3) * 0.7
            color = (palette["accent"], palette["accent_alt"], palette.get("pink", palette["warning"]))[index % 3]
            self.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color, outline="")

        pulse = 14 + (math.sin(self._phase * 2) + 1) * 4
        self.create_oval(
            center_x - pulse,
            center_y - pulse,
            center_x + pulse,
            center_y + pulse,
            fill=palette["accent_alt"],
            outline=palette["accent"],
            width=2,
        )
        self.create_text(
            28,
            height * 0.30,
            anchor="w",
            text="BUILD THE NEXT REPEATABLE WIN",
            fill=palette["accent"],
            font=("Segoe UI", 10, "bold"),
        )
        self.create_text(
            28,
            height * 0.56,
            anchor="w",
            text="Evidence · rhythm · recovery · purpose",
            fill=palette["text"],
            font=("Segoe UI", 17, "bold"),
        )
        self.create_text(
            28,
            height * 0.78,
            anchor="w",
            text="Your data is a guide, never a judge.",
            fill=palette["muted"],
            font=("Segoe UI", 9),
        )

    def _on_destroy(self, _event: tk.Event[tk.Misc]) -> None:
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except tk.TclError:
                pass
            self._after_id = None


class FocusBreathingCanvas(tk.Canvas):
    """Provide a short visual focus-reset animation.

    Args:
        master: Parent Tkinter widget.
        palette: Active NovaFit palette.
        reduced_motion: Use a static ring when true.

    Example:
        >>> reset = FocusBreathingCanvas(root, palette)  # doctest: +SKIP
    """

    def __init__(
        self,
        master: tk.Misc,
        palette: Mapping[str, str],
        *,
        reduced_motion: bool = False,
    ) -> None:
        super().__init__(
            master,
            width=170,
            height=170,
            highlightthickness=0,
            bd=0,
            background=palette["panel_alt"],
        )
        self._palette = dict(palette)
        self._reduced_motion = reduced_motion
        self._running = False
        self._phase = 0.0
        self._ticks = 0
        self._after_id: str | None = None
        self.bind("<Destroy>", self._on_destroy, add="+")
        self._draw_frame()

    def start(self) -> None:
        """Start a sixty-second visual reset.

        Returns:
            None.

        Example:
            >>> reset.start()  # doctest: +SKIP
        """
        self._running = True
        self._ticks = 0
        if not self._reduced_motion and self._after_id is None:
            self._schedule()
        self._draw_frame()

    def stop(self) -> None:
        """Stop the focus-reset animation.

        Returns:
            None.

        Example:
            >>> reset.stop()  # doctest: +SKIP
        """
        self._running = False
        if self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None
        self._draw_frame()

    def set_palette(self, palette: Mapping[str, str]) -> None:
        """Apply a new palette.

        Args:
            palette: NovaFit UI palette.

        Returns:
            None.

        Example:
            >>> reset.set_palette(palette)  # doctest: +SKIP
        """
        self._palette = dict(palette)
        self.configure(background=palette["panel_alt"])
        self._draw_frame()

    def set_language(self, language: str) -> None:
        """Update localized hero copy and redraw.

        Args:
            language: Supported ``en``, ``es``, or ``he`` code.

        Returns:
            None.

        Example:
            >>> art.set_language("he")  # doctest: +SKIP
        """
        self._language = language if language in {"en", "es", "he"} else "en"
        self._draw_frame()

    def set_reduced_motion(self, reduced_motion: bool) -> None:
        """Update reduced-motion preference.

        Args:
            reduced_motion: Whether animation should be disabled.

        Returns:
            None.

        Example:
            >>> reset.set_reduced_motion(True)  # doctest: +SKIP
        """
        self._reduced_motion = reduced_motion
        if reduced_motion:
            self.stop()
        self._draw_frame()

    def _schedule(self) -> None:
        self._after_id = self.after(100, self._animate)

    def _animate(self) -> None:
        self._phase = (self._phase + 0.08) % math.tau
        self._ticks += 1
        if self._ticks >= 600:
            self.stop()
            return
        self._draw_frame()
        if self._running and not self._reduced_motion:
            self._schedule()

    def _draw_frame(self) -> None:
        self.delete("all")
        palette = self._palette
        center = 85
        wave = (math.sin(self._phase) + 1) / 2 if self._running else 0.35
        radius = 35 + wave * 25
        self.create_oval(20, 20, 150, 150, outline=palette["border"], width=2)
        self.create_oval(
            center - radius,
            center - radius,
            center + radius,
            center + radius,
            fill=palette["accent_alt"],
            outline=palette["accent"],
            width=2,
        )
        if not self._running:
            label = "60s RESET"
        elif math.sin(self._phase) >= 0:
            label = "BREATHE IN"
        else:
            label = "BREATHE OUT"
        self.create_text(center, center, text=label, fill=palette["text"], font=("Segoe UI", 9, "bold"))

    def _on_destroy(self, _event: tk.Event[tk.Misc]) -> None:
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except tk.TclError:
                pass
            self._after_id = None


class UltimateHeroCanvas(tk.Canvas):
    """Render a larger animated health-technology hero scene.

    Args:
        master: Parent Tkinter widget.
        palette: Active theme palette.
        reduced_motion: Draw a static scene when true.
        profile_name: Name displayed in the orbit label.

    Example:
        >>> art = UltimateHeroCanvas(root, palette, profile_name="Kevin")  # doctest: +SKIP
    """

    def __init__(
        self,
        master: tk.Misc,
        palette: Mapping[str, str],
        *,
        reduced_motion: bool = False,
        profile_name: str = "Primary User",
        language: str = "en",
        height: int = 188,
    ) -> None:
        super().__init__(master, height=height, highlightthickness=0, bd=0, background=palette["bg"])
        self._palette = dict(palette)
        self._reduced_motion = reduced_motion
        self._profile_name = profile_name
        self._language = language if language in {"en", "es", "he"} else "en"
        self._phase = 0.0
        self._after_id: str | None = None
        self.bind("<Configure>", lambda _event: self._draw_frame(), add="+")
        self.bind("<Destroy>", self._on_destroy, add="+")
        self._draw_frame()
        if not reduced_motion:
            self._schedule()

    def set_palette(self, palette: Mapping[str, str]) -> None:
        """Apply a theme palette and redraw."""
        self._palette = dict(palette)
        self.configure(background=palette["bg"])
        self._draw_frame()

    def set_profile_name(self, profile_name: str) -> None:
        """Update the active-profile label."""
        self._profile_name = profile_name
        self._draw_frame()

    def set_language(self, language: str) -> None:
        """Update localized hero copy and redraw.

        Args:
            language: Supported ``en``, ``es``, or ``he`` code.

        Returns:
            None.

        Example:
            >>> art.set_language("he")  # doctest: +SKIP
        """
        self._language = language if language in {"en", "es", "he"} else "en"
        self._draw_frame()

    def set_reduced_motion(self, reduced_motion: bool) -> None:
        """Enable or disable decorative animation."""
        self._reduced_motion = reduced_motion
        if reduced_motion and self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None
        elif not reduced_motion and self._after_id is None:
            self._schedule()
        self._draw_frame()

    def _schedule(self) -> None:
        self._after_id = self.after(48, self._animate)

    def _animate(self) -> None:
        self._phase = (self._phase + 0.035) % math.tau
        self._draw_frame()
        if not self._reduced_motion:
            self._schedule()

    def _draw_frame(self) -> None:
        if not self.winfo_exists():
            return
        self.delete("all")
        palette = self._palette
        width = max(760, self.winfo_width())
        height = max(170, self.winfo_height())

        # Layered horizontal bands and grid lines evoke a calm command center.
        self.create_rectangle(0, 0, width, height, fill=palette["panel"], outline="")
        for row in range(0, height, 24):
            self.create_line(0, row, width, row, fill=palette["border"], width=1)
        for column in range(0, width, 56):
            self.create_line(column, 0, column, height, fill=palette["border"], width=1)

        # A wide data wave travels across the hero without blocking interaction.
        points: list[float] = []
        for x in range(-20, width + 20, 9):
            wave = math.sin((x / 85) + self._phase * 2.2) * 14
            pulse = math.sin((x / 31) - self._phase * 1.3) * 4
            points.extend((x, height * 0.70 + wave + pulse))
        self.create_line(*points, fill=palette["accent"], width=2.2, smooth=True)

        center_x, center_y = width * 0.79, height * 0.48
        for index, radius in enumerate((65, 48, 31)):
            self.create_oval(
                center_x - radius,
                center_y - radius * 0.62,
                center_x + radius,
                center_y + radius * 0.62,
                outline=(palette["accent"], palette["accent_alt"], palette.get("blue", palette["accent"]))[index],
                width=1.4,
            )
        for index in range(18):
            angle = self._phase * (0.6 + (index % 3) * 0.12) + index * 0.57
            radius_x = 32 + (index % 5) * 10
            radius_y = 19 + (index % 4) * 7
            x = center_x + math.cos(angle) * radius_x
            y = center_y + math.sin(angle) * radius_y
            dot = 1.5 + (index % 3)
            color = (palette["accent"], palette["accent_alt"], palette.get("pink", palette["warning"]))[index % 3]
            self.create_oval(x-dot, y-dot, x+dot, y+dot, fill=color, outline="")
        core = 11 + (math.sin(self._phase * 2) + 1) * 3
        self.create_oval(center_x-core, center_y-core, center_x+core, center_y+core, fill=palette["accent_alt"], outline=palette["accent"], width=2)

        copy = {
            "en": (
                "NOVA HEALTH INTELLIGENCE",
                "TURN DAILY SIGNALS INTO A SUSTAINABLE SYSTEM",
                "Profiles · multilingual UI · analytics · recommendations · privacy",
                "ACTIVE PROFILE",
            ),
            "es": (
                "INTELIGENCIA DE BIENESTAR NOVA",
                "CONVIERTE SEÑALES DIARIAS EN UN SISTEMA SOSTENIBLE",
                "Perfiles · interfaz multilingüe · analítica · recomendaciones · privacidad",
                "PERFIL ACTIVO",
            ),
            "he": (
                "NOVA · תובנות רווחה",
                "הופכים אותות יומיים למערכת יציבה",
                "פרופילים · ממשק רב־לשוני · ניתוח · המלצות · פרטיות",
                "פרופיל פעיל",
            ),
        }[self._language]
        if self._language == "he":
            text_x = width - 34
            anchor = "e"
        else:
            text_x = 34
            anchor = "w"
        self.create_text(text_x, 38, text=copy[0], anchor=anchor, fill=palette["accent"], font=("Segoe UI", 10, "bold"))
        self.create_text(text_x, 75, text=copy[1], anchor=anchor, fill=palette["text"], font=("Segoe UI", 19, "bold"))
        self.create_text(text_x, 111, text=copy[2], anchor=anchor, fill=palette["muted"], font=("Segoe UI", 10))
        self.create_text(center_x, height - 18, text=f"{copy[3]}  •  {self._profile_name.upper()}", fill=palette["muted"], font=("Segoe UI", 8, "bold"))

    def _on_destroy(self, _event: tk.Event[tk.Misc]) -> None:
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except tk.TclError:
                pass
            self._after_id = None


class ActivityOrbitCanvas(tk.Canvas):
    """Render an animated orbit for the recommendation workspace."""

    def __init__(self, master: tk.Misc, palette: Mapping[str, str], *, reduced_motion: bool = False) -> None:
        super().__init__(master, width=240, height=150, highlightthickness=0, bd=0, background=palette["panel"])
        self._palette = dict(palette)
        self._reduced_motion = reduced_motion
        self._phase = 0.0
        self._after_id: str | None = None
        self.bind("<Destroy>", self._on_destroy, add="+")
        self._draw_frame()
        if not reduced_motion:
            self._schedule()

    def set_palette(self, palette: Mapping[str, str]) -> None:
        """Apply a new theme palette."""
        self._palette = dict(palette)
        self.configure(background=palette["panel"])
        self._draw_frame()

    def set_language(self, language: str) -> None:
        """Update localized hero copy and redraw.

        Args:
            language: Supported ``en``, ``es``, or ``he`` code.

        Returns:
            None.

        Example:
            >>> art.set_language("he")  # doctest: +SKIP
        """
        self._language = language if language in {"en", "es", "he"} else "en"
        self._draw_frame()

    def set_reduced_motion(self, reduced_motion: bool) -> None:
        """Update the reduced-motion preference."""
        self._reduced_motion = reduced_motion
        if reduced_motion and self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None
        elif not reduced_motion and self._after_id is None:
            self._schedule()

    def _schedule(self) -> None:
        self._after_id = self.after(55, self._animate)

    def _animate(self) -> None:
        self._phase = (self._phase + 0.05) % math.tau
        self._draw_frame()
        if not self._reduced_motion:
            self._schedule()

    def _draw_frame(self) -> None:
        self.delete("all")
        palette = self._palette
        cx, cy = 120, 75
        for index, (rx, ry) in enumerate(((88, 44), (63, 32), (38, 20))):
            self.create_oval(cx-rx, cy-ry, cx+rx, cy+ry, outline=(palette["border"], palette["accent_alt"], palette["accent"])[index], width=1.4)
        labels = (("MOVE", palette["accent"]), ("HYDRATE", palette.get("blue", palette["accent"])), ("RECOVER", palette["accent_alt"]), ("TRACK", palette.get("pink", palette["warning"])))
        for index, (label, color) in enumerate(labels):
            angle = self._phase + index * math.tau / len(labels)
            x = cx + math.cos(angle) * (72 - index * 7)
            y = cy + math.sin(angle) * (36 - index * 3)
            self.create_oval(x-6, y-6, x+6, y+6, fill=color, outline="")
            self.create_text(x, y-14, text=label, fill=palette["muted"], font=("Segoe UI", 6, "bold"))
        self.create_oval(cx-17, cy-17, cx+17, cy+17, fill=palette["panel_alt"], outline=palette["accent"], width=2)
        self.create_text(cx, cy, text="NOVA", fill=palette["text"], font=("Segoe UI", 8, "bold"))

    def _on_destroy(self, _event: tk.Event[tk.Misc]) -> None:
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except tk.TclError:
                pass
            self._after_id = None
