"""
Module: motivation center panel
Purpose: Present grounded encouragement, milestones, personal purpose, and a
    short focus reset inside a responsive, scrollable NovaFit workspace.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Tkinter/ttk only; messages are non-medical and derived from local data.
"""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable, Mapping
from tkinter import ttk

from .analytics import DashboardStats
from .config import AppSettings
from .i18n import direction_for, normalize_language, tr
from .models import HealthEntry
from .motivation import MotivationSnapshot, build_motivation_snapshot
from .ui_components import FocusBreathingCanvas, MotivationGalaxyCanvas


class MotivationCenterPanel(ttk.Frame):
    """Render the complete, scrollable NovaFit Motivation Center.

    Args:
        master: Parent Tkinter widget.
        settings: Current application settings.
        palette_provider: Callable returning the active UI palette.
        save_callback: Callback receiving updated personal motivation fields.
        status_callback: Callback for friendly status messages.

    Example:
        >>> panel = MotivationCenterPanel(root, settings, palette, save, status)  # doctest: +SKIP
    """

    def __init__(
        self,
        master: tk.Misc,
        settings: AppSettings,
        palette_provider: Callable[[], Mapping[str, str]],
        save_callback: Callable[[str, str, str], None],
        status_callback: Callable[[str], None],
    ) -> None:
        super().__init__(master, style="Panel.TFrame", padding=0)
        self.settings = settings
        self._palette_provider = palette_provider
        self._save_callback = save_callback
        self._status_callback = status_callback
        self._entries: list[HealthEntry] = []
        self._stats = DashboardStats.empty()
        self._snapshot = build_motivation_snapshot([], settings)
        self._spark_offset = 0
        self.language = normalize_language(settings.language)
        self._rtl = direction_for(self.language) == "rtl"

        self.headline_var = tk.StringVar()
        self.message_var = tk.StringVar()
        self.spark_var = tk.StringVar()
        self.action_var = tk.StringVar()
        self.challenge_var = tk.StringVar()
        self.milestone_var = tk.StringVar()
        self.personal_why_var = tk.StringVar(value=settings.personal_why)
        self.weekly_focus_var = tk.StringVar(value=settings.weekly_focus)
        self.reward_note_var = tk.StringVar(value=settings.reward_note)
        self.metric_vars = {
            "momentum": tk.StringVar(value="0/100"),
            "streak": tk.StringVar(value=tr(self.language, "day_count", count=0)),
            "perfect": tk.StringVar(value=tr(self.language, "day_count", count=0)),
            "earned": tk.StringVar(value="0/6"),
        }
        self._build_scroll_shell()
        self._build_content()
        self.refresh([], DashboardStats.empty(), settings)

    def _build_scroll_shell(self) -> None:
        """Create an accessible vertical scroll container.

        Returns:
            None.

        Example:
            >>> panel._build_scroll_shell()  # doctest: +SKIP
        """
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        palette = self._palette_provider()
        self.scroll_canvas = tk.Canvas(
            self,
            highlightthickness=0,
            bd=0,
            background=palette["bg"],
        )
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.scroll_canvas.yview)
        self.scroll_canvas.configure(yscrollcommand=scrollbar.set)
        self.scroll_canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.content = ttk.Frame(self.scroll_canvas, style="Panel.TFrame", padding=(4, 4, 10, 14))
        self._window_id = self.scroll_canvas.create_window(
            (0, 0),
            window=self.content,
            anchor="ne" if self._rtl else "nw",
        )
        self.content.bind("<Configure>", self._update_scroll_region, add="+")
        self.scroll_canvas.bind("<Configure>", self._resize_content, add="+")
        self.scroll_canvas.bind(
            "<Enter>",
            lambda _event: self.scroll_canvas.bind_all("<MouseWheel>", self._on_mousewheel),
            add="+",
        )
        self.scroll_canvas.bind(
            "<Leave>", lambda _event: self.scroll_canvas.unbind_all("<MouseWheel>"), add="+"
        )

    def _build_content(self) -> None:
        """Build Motivation Center cards inside the scroll container.

        Returns:
            None.

        Example:
            >>> panel._build_content()  # doctest: +SKIP
        """
        self.content.columnconfigure(0, weight=1)
        anchor = "e" if self._rtl else "w"
        justify = "right" if self._rtl else "left"
        start_side = "right" if self._rtl else "left"
        palette = self._palette_provider()
        self.galaxy = MotivationGalaxyCanvas(
            self.content,
            palette,
            reduced_motion=self.settings.reduce_motion,
            height=145,
            language=self.language,
        )
        self.galaxy.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        hero = ttk.Frame(self.content, style="Card.TFrame", padding=18)
        hero.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        hero.columnconfigure(0, weight=1)
        ttk.Label(
            hero,
            textvariable=self.headline_var,
            style="CardValue.TLabel",
            font=("Segoe UI", 18, "bold"),
            anchor=anchor,
            justify=justify,
        ).grid(row=0, column=0, sticky="ew")
        ttk.Label(
            hero,
            textvariable=self.message_var,
            style="CardTitle.TLabel",
            wraplength=900,
            justify=justify,
            anchor=anchor,
        ).grid(row=1, column=0, sticky="ew", pady=(8, 8))
        spark_row = ttk.Frame(hero, style="Card.TFrame")
        spark_row.grid(row=2, column=0, sticky="ew")
        spark_column = 2 if self._rtl else 0
        celebrate_column = 0 if self._rtl else 2
        spark_row.columnconfigure(spark_column, weight=1)
        ttk.Label(
            spark_row,
            textvariable=self.spark_var,
            style="Panel.TLabel",
            wraplength=780,
            justify=justify,
            anchor=anchor,
        ).grid(row=0, column=spark_column, sticky="ew")
        ttk.Button(
            spark_row,
            text=tr(self.language, "motivation_new_spark"),
            command=self._new_spark,
        ).grid(row=0, column=1, padx=8)
        ttk.Button(
            spark_row,
            text=tr(self.language, "motivation_celebrate"),
            style="Accent.TButton",
            command=self._celebrate,
        ).grid(row=0, column=celebrate_column)

        body = ttk.Frame(self.content, style="Panel.TFrame")
        body.grid(row=2, column=0, sticky="ew")
        main_column = 1 if self._rtl else 0
        purpose_column = 0 if self._rtl else 1
        body.columnconfigure(main_column, weight=3)
        body.columnconfigure(purpose_column, weight=2)
        left = ttk.Frame(body, style="Panel.TFrame")
        right = ttk.Frame(body, style="Panel.TFrame")
        left.grid(row=0, column=main_column, sticky="nsew", padx=6)
        right.grid(row=0, column=purpose_column, sticky="nsew", padx=6)

        cards = ttk.Frame(left, style="Panel.TFrame")
        cards.pack(fill="x", pady=(0, 10))
        for index, (key, title) in enumerate(
            (
                ("momentum", "motivation_momentum"),
                ("streak", "motivation_current_streak"),
                ("perfect", "motivation_combined_days"),
                ("earned", "motivation_badges_earned"),
            )
        ):
            column = 3 - index if self._rtl else index
            cards.columnconfigure(column, weight=1)
            card = ttk.Frame(cards, style="Card.TFrame", padding=14)
            card.grid(row=0, column=column, sticky="nsew", padx=3)
            ttk.Label(card, text=tr(self.language, title).upper(), style="CardTitle.TLabel").pack(
                anchor=anchor
            )
            ttk.Label(card, textvariable=self.metric_vars[key], style="CardValue.TLabel").pack(
                anchor=anchor, pady=(6, 0)
            )

        mission = ttk.Frame(left, style="Card.TFrame", padding=18)
        mission.pack(fill="x", pady=(0, 10))
        ttk.Label(
            mission, text=tr(self.language, "motivation_next_action").upper(), style="CardTitle.TLabel"
        ).pack(anchor=anchor)
        ttk.Label(
            mission, textvariable=self.action_var, style="Panel.TLabel", wraplength=720, justify=justify
        ).pack(anchor=anchor, pady=(6, 12))
        ttk.Label(
            mission, text=tr(self.language, "motivation_week_challenge").upper(), style="CardTitle.TLabel"
        ).pack(anchor=anchor)
        ttk.Label(
            mission, textvariable=self.challenge_var, style="Panel.TLabel", wraplength=720, justify=justify
        ).pack(anchor=anchor, pady=(6, 12))
        ttk.Label(
            mission, text=tr(self.language, "motivation_next_milestone").upper(), style="CardTitle.TLabel"
        ).pack(anchor=anchor)
        ttk.Label(mission, textvariable=self.milestone_var, style="Panel.TLabel", justify=justify).pack(
            anchor=anchor, pady=(6, 5)
        )
        self.milestone_progress = ttk.Progressbar(mission, maximum=100)
        self.milestone_progress.pack(fill="x")

        badge_shell = ttk.Frame(left, style="Card.TFrame", padding=18)
        badge_shell.pack(fill="x")
        ttk.Label(
            badge_shell, text=tr(self.language, "motivation_constellation").upper(), style="CardValue.TLabel"
        ).pack(anchor=anchor, pady=(0, 10))
        self.badge_frame = ttk.Frame(badge_shell, style="Card.TFrame")
        self.badge_frame.pack(fill="x")

        purpose = ttk.Frame(right, style="Card.TFrame", padding=18)
        purpose.pack(fill="x", pady=(0, 10))
        ttk.Label(
            purpose, text=tr(self.language, "motivation_purpose_board").upper(), style="CardValue.TLabel"
        ).pack(anchor=anchor)
        ttk.Label(
            purpose,
            text=tr(self.language, "motivation_purpose_hint"),
            style="CardTitle.TLabel",
            justify=justify,
        ).pack(anchor=anchor, pady=(4, 10))
        for label, variable in (
            (tr(self.language, "motivation_personal_why"), self.personal_why_var),
            (tr(self.language, "motivation_weekly_focus"), self.weekly_focus_var),
            (tr(self.language, "motivation_reward_note"), self.reward_note_var),
        ):
            ttk.Label(purpose, text=label, style="CardTitle.TLabel").pack(anchor=anchor, pady=(7, 3))
            ttk.Entry(purpose, textvariable=variable, justify=justify).pack(fill="x")
        ttk.Button(
            purpose,
            text=tr(self.language, "motivation_save_purpose"),
            style="Accent.TButton",
            command=self._save_purpose,
        ).pack(fill="x", pady=(14, 0))

        reset_card = ttk.Frame(right, style="Card.TFrame", padding=18)
        reset_card.pack(fill="x")
        ttk.Label(
            reset_card, text=tr(self.language, "motivation_focus_reset").upper(), style="CardValue.TLabel"
        ).pack(anchor=anchor)
        ttk.Label(
            reset_card,
            text=tr(self.language, "motivation_focus_hint"),
            style="CardTitle.TLabel",
            wraplength=360,
            justify=justify,
        ).pack(anchor=anchor, pady=(5, 10))
        self.focus_canvas = FocusBreathingCanvas(
            reset_card,
            palette,
            reduced_motion=self.settings.reduce_motion,
            language=self.language,
        )
        self.focus_canvas.pack(pady=(4, 10))
        controls = ttk.Frame(reset_card, style="Card.TFrame")
        controls.pack(fill="x")
        ttk.Button(
            controls, text=tr(self.language, "motivation_start_reset"), command=self.focus_canvas.start
        ).pack(side=start_side, expand=True, fill="x", padx=4)
        ttk.Button(controls, text=tr(self.language, "stop"), command=self.focus_canvas.stop).pack(
            side=start_side, expand=True, fill="x", padx=4
        )

    def refresh(
        self,
        entries: list[HealthEntry],
        stats: DashboardStats,
        settings: AppSettings,
    ) -> None:
        """Refresh motivation copy and badge progress from local records.

        Args:
            entries: Current local records.
            stats: Precomputed dashboard metrics.
            settings: Current settings and purpose-board values.

        Returns:
            None.

        Example:
            >>> panel.refresh([], DashboardStats.empty(), AppSettings())  # doctest: +SKIP
        """
        self._entries = list(entries)
        self._stats = stats
        self.settings = settings
        self.language = normalize_language(settings.language)
        self._rtl = direction_for(self.language) == "rtl"
        self.galaxy.set_language(self.language)
        self.focus_canvas.set_language(self.language)
        self._snapshot = build_motivation_snapshot(
            self._entries,
            settings,
            spark_offset=self._spark_offset,
        )
        self.headline_var.set(self._snapshot.headline)
        self.message_var.set(self._snapshot.message)
        self.spark_var.set(f"💙 {self._snapshot.daily_spark}")
        self.action_var.set(self._snapshot.micro_action)
        self.challenge_var.set(settings.weekly_focus.strip() or self._snapshot.weekly_challenge)
        self.milestone_var.set(self._snapshot.next_milestone)
        self.milestone_progress["value"] = self._snapshot.milestone_progress_pct
        self.metric_vars["momentum"].set(f"{stats.consistency_score}/100")
        self.metric_vars["streak"].set(tr(self.language, "day_count", count=stats.current_streak_days))
        self.metric_vars["perfect"].set(tr(self.language, "day_count", count=stats.perfect_goal_days))
        earned = sum(item.earned for item in self._snapshot.achievements)
        self.metric_vars["earned"].set(f"{earned}/{len(self._snapshot.achievements)}")
        self.personal_why_var.set(settings.personal_why)
        self.weekly_focus_var.set(settings.weekly_focus)
        self.reward_note_var.set(settings.reward_note)
        self.galaxy.set_spark_level(self._snapshot.celebration_level)
        self._render_badges(self._snapshot)
        self.after_idle(self._update_scroll_region)

    def apply_theme(self) -> None:
        """Apply the current palette and motion preference.

        Returns:
            None.

        Example:
            >>> panel.apply_theme()  # doctest: +SKIP
        """
        palette = self._palette_provider()
        self.scroll_canvas.configure(background=palette["bg"])
        self.galaxy.set_palette(palette)
        self.galaxy.set_reduced_motion(self.settings.reduce_motion)
        self.galaxy.set_language(self.language)
        self.focus_canvas.set_palette(palette)
        self.focus_canvas.set_reduced_motion(self.settings.reduce_motion)
        self.focus_canvas.set_language(self.language)

    def _render_badges(self, snapshot: MotivationSnapshot) -> None:
        anchor = "e" if self._rtl else "w"
        justify = "right" if self._rtl else "left"
        for child in self.badge_frame.winfo_children():
            child.destroy()
        for index, badge in enumerate(snapshot.achievements):
            column = 2 - (index % 3) if self._rtl else index % 3
            self.badge_frame.columnconfigure(column, weight=1)
            card = ttk.Frame(self.badge_frame, style="Card.TFrame", padding=10)
            card.grid(row=index // 3, column=column, sticky="nsew", padx=4, pady=4)
            state = tr(self.language, "earned").upper() if badge.earned else f"{badge.progress_pct}%"
            ttk.Label(
                card,
                text=f"{badge.icon}  {badge.title}",
                style="Panel.TLabel",
                font=("Segoe UI", 9, "bold"),
                justify=justify,
            ).pack(anchor=anchor)
            ttk.Label(
                card,
                text=badge.description,
                style="CardTitle.TLabel",
                wraplength=190,
                justify=justify,
            ).pack(anchor=anchor, pady=(5, 7))
            ttk.Label(card, text=state, style="CardValue.TLabel").pack(anchor=anchor)

    def _new_spark(self) -> None:
        self._spark_offset += 1
        self.refresh(self._entries, self._stats, self.settings)
        self._status_callback(tr(self.language, "motivation_new_spark_ready"))

    def _celebrate(self) -> None:
        self.galaxy.celebrate()
        self._status_callback(tr(self.language, "motivation_celebrate_status"))

    def _save_purpose(self) -> None:
        self._save_callback(
            self.personal_why_var.get().strip(),
            self.weekly_focus_var.get().strip(),
            self.reward_note_var.get().strip(),
        )

    def _update_scroll_region(self, _event: tk.Event[tk.Misc] | None = None) -> None:
        self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))

    def _resize_content(self, event: tk.Event[tk.Misc]) -> None:
        self.scroll_canvas.itemconfigure(self._window_id, width=event.width)
        self.scroll_canvas.coords(self._window_id, event.width if self._rtl else 0, 0)

    def _on_mousewheel(self, event: tk.Event[tk.Misc]) -> None:
        delta = -1 if event.delta > 0 else 1
        self.scroll_canvas.yview_scroll(delta * 3, "units")
