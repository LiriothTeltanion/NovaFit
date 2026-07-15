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

from .analytics import DashboardStats, build_insight_lines
from .charts import CHART_VIEWS, create_dashboard_figure, normalize_chart_view, save_dashboard_chart
from .config import AppSettings
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

        self.range_var = tk.StringVar(value=str(settings.chart_days))
        self.view_var = tk.StringVar(value=CHART_VIEWS.get(settings.chart_view, "Command Center"))
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
        self.step_goal_var = tk.StringVar(value="Step goal —")
        self.water_goal_var = tk.StringVar(value="Water goal —")
        self.both_goal_var = tk.StringVar(value="Both goals —")
        self.latest_var = tk.StringVar(value="No latest record yet.")
        self._build()

    def _build(self) -> None:
        controls = ttk.Frame(self, style="Panel.TFrame")
        controls.pack(fill="x", pady=(0, 10))
        ttk.Label(controls, text="Analytics view", style="Panel.TLabel").pack(side="left")
        view = ttk.Combobox(
            controls,
            textvariable=self.view_var,
            values=tuple(CHART_VIEWS.values()),
            state="readonly",
            width=18,
        )
        view.pack(side="left", padx=(7, 16))
        ttk.Label(controls, text="Calendar range", style="Panel.TLabel").pack(side="left")
        range_box = ttk.Combobox(
            controls,
            textvariable=self.range_var,
            values=("7", "14", "30", "60", "90", "180", "365"),
            state="readonly",
            width=7,
        )
        range_box.pack(side="left", padx=(7, 8))
        ttk.Label(controls, text="days", style="Panel.TLabel").pack(side="left")
        ttk.Button(controls, text="Refresh charts", style="Accent.TButton", command=self.refresh_chart).pack(side="right")
        ttk.Button(controls, text="Export PNG", command=self.export_png).pack(side="right", padx=(0, 8))
        view.bind("<<ComboboxSelected>>", lambda _event: self.refresh_chart())
        range_box.bind("<<ComboboxSelected>>", lambda _event: self.refresh_chart())

        cards = ttk.Frame(self, style="Panel.TFrame")
        cards.pack(fill="x", pady=(0, 10))
        for column in range(5):
            cards.columnconfigure(column, weight=1)
        specs = [
            ("Consistency", "momentum"),
            ("Tracked days", "tracked"),
            ("30-day coverage", "coverage"),
            ("Total steps", "total_steps"),
            ("Average steps", "average_steps"),
            ("Average water", "average_water"),
            ("Both goals", "combined_goals"),
            ("Current / longest", "streak"),
            ("Best day", "best_day"),
            ("Recent trend", "trend"),
        ]
        for index, (label, key) in enumerate(specs):
            card = ttk.Frame(cards, style="Card.TFrame", padding=(13, 10))
            card.grid(row=index // 5, column=index % 5, sticky="nsew", padx=4, pady=4)
            ttk.Label(card, text=label.upper(), style="CardTitle.TLabel").pack(anchor="w")
            ttk.Label(card, textvariable=self.metric_vars[key], style="CardValue.TLabel").pack(anchor="w", pady=(4, 0))

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

        ttk.Label(insights_shell, text="Signal summary", style="CardValue.TLabel").pack(anchor="w")
        ttk.Label(
            insights_shell,
            text="Transparent observations from your stored records — never a diagnosis.",
            style="CardTitle.TLabel",
            wraplength=225,
            justify="left",
        ).pack(anchor="w", pady=(5, 12))
        ttk.Label(insights_shell, textvariable=self.latest_var, style="Panel.TLabel", wraplength=225, justify="left").pack(anchor="w")

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
            ttk.Label(insights_shell, textvariable=variable, style="CardTitle.TLabel").pack(anchor="w", pady=2)
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
        self.view_var.set(CHART_VIEWS.get(settings.chart_view, "Command Center"))
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
            view = normalize_chart_view(self.view_var.get())
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
                text="Theme-aware local preview · use Export PNG for full-resolution artwork",
                style="CardTitle.TLabel",
                anchor="center",
            ).pack(fill="x", pady=(4, 0))
            figure.clear()
            buffer.close()
        except (ImportError, ValueError, tk.TclError) as exc:
            self._error_callback("Dashboard chart", exc)

    def export_png(self) -> None:
        """Export the selected view and range as a high-resolution PNG.

        Returns:
            None.

        Example:
            >>> panel.export_png()  # doctest: +SKIP
        """
        destination = filedialog.asksaveasfilename(
            title="Save NovaFit analytics dashboard",
            defaultextension=".png",
            filetypes=[("PNG image", "*.png")],
            initialfile=f"novafit-{normalize_chart_view(self.view_var.get())}-{self.range_var.get()}d.png",
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
                view=normalize_chart_view(self.view_var.get()),
            )
            self._status_callback(f"Analytics dashboard saved to {path} ✅")
        except (ImportError, OSError, ValueError) as exc:
            self._error_callback("Export chart", exc)

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
        return int(self.range_var.get()), normalize_chart_view(self.view_var.get())

    def _update_metrics(self) -> None:
        stats = self._stats
        trend = "Need 14 records" if stats.recent_step_change_pct is None else f"{stats.recent_step_change_pct:+.1f}%"
        calories = "N/A" if stats.average_calories is None else f"{stats.average_calories:,} kcal"
        self.metric_vars["momentum"].set(f"{stats.consistency_score}/100")
        self.metric_vars["tracked"].set(str(stats.entry_count))
        self.metric_vars["coverage"].set(f"{stats.tracking_coverage_pct:.0f}%")
        self.metric_vars["total_steps"].set(f"{stats.total_steps:,}")
        self.metric_vars["average_steps"].set(f"{stats.average_steps:,}")
        self.metric_vars["average_water"].set(f"{stats.average_water_l:.2f} L")
        self.metric_vars["combined_goals"].set(f"{stats.perfect_goal_days} days")
        self.metric_vars["streak"].set(f"{stats.current_streak_days} / {stats.longest_tracking_streak_days}d")
        self.metric_vars["best_day"].set(
            "—" if stats.best_date is None else f"{stats.best_steps:,} · {stats.best_date[5:]}"
        )
        self.metric_vars["trend"].set(trend)
        latest = max(self._entries, key=lambda item: item.entry_date) if self._entries else None
        latest_line = (
            "No latest record yet."
            if latest is None
            else f"Latest record: {latest.entry_date} · {latest.steps:,} steps · {latest.water_l:.2f} L water"
        )
        self.latest_var.set(
            f"{latest_line}\nAverage calories: {calories}\nDominant mood: {stats.dominant_mood or 'Not recorded'}"
        )

        self.step_progress["value"] = stats.step_goal_rate_pct
        self.water_progress["value"] = stats.water_goal_rate_pct
        self.both_progress["value"] = stats.perfect_goal_rate_pct
        self.step_goal_var.set(f"Step goal · {stats.step_goal_rate_pct:.0f}% of tracked dates")
        self.water_goal_var.set(f"Water goal · {stats.water_goal_rate_pct:.0f}% of tracked dates")
        self.both_goal_var.set(f"Both goals · {stats.perfect_goal_rate_pct:.0f}% of tracked dates")

    def _update_insights(self) -> None:
        lines = build_insight_lines(self._stats, self.settings)
        self.insight_text.configure(state="normal")
        self.insight_text.delete("1.0", "end")
        for index, line in enumerate(lines, start=1):
            self.insight_text.insert("end", f"{index}. {line}\n\n")
        self.insight_text.configure(state="disabled")

    def _apply_text_palette(self) -> None:
        palette = self._palette_provider()
        self.insight_text.configure(
            background=palette["panel_alt"],
            foreground=palette["text"],
            insertbackground=palette["text"],
            selectbackground=palette["accent_alt"],
            selectforeground="#ffffff",
        )
