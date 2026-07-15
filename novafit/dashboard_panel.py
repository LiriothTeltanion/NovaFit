"""
Module: analytics dashboard panel
Purpose: Encapsulate NovaFit's advanced chart controls, metric cards, evidence-based
    insight sidebar, and Matplotlib embedding in a reusable ttk frame.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Matplotlib is optional; comments in ENGLISH; emojis sparingly.
"""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk
from typing import Any, Callable, Mapping

from .analytics import DashboardStats
from .charts import CHART_VIEWS, create_dashboard_figure, normalize_chart_view, save_dashboard_chart
from .config import AppSettings
from .i18n import direction_for, normalize_language, tr
from .models import HealthEntry

PaletteProvider = Callable[[], Mapping[str, str]]
StatusCallback = Callable[[str], None]
ErrorCallback = Callable[[str, Exception], None]


class DashboardPanel(ttk.Frame):
    """Present NovaFit analytics as an interactive desktop command center.

    Args:
        master: Parent ttk widget.
        settings: Current application preferences.
        palette_provider: Callable returning the active UI palette.
        status_callback: Callable for user-facing status updates.
        error_callback: Callable for recoverable display errors.

    Example:
        >>> panel = DashboardPanel(parent, settings, palette, status, errors)  # doctest: +SKIP
    """

    def __init__(
        self,
        master: tk.Misc,
        settings: AppSettings,
        palette_provider: PaletteProvider,
        status_callback: StatusCallback,
        error_callback: ErrorCallback,
    ) -> None:
        super().__init__(master, style="Panel.TFrame", padding=12)
        self.settings = settings
        self._palette_provider = palette_provider
        self._status_callback = status_callback
        self._error_callback = error_callback
        self._entries: list[HealthEntry] = []
        self._stats = DashboardStats.empty()
        self._chart_canvas: Any = None
        self._toolbar: Any = None
        self._chart_image: Any = None
        self.language = normalize_language(settings.language)
        self._rtl = direction_for(self.language) == "rtl"
        self._chart_labels = {key: tr(self.language, f"chart_view_{key}") for key in CHART_VIEWS}

        self.range_var = tk.StringVar(value=str(settings.chart_days))
        self.view_var = tk.StringVar(
            value=self._chart_labels.get(settings.chart_view, self._chart_labels["command_center"])
        )
        self.metric_vars = {
            key: tk.StringVar(value="—")
            for key in (
                "momentum",
                "tracked",
                "coverage",
                "total_steps",
                "average_steps",
                "average_water",
                "combined_goals",
                "streak",
                "best_day",
                "trend",
            )
        }
        self.step_goal_var = tk.StringVar(value=f"{tr(self.language, 'step_goal')} —")
        self.water_goal_var = tk.StringVar(value=f"{tr(self.language, 'water_goal')} —")
        self.both_goal_var = tk.StringVar(value=f"{tr(self.language, 'metric_both_goals')} —")
        self.latest_var = tk.StringVar(value=tr(self.language, "no_latest_record"))
        self._build()

    def _build(self) -> None:
        start_side = "right" if self._rtl else "left"
        end_side = "left" if self._rtl else "right"
        anchor = "e" if self._rtl else "w"
        justify = "right" if self._rtl else "left"
        controls = ttk.Frame(self, style="Panel.TFrame")
        controls.pack(fill="x", pady=(0, 10))
        ttk.Label(controls, text=tr(self.language, "analytics_view"), style="Panel.TLabel").pack(
            side=start_side
        )
        view = ttk.Combobox(
            controls,
            textvariable=self.view_var,
            values=tuple(self._chart_labels.values()),
            state="readonly",
            width=18,
            justify="right" if self._rtl else "left",
        )
        view.pack(side=start_side, padx=7)
        ttk.Label(controls, text=tr(self.language, "calendar_range"), style="Panel.TLabel").pack(
            side=start_side, padx=(9, 0)
        )
        range_box = ttk.Combobox(
            controls,
            textvariable=self.range_var,
            values=("7", "14", "30", "60", "90", "180", "365"),
            state="readonly",
            width=7,
            justify="right" if self._rtl else "left",
        )
        range_box.pack(side=start_side, padx=7)
        ttk.Label(controls, text=tr(self.language, "days"), style="Panel.TLabel").pack(side=start_side)
        ttk.Button(
            controls,
            text=tr(self.language, "refresh_charts"),
            style="Accent.TButton",
            command=self.refresh_chart,
        ).pack(side=end_side)
        ttk.Button(controls, text=tr(self.language, "export_png"), command=self.export_png).pack(
            side=end_side, padx=8
        )
        view.bind("<<ComboboxSelected>>", lambda _event: self.refresh_chart())
        range_box.bind("<<ComboboxSelected>>", lambda _event: self.refresh_chart())

        cards = ttk.Frame(self, style="Panel.TFrame")
        cards.pack(fill="x", pady=(0, 10))
        for column in range(5):
            cards.columnconfigure(column, weight=1)
        specs = [
            ("metric_consistency", "momentum"),
            ("metric_tracked_days", "tracked"),
            ("metric_coverage_30", "coverage"),
            ("metric_total_steps", "total_steps"),
            ("metric_average_steps", "average_steps"),
            ("metric_average_water", "average_water"),
            ("metric_both_goals", "combined_goals"),
            ("metric_current_longest", "streak"),
            ("metric_best_day", "best_day"),
            ("metric_recent_trend", "trend"),
        ]
        for index, (label_key, key) in enumerate(specs):
            column = 4 - (index % 5) if self._rtl else index % 5
            card = ttk.Frame(cards, style="Card.TFrame", padding=(13, 10))
            card.grid(row=index // 5, column=column, sticky="nsew", padx=4, pady=4)
            ttk.Label(card, text=tr(self.language, label_key).upper(), style="CardTitle.TLabel").pack(
                anchor=anchor
            )
            ttk.Label(card, textvariable=self.metric_vars[key], style="CardValue.TLabel").pack(
                anchor=anchor, pady=(4, 0)
            )

        self.content_pane = ttk.Panedwindow(self, orient="horizontal")
        self.content_pane.pack(fill="both", expand=True)
        # Both panes must be direct children of the Panedwindow. Keeping the
        # analytics canvas wide preserves the exported dashboard's 1.74:1
        # visual ratio while the signal rail remains readable beside it.
        chart_shell = ttk.Frame(self.content_pane, style="Card.TFrame", padding=6, width=1040)
        insights_shell = ttk.Frame(self.content_pane, style="Card.TFrame", padding=15, width=270)
        self.content_pane.add(chart_shell, weight=5)
        self.content_pane.add(insights_shell, weight=1)

        self.chart_host = ttk.Frame(chart_shell, style="Card.TFrame")
        self.chart_host.pack(fill="both", expand=True)
        self.toolbar_host = ttk.Frame(chart_shell, style="Card.TFrame")
        self.toolbar_host.pack(fill="x")

        ttk.Label(insights_shell, text=tr(self.language, "signal_summary"), style="CardValue.TLabel").pack(
            anchor=anchor
        )
        ttk.Label(
            insights_shell,
            text=tr(self.language, "signal_summary_body"),
            style="CardTitle.TLabel",
            wraplength=225,
            justify=justify,
        ).pack(anchor=anchor, pady=(5, 12))
        ttk.Label(
            insights_shell,
            textvariable=self.latest_var,
            style="Panel.TLabel",
            wraplength=225,
            justify=justify,
        ).pack(anchor=anchor)

        self.insight_text = tk.Text(
            insights_shell,
            height=11,
            width=34,
            wrap="word",
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            padx=2,
            pady=10,
            font=("Segoe UI", 9),
            state="disabled",
        )
        self.insight_text.pack(fill="both", expand=True)

        ttk.Separator(insights_shell).pack(fill="x", pady=8)
        for variable in (self.step_goal_var, self.water_goal_var, self.both_goal_var):
            ttk.Label(insights_shell, textvariable=variable, style="CardTitle.TLabel").pack(
                anchor=anchor, pady=2
            )
        self.step_progress = ttk.Progressbar(insights_shell, maximum=100)
        self.step_progress.pack(fill="x", pady=(2, 7))
        self.water_progress = ttk.Progressbar(insights_shell, maximum=100)
        self.water_progress.pack(fill="x", pady=(2, 7))
        self.both_progress = ttk.Progressbar(insights_shell, maximum=100)
        self.both_progress.pack(fill="x", pady=(2, 0))
        self._apply_text_palette()

    def finalize_layout(self) -> None:
        """Set a stable analytics/insight split after Tk has mapped the window.

        Returns:
            None.

        Example:
            >>> panel.finalize_layout()  # doctest: +SKIP
        """
        self.update_idletasks()
        width = self.content_pane.winfo_width()
        if width > 400:
            self.content_pane.sashpos(0, int(width * 0.82))
            self.update_idletasks()
        self.refresh_chart()

    def refresh(
        self,
        entries: list[HealthEntry],
        stats: DashboardStats,
        settings: AppSettings,
    ) -> None:
        """Refresh cards, progress meters, insights, and the active chart.

        Args:
            entries: Current database records.
            stats: Precomputed dashboard values.
            settings: Current preferences.

        Returns:
            None.

        Example:
            >>> panel.refresh([], DashboardStats.empty(), AppSettings())  # doctest: +SKIP
        """
        self._entries = list(entries)
        self._stats = stats
        self.settings = settings
        self.range_var.set(str(settings.chart_days))
        self.view_var.set(self._chart_labels.get(settings.chart_view, self._chart_labels["command_center"]))
        self._update_metrics()
        self._update_insights()
        self._apply_text_palette()
        self.refresh_chart()

    def refresh_chart(self) -> None:
        """Recreate the selected chart view from the current local records.

        Returns:
            None.

        Example:
            >>> panel.refresh_chart()  # doctest: +SKIP
        """
        try:
            from io import BytesIO

            from PIL import Image, ImageTk

            days = int(self.range_var.get())
            view = self._selected_view_id()
            self.chart_host.update_idletasks()
            pane_width = max(1, self.content_pane.winfo_width())
            pane_height = max(1, self.content_pane.winfo_height())
            host_width = max(720, self.chart_host.winfo_width(), int(pane_width * 0.80))
            host_height = max(410, self.chart_host.winfo_height(), pane_height - 48)

            # Render through the non-interactive Agg path and display one exact
            # raster preview. This stays crisp, theme-aware, and avoids TkAgg
            # buffer tiling on high-DPI Windows configurations.
            figure = create_dashboard_figure(
                self._entries,
                self.settings,
                days=days,
                theme=self.settings.theme,
                view=view,
                figure_size=(host_width / 100.0, host_height / 100.0),
            )
            buffer = BytesIO()
            figure.savefig(
                buffer,
                format="png",
                dpi=100,
                facecolor=figure.get_facecolor(),
                edgecolor="none",
            )
            buffer.seek(0)
            image = Image.open(buffer).convert("RGB")
            if image.size != (host_width, host_height):
                image = image.resize((host_width, host_height), Image.Resampling.LANCZOS)

            for child in self.chart_host.winfo_children():
                child.destroy()
            for child in self.toolbar_host.winfo_children():
                child.destroy()

            self._chart_image = ImageTk.PhotoImage(image)
            preview = tk.Label(
                self.chart_host,
                image=self._chart_image,
                background=self._palette_provider()["bg"],
                borderwidth=0,
                highlightthickness=0,
            )
            preview.pack(fill="both", expand=True)
            ttk.Label(
                self.toolbar_host,
                text=tr(self.language, "local_chart_preview"),
                style="CardTitle.TLabel",
                anchor="center",
            ).pack(fill="x", pady=(4, 0))
            figure.clear()
            buffer.close()
        except (ImportError, ValueError, tk.TclError) as exc:
            self._error_callback(tr(self.language, "dashboard_chart_error"), exc)

    def export_png(self) -> None:
        """Export the selected view and range as a high-resolution PNG.

        Returns:
            None.

        Example:
            >>> panel.export_png()  # doctest: +SKIP
        """
        destination = filedialog.asksaveasfilename(
            title=tr(self.language, "save_dashboard_title"),
            defaultextension=".png",
            filetypes=[(tr(self.language, "png_image"), "*.png")],
            initialfile=f"novafit-{self._selected_view_id()}-{self.range_var.get()}d.png",
        )
        if not destination:
            return
        try:
            path = save_dashboard_chart(
                self._entries,
                self.settings,
                Path(destination),
                days=int(self.range_var.get()),
                theme=self.settings.theme,
                view=self._selected_view_id(),
            )
            self._status_callback(tr(self.language, "dashboard_saved", path=path))
        except (ImportError, OSError, ValueError) as exc:
            self._error_callback(tr(self.language, "export_chart_error"), exc)

    def apply_theme(self) -> None:
        """Refresh embedded chart and sidebar colors after a theme change.

        Returns:
            None.

        Example:
            >>> panel.apply_theme()  # doctest: +SKIP
        """
        self._apply_text_palette()
        self.refresh_chart()

    def selected_preferences(self) -> tuple[int, str]:
        """Return the selected chart range and view for persistence.

        Returns:
            ``(days, view)`` tuple.

        Example:
            >>> panel.selected_preferences()[0] >= 7  # doctest: +SKIP
            True
        """
        return int(self.range_var.get()), self._selected_view_id()

    def _selected_view_id(self) -> str:
        """Resolve a localized chart label to its stable storage identifier."""
        selected = self.view_var.get()
        for key, label in self._chart_labels.items():
            if selected == label:
                return key
        return normalize_chart_view(selected)

    def _update_metrics(self) -> None:
        stats = self._stats
        trend = (
            tr(self.language, "need_14_records")
            if stats.recent_step_change_pct is None
            else f"{stats.recent_step_change_pct:+.1f}%"
        )
        calories = (
            "—"
            if stats.average_calories is None
            else f"{stats.average_calories:,} {tr(self.language, 'kcal')}"
        )
        self.metric_vars["momentum"].set(f"{stats.consistency_score}/100")
        self.metric_vars["tracked"].set(str(stats.entry_count))
        self.metric_vars["coverage"].set(f"{stats.tracking_coverage_pct:.0f}%")
        self.metric_vars["total_steps"].set(f"{stats.total_steps:,}")
        self.metric_vars["average_steps"].set(f"{stats.average_steps:,}")
        self.metric_vars["average_water"].set(f"{stats.average_water_l:.2f} L")
        self.metric_vars["combined_goals"].set(tr(self.language, "day_count", count=stats.perfect_goal_days))
        self.metric_vars["streak"].set(f"{stats.current_streak_days} / {stats.longest_tracking_streak_days}")
        self.metric_vars["best_day"].set(
            "—" if stats.best_date is None else f"{stats.best_steps:,} · {stats.best_date[5:]}"
        )
        self.metric_vars["trend"].set(trend)
        latest = max(self._entries, key=lambda item: item.entry_date) if self._entries else None
        latest_line = (
            tr(self.language, "no_latest_record")
            if latest is None
            else tr(
                self.language,
                "latest_record",
                date=latest.entry_date,
                steps=f"{latest.steps:,}",
                water=f"{latest.water_l:.2f}",
            )
        )
        mood = (
            self._localized_option("mood", stats.dominant_mood)
            if stats.dominant_mood
            else tr(self.language, "not_recorded")
        )
        self.latest_var.set(
            "\n".join(
                (
                    latest_line,
                    tr(self.language, "average_calories", value=calories),
                    tr(self.language, "dominant_mood", value=mood),
                )
            )
        )

        self.step_progress["value"] = stats.step_goal_rate_pct
        self.water_progress["value"] = stats.water_goal_rate_pct
        self.both_progress["value"] = stats.perfect_goal_rate_pct
        self.step_goal_var.set(
            tr(
                self.language,
                "goal_rate",
                label=tr(self.language, "step_goal"),
                rate=f"{stats.step_goal_rate_pct:.0f}",
            )
        )
        self.water_goal_var.set(
            tr(
                self.language,
                "goal_rate",
                label=tr(self.language, "water_goal"),
                rate=f"{stats.water_goal_rate_pct:.0f}",
            )
        )
        self.both_goal_var.set(
            tr(
                self.language,
                "goal_rate",
                label=tr(self.language, "metric_both_goals"),
                rate=f"{stats.perfect_goal_rate_pct:.0f}",
            )
        )

    def _update_insights(self) -> None:
        lines = self._localized_insight_lines()
        self.insight_text.configure(state="normal")
        self.insight_text.delete("1.0", "end")
        self.insight_text.tag_configure("body", justify="right" if self._rtl else "left")
        for index, line in enumerate(lines, start=1):
            self.insight_text.insert("end", f"{index}. {line}\n\n", "body")
        self.insight_text.configure(state="disabled")

    def _localized_insight_lines(self) -> list[str]:
        """Build evidence-based insights in the active interface language."""
        stats = self._stats
        if stats.entry_count == 0:
            return [
                tr(self.language, "insight_first_record"),
                tr(self.language, "insight_portable"),
                tr(self.language, "insight_weather"),
                tr(self.language, "insight_score_scope"),
            ]

        trend = (
            tr(self.language, "insight_trend_locked")
            if stats.recent_step_change_pct is None
            else tr(self.language, "insight_trend", change=f"{stats.recent_step_change_pct:+.1f}%")
        )
        rhythm = (
            tr(
                self.language,
                "insight_best_weekday",
                weekday=self._localized_option("weekday", stats.best_weekday),
            )
            if stats.best_weekday
            else tr(self.language, "insight_more_weekdays")
        )
        mood = (
            self._localized_option("mood", stats.dominant_mood)
            if stats.dominant_mood
            else tr(self.language, "not_recorded")
        )
        freshness = (
            tr(
                self.language,
                "insight_stale",
                days=stats.days_since_latest,
                coverage=f"{stats.tracking_coverage_pct:.0f}",
            )
            if stats.is_stale
            else tr(
                self.language,
                "insight_recent_activity",
                active=stats.active_last_7_days,
                coverage=f"{stats.tracking_coverage_pct:.0f}",
            )
        )
        return [
            tr(self.language, "insight_goal_rate", rate=f"{stats.perfect_goal_rate_pct:.0f}"),
            freshness,
            trend,
            tr(self.language, "insight_mood", rhythm=rhythm, mood=mood),
        ]

    def _localized_option(self, category: str, value: str | None) -> str:
        """Translate a known weekday or mood while preserving custom values."""
        if not value:
            return tr(self.language, "not_recorded")
        key = f"{category}_{value.strip().lower().replace(' ', '_')}"
        try:
            return tr(self.language, key)
        except KeyError:
            return value

    def _apply_text_palette(self) -> None:
        palette = self._palette_provider()
        self.insight_text.configure(
            background=palette["panel_alt"],
            foreground=palette["text"],
            insertbackground=palette["text"],
            selectbackground=palette["accent_alt"],
            selectforeground="#ffffff",
        )
