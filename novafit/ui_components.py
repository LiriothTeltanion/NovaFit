"""
Module: reusable Tkinter components
Purpose: Provide efficient, accessible motion and visual identity without mixing
    decorative UI code into NovaFit's data or analytics layers.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-16 | TZ: Asia/Jerusalem
Notes: Tkinter stdlib only; animated items are persisted and moved in place.
"""

from __future__ import annotations

import math
import tkinter as tk
from collections.abc import Mapping


_LANGUAGES = {"en", "es", "he"}


class _MotionCanvas(tk.Canvas):
    """Coordinate animation scheduling and widget lifecycle for Canvas scenes."""

    FRAME_MS = 50

    def _initialize_motion(self, reduced_motion: bool) -> None:
        self._reduced_motion = bool(reduced_motion)
        self._motion_active = True
        self._motion_visible = False
        self._after_id: str | None = None
        self._resize_id: str | None = None
        self.bind("<Map>", self._on_map, add="+")
        self.bind("<Unmap>", self._on_unmap, add="+")
        self.bind("<Visibility>", self._on_visibility, add="+")
        self.bind("<Destroy>", self._on_destroy, add="+")

    def set_active(self, active: bool) -> None:
        """Explicitly enable or pause motion for a page-level lifecycle.

        Parent views may call this when switching pages. Map and visibility events
        remain a safe fallback when no page controller is available.
        """
        self._motion_active = bool(active)
        if self._motion_should_run():
            self._schedule()
        else:
            self._cancel_animation()
        self._render_motion()

    def set_reduced_motion(self, reduced_motion: bool) -> None:
        """Enable a calm static composition or resume efficient motion."""
        self._reduced_motion = bool(reduced_motion)
        if self._motion_should_run():
            self._schedule()
        else:
            self._cancel_animation()
        self._render_motion()

    def _motion_should_run(self) -> bool:
        return self._motion_active and self._motion_visible and not self._reduced_motion

    def _schedule(self) -> None:
        if self._after_id is None and self._motion_should_run():
            self._after_id = self.after(self.FRAME_MS, self._run_frame)

    def _run_frame(self) -> None:
        self._after_id = None
        if not self._motion_should_run() or not self.winfo_exists():
            return
        self._advance_motion()
        self._render_motion()
        self._schedule()

    def _advance_motion(self) -> None:
        raise NotImplementedError

    def _render_motion(self) -> None:
        raise NotImplementedError

    def _queue_rebuild(self, _event: tk.Event[tk.Misc] | None = None) -> None:
        """Debounce resize redraws while keeping animation frames lightweight."""
        if self._resize_id is not None:
            try:
                self.after_cancel(self._resize_id)
            except tk.TclError:
                return
        self._resize_id = self.after(70, self._rebuild_after_resize)

    def _rebuild_after_resize(self) -> None:
        self._resize_id = None
        if self.winfo_exists():
            self._rebuild_scene()

    def _rebuild_scene(self) -> None:
        raise NotImplementedError

    def _on_map(self, _event: tk.Event[tk.Misc]) -> None:
        self._motion_visible = True
        self._schedule()

    def _on_unmap(self, _event: tk.Event[tk.Misc]) -> None:
        self._motion_visible = False
        self._cancel_animation()

    def _on_visibility(self, event: tk.Event[tk.Misc]) -> None:
        visibility_state = str(getattr(event, "state", ""))
        self._motion_visible = visibility_state not in {"2", "VisibilityFullyObscured"}
        if self._motion_should_run():
            self._schedule()
        else:
            self._cancel_animation()

    def _cancel_animation(self) -> None:
        if self._after_id is None:
            return
        try:
            self.after_cancel(self._after_id)
        except tk.TclError:
            pass
        self._after_id = None

    def _on_destroy(self, event: tk.Event[tk.Misc]) -> None:
        if event.widget is not self:
            return
        self._cancel_animation()
        if self._resize_id is not None:
            try:
                self.after_cancel(self._resize_id)
            except tk.TclError:
                pass
            self._resize_id = None


class NovaPulseCanvas(_MotionCanvas):
    """Render a compact ECG and orbit header with persistent canvas items."""

    FRAME_MS = 50

    def __init__(
        self,
        master: tk.Misc,
        palette: Mapping[str, str],
        *,
        reduced_motion: bool = False,
        language: str = "en",
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
        self._language = language if language in _LANGUAGES else "en"
        self._phase = 0.0
        self._pulse_id = 0
        self._orbit_id = 0
        self._initialize_motion(reduced_motion)
        self._rebuild_scene()

    def set_palette(self, palette: Mapping[str, str]) -> None:
        self._palette = dict(palette)
        self.configure(background=palette["bg"])
        self._rebuild_scene()

    def set_language(self, language: str) -> None:
        self._language = language if language in _LANGUAGES else "en"
        self._rebuild_scene()

    def _rebuild_scene(self) -> None:
        self.delete("all")
        palette = self._palette
        center_x, center_y = 226, 37
        points = [6, 39, 46, 39, 61, 29, 75, 51, 91, 16, 108, 45, 128, 36, 151, 39]
        self.create_line(points, fill=palette["accent"], width=2, smooth=True)
        self._pulse_id = self.create_oval(0, 0, 0, 0, fill=palette["accent_alt"], outline="")
        for radius, color in ((29, palette["border"]), (21, palette["accent_alt"])):
            self.create_oval(
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
                outline=color,
                width=1.2,
            )
        self._orbit_id = self.create_oval(0, 0, 0, 0, fill=palette["accent"], outline="")
        self.create_oval(
            center_x - 8,
            center_y - 8,
            center_x + 8,
            center_y + 8,
            fill=palette["accent_alt"],
            outline="",
        )
        copy = {
            "en": "LOCAL DATA  •  CLEAR SIGNALS",
            "es": "DATOS LOCALES  •  SEÑALES CLARAS",
            "he": "נתונים מקומיים  •  אותות ברורים",
        }[self._language]
        self.create_text(
            151,
            62,
            text=copy,
            anchor="w",
            fill=palette["muted"],
            font=("Segoe UI", 7, "bold"),
        )
        self._render_motion()

    def _advance_motion(self) -> None:
        self._phase = (self._phase + 0.075) % math.tau

    def _render_motion(self) -> None:
        if not self._pulse_id or not self.winfo_exists():
            return
        pulse = 2.5 + (math.sin(self._phase) + 1) * 1.8
        self.coords(self._pulse_id, 88 - pulse, 16 - pulse, 88 + pulse, 16 + pulse)
        orbit_x = 226 + math.cos(self._phase) * 27
        orbit_y = 37 + math.sin(self._phase) * 15
        self.coords(self._orbit_id, orbit_x - 4, orbit_y - 4, orbit_x + 4, orbit_y + 4)


class MotivationGalaxyCanvas(_MotionCanvas):
    """Render a responsive motivation galaxy without reallocating each frame."""

    FRAME_MS = 66
    _MAX_ORBITS = 29

    def __init__(
        self,
        master: tk.Misc,
        palette: Mapping[str, str],
        *,
        reduced_motion: bool = False,
        height: int = 150,
        language: str = "en",
    ) -> None:
        super().__init__(
            master,
            height=height,
            highlightthickness=0,
            bd=0,
            background=palette["panel"],
        )
        self._palette = dict(palette)
        self._language = language if language in _LANGUAGES else "en"
        self._phase = 0.0
        self._spark_level = 1
        self._orbit_ids: list[int] = []
        self._core_id = 0
        self._initialize_motion(reduced_motion)
        self.bind("<Configure>", self._queue_rebuild, add="+")
        self._rebuild_scene()

    def set_palette(self, palette: Mapping[str, str]) -> None:
        self._palette = dict(palette)
        self.configure(background=palette["panel"])
        self._rebuild_scene()

    def set_language(self, language: str) -> None:
        self._language = language if language in _LANGUAGES else "en"
        self._rebuild_scene()

    def set_spark_level(self, level: int) -> None:
        if not 0 <= level <= 3:
            raise ValueError("Spark level must be between 0 and 3.")
        self._spark_level = level
        self._render_motion()

    def celebrate(self) -> None:
        self._spark_level = 3
        self._phase = (self._phase + 0.9) % math.tau
        self._render_motion()
        self.after(1400, self._finish_celebration)

    def _finish_celebration(self) -> None:
        if self.winfo_exists():
            self.set_spark_level(1)

    def _rebuild_scene(self) -> None:
        self.delete("all")
        palette = self._palette
        width = max(420, self.winfo_width())
        height = max(120, self.winfo_height())
        for index in range(7):
            y = int((index / 7) * height)
            color = palette["panel_alt"] if index % 2 == 0 else palette["panel"]
            self.create_rectangle(0, y, width, y + height / 7 + 2, fill=color, outline="")
        colors = (palette["accent"], palette["accent_alt"], palette.get("pink", palette["warning"]))
        self._orbit_ids = [
            self.create_oval(0, 0, 0, 0, fill=colors[index % 3], outline="")
            for index in range(self._MAX_ORBITS)
        ]
        self._core_id = self.create_oval(
            0,
            0,
            0,
            0,
            fill=palette["accent_alt"],
            outline=palette["accent"],
            width=2,
        )
        copy = {
            "en": (
                "BUILD THE NEXT REPEATABLE WIN",
                "Evidence · rhythm · recovery · purpose",
                "Your data is a guide, never a judge.",
            ),
            "es": (
                "CONSTRUYE TU PRÓXIMO LOGRO REPETIBLE",
                "Evidencia · ritmo · recuperación · propósito",
                "Tus datos orientan; nunca te juzgan.",
            ),
            "he": (
                "בונים את ההצלחה הבאה שאפשר לשחזר",
                "ראיות · קצב · התאוששות · מטרה",
                "הנתונים שלך הם מצפן, לא שופט.",
            ),
        }[self._language]
        text_x = width - 28 if self._language == "he" else 28
        anchor = "e" if self._language == "he" else "w"
        text_width = max(220, int(width * 0.57))
        self.create_text(
            text_x,
            height * 0.28,
            anchor=anchor,
            width=text_width,
            text=copy[0],
            fill=palette["accent"],
            font=("Segoe UI", 10, "bold"),
        )
        self.create_text(
            text_x,
            height * 0.54,
            anchor=anchor,
            width=text_width,
            text=copy[1],
            fill=palette["text"],
            font=("Segoe UI", 16, "bold"),
        )
        self.create_text(
            text_x,
            height * 0.78,
            anchor=anchor,
            width=text_width,
            text=copy[2],
            fill=palette["muted"],
            font=("Segoe UI", 9),
        )
        self._render_motion()

    def _advance_motion(self) -> None:
        self._phase = (self._phase + 0.045) % math.tau

    def _render_motion(self) -> None:
        if not self._orbit_ids or not self.winfo_exists():
            return
        width = max(420, self.winfo_width())
        height = max(120, self.winfo_height())
        center_x = width * (0.22 if self._language == "he" else 0.78)
        center_y = height * 0.52
        orbit_count = 14 + self._spark_level * 5
        for index, item_id in enumerate(self._orbit_ids):
            if index >= orbit_count:
                self.itemconfigure(item_id, state="hidden")
                continue
            self.itemconfigure(item_id, state="normal")
            angle = self._phase * (0.35 + (index % 4) * 0.08) + index * 0.78
            radius_x = 35 + (index % 5) * 16
            radius_y = 18 + (index % 4) * 9
            x = center_x + math.cos(angle) * radius_x
            y = center_y + math.sin(angle) * radius_y
            radius = 1.5 + (index % 3) * 0.7
            self.coords(item_id, x - radius, y - radius, x + radius, y + radius)
        pulse = 14 + (math.sin(self._phase * 2) + 1) * 4
        self.coords(
            self._core_id,
            center_x - pulse,
            center_y - pulse,
            center_x + pulse,
            center_y + pulse,
        )


class FocusBreathingCanvas(_MotionCanvas):
    """Provide a calm, localized sixty-second visual focus reset."""

    FRAME_MS = 100

    def __init__(
        self,
        master: tk.Misc,
        palette: Mapping[str, str],
        *,
        reduced_motion: bool = False,
        language: str = "en",
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
        self._language = language if language in _LANGUAGES else "en"
        self._running = False
        self._phase = 0.0
        self._ticks = 0
        self._breath_id = 0
        self._label_id = 0
        self._initialize_motion(reduced_motion)
        self._rebuild_scene()

    def start(self) -> None:
        self._running = True
        self._ticks = 0
        self._phase = 0.0
        self._render_motion()
        self._schedule()

    def stop(self) -> None:
        self._running = False
        self._cancel_animation()
        self._render_motion()

    def set_palette(self, palette: Mapping[str, str]) -> None:
        self._palette = dict(palette)
        self.configure(background=palette["panel_alt"])
        self._rebuild_scene()

    def set_language(self, language: str) -> None:
        self._language = language if language in _LANGUAGES else "en"
        self._render_motion()

    def set_reduced_motion(self, reduced_motion: bool) -> None:
        super().set_reduced_motion(reduced_motion)
        if reduced_motion:
            self._running = False
            self._render_motion()

    def _motion_should_run(self) -> bool:
        return self._running and super()._motion_should_run()

    def _rebuild_scene(self) -> None:
        self.delete("all")
        palette = self._palette
        self.create_oval(20, 20, 150, 150, outline=palette["border"], width=2)
        self._breath_id = self.create_oval(
            0,
            0,
            0,
            0,
            fill=palette["accent_alt"],
            outline=palette["accent"],
            width=2,
        )
        self._label_id = self.create_text(
            85,
            85,
            fill=palette["text"],
            font=("Segoe UI", 9, "bold"),
            justify="center",
        )
        self._render_motion()

    def _advance_motion(self) -> None:
        self._phase = (self._phase + 0.08) % math.tau
        self._ticks += 1
        if self._ticks >= 600:
            self.stop()

    def _render_motion(self) -> None:
        if not self._breath_id or not self.winfo_exists():
            return
        wave = (math.sin(self._phase) + 1) / 2 if self._running else 0.35
        radius = 35 + wave * 25
        self.coords(self._breath_id, 85 - radius, 85 - radius, 85 + radius, 85 + radius)
        labels = {
            "en": ("60s RESET", "BREATHE IN", "BREATHE OUT"),
            "es": ("PAUSA 60s", "INHALA", "EXHALA"),
            "he": ("איפוס 60 שניות", "שאיפה", "נשיפה"),
        }[self._language]
        label = labels[0] if not self._running else labels[1] if math.sin(self._phase) >= 0 else labels[2]
        self.itemconfigure(self._label_id, text=label)


class UltimateHeroCanvas(_MotionCanvas):
    """Render the responsive NovaFit command-center hero with efficient motion."""

    FRAME_MS = 50

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
        self._profile_name = profile_name
        self._language = language if language in _LANGUAGES else "en"
        self._phase = 0.0
        self._wave_id = 0
        self._orbit_ids: list[int] = []
        self._core_id = 0
        self._initialize_motion(reduced_motion)
        self.bind("<Configure>", self._queue_rebuild, add="+")
        self._rebuild_scene()

    def set_palette(self, palette: Mapping[str, str]) -> None:
        self._palette = dict(palette)
        self.configure(background=palette["bg"])
        self._rebuild_scene()

    def set_profile_name(self, profile_name: str) -> None:
        self._profile_name = profile_name
        self._rebuild_scene()

    def set_language(self, language: str) -> None:
        self._language = language if language in _LANGUAGES else "en"
        self._rebuild_scene()

    def _rebuild_scene(self) -> None:
        self.delete("all")
        palette = self._palette
        width = max(620, self.winfo_width())
        height = max(170, self.winfo_height())
        self.create_rectangle(0, 0, width, height, fill=palette["panel"], outline="")
        for row in range(0, height, 28):
            self.create_line(0, row, width, row, fill=palette["border"], width=1)
        for column in range(0, width, 64):
            self.create_line(column, 0, column, height, fill=palette["border"], width=1)
        self._wave_id = self.create_line(0, 0, 1, 1, fill=palette["accent"], width=2.2, smooth=True)

        center_x = width * (0.18 if self._language == "he" else 0.82)
        center_y = height * 0.48
        orbit_colors = (palette["accent"], palette["accent_alt"], palette.get("blue", palette["accent"]))
        for index, radius in enumerate((65, 48, 31)):
            self.create_oval(
                center_x - radius,
                center_y - radius * 0.62,
                center_x + radius,
                center_y + radius * 0.62,
                outline=orbit_colors[index],
                width=1.4,
            )
        dot_colors = (palette["accent"], palette["accent_alt"], palette.get("pink", palette["warning"]))
        self._orbit_ids = [
            self.create_oval(0, 0, 0, 0, fill=dot_colors[index % 3], outline="") for index in range(18)
        ]
        self._core_id = self.create_oval(
            0,
            0,
            0,
            0,
            fill=palette["accent_alt"],
            outline=palette["accent"],
            width=2,
        )
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
                "NOVA · תובנות לבריאות יומיומית",
                "הופכים אותות יומיים למערכת יציבה ובת־קיימא",
                "פרופילים · ממשק רב־לשוני · ניתוח נתונים · המלצות · פרטיות",
                "פרופיל פעיל",
            ),
        }[self._language]
        text_x = width - 30 if self._language == "he" else 30
        anchor = "e" if self._language == "he" else "w"
        safe_width = max(260, int(width * 0.64))
        self.create_text(
            text_x,
            34,
            text=copy[0],
            anchor=anchor,
            width=safe_width,
            fill=palette["accent"],
            font=("Segoe UI", 10, "bold"),
        )
        self.create_text(
            text_x,
            72,
            text=copy[1],
            anchor=anchor,
            width=safe_width,
            fill=palette["text"],
            font=("Segoe UI", 17, "bold"),
        )
        self.create_text(
            text_x,
            110,
            text=copy[2],
            anchor=anchor,
            width=safe_width,
            fill=palette["muted"],
            font=("Segoe UI", 9),
        )
        profile_text = f"{copy[3]}  •  {self._profile_name}"
        self.create_text(
            center_x,
            height - 16,
            text=profile_text,
            fill=palette["muted"],
            font=("Segoe UI", 8, "bold"),
        )
        self._render_motion()

    def _advance_motion(self) -> None:
        self._phase = (self._phase + 0.035) % math.tau

    def _render_motion(self) -> None:
        if not self._wave_id or not self._orbit_ids or not self.winfo_exists():
            return
        width = max(620, self.winfo_width())
        height = max(170, self.winfo_height())
        points: list[float] = []
        for x in range(-20, width + 20, 11):
            wave = math.sin((x / 85) + self._phase * 2.2) * 14
            pulse = math.sin((x / 31) - self._phase * 1.3) * 4
            points.extend((x, height * 0.70 + wave + pulse))
        self.coords(self._wave_id, *points)
        center_x = width * (0.18 if self._language == "he" else 0.82)
        center_y = height * 0.48
        for index, item_id in enumerate(self._orbit_ids):
            angle = self._phase * (0.6 + (index % 3) * 0.12) + index * 0.57
            radius_x = 32 + (index % 5) * 10
            radius_y = 19 + (index % 4) * 7
            x = center_x + math.cos(angle) * radius_x
            y = center_y + math.sin(angle) * radius_y
            dot = 1.5 + (index % 3)
            self.coords(item_id, x - dot, y - dot, x + dot, y + dot)
        core = 11 + (math.sin(self._phase * 2) + 1) * 3
        self.coords(self._core_id, center_x - core, center_y - core, center_x + core, center_y + core)


class ActivityOrbitCanvas(_MotionCanvas):
    """Render a localized activity orbit with persistent dots and labels."""

    FRAME_MS = 66

    def __init__(
        self,
        master: tk.Misc,
        palette: Mapping[str, str],
        *,
        reduced_motion: bool = False,
        language: str = "en",
    ) -> None:
        super().__init__(
            master,
            width=240,
            height=150,
            highlightthickness=0,
            bd=0,
            background=palette["panel"],
        )
        self._palette = dict(palette)
        self._language = language if language in _LANGUAGES else "en"
        self._phase = 0.0
        self._dot_ids: list[int] = []
        self._label_ids: list[int] = []
        self._initialize_motion(reduced_motion)
        self._rebuild_scene()

    def set_palette(self, palette: Mapping[str, str]) -> None:
        self._palette = dict(palette)
        self.configure(background=palette["panel"])
        self._rebuild_scene()

    def set_language(self, language: str) -> None:
        self._language = language if language in _LANGUAGES else "en"
        self._rebuild_scene()

    def _rebuild_scene(self) -> None:
        self.delete("all")
        palette = self._palette
        cx, cy = 120, 75
        for index, (rx, ry) in enumerate(((88, 44), (63, 32), (38, 20))):
            self.create_oval(
                cx - rx,
                cy - ry,
                cx + rx,
                cy + ry,
                outline=(palette["border"], palette["accent_alt"], palette["accent"])[index],
                width=1.4,
            )
        colors = (
            palette["accent"],
            palette.get("blue", palette["accent"]),
            palette["accent_alt"],
            palette.get("pink", palette["warning"]),
        )
        labels = {
            "en": ("MOVE", "HYDRATE", "RECOVER", "TRACK"),
            "es": ("MOVER", "HIDRATAR", "RECUPERAR", "REGISTRAR"),
            "he": ("תנועה", "שתייה", "התאוששות", "מעקב"),
        }[self._language]
        self._dot_ids = [self.create_oval(0, 0, 0, 0, fill=color, outline="") for color in colors]
        self._label_ids = [
            self.create_text(0, 0, text=label, fill=palette["muted"], font=("Segoe UI", 7, "bold"))
            for label in labels
        ]
        self.create_oval(
            cx - 17,
            cy - 17,
            cx + 17,
            cy + 17,
            fill=palette["panel_alt"],
            outline=palette["accent"],
            width=2,
        )
        self.create_text(cx, cy, text="NOVA", fill=palette["text"], font=("Segoe UI", 8, "bold"))
        self._render_motion()

    def _advance_motion(self) -> None:
        self._phase = (self._phase + 0.05) % math.tau

    def _render_motion(self) -> None:
        if not self._dot_ids or not self.winfo_exists():
            return
        cx, cy = 120, 75
        for index, (dot_id, label_id) in enumerate(zip(self._dot_ids, self._label_ids)):
            angle = self._phase + index * math.tau / len(self._dot_ids)
            x = cx + math.cos(angle) * (72 - index * 7)
            y = cy + math.sin(angle) * (36 - index * 3)
            self.coords(dot_id, x - 6, y - 6, x + 6, y + 6)
            self.coords(label_id, x, y - 15)
