"""
Module: training panel
Purpose: Log training sessions and show the weekly picture (minutes, streak,
    WHO reference and recent sessions) inside the Tkinter command center.
Author: Kevin "Lirioth" Cusnir
Date: 2026-10-19 | TZ: Asia/Jerusalem
Notes: Descriptive only; the bar geometry is a pure function so it is testable headless.
"""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Literal

from .i18n import direction_for, tr
from .workouts import (
    REFERENCE_WEEKLY_MINUTES,
    WORKOUT_KINDS,
    TrainingSnapshot,
    TrainingWeek,
    WorkoutSession,
    WorkoutStore,
    build_training_snapshot,
    export_workouts_csv,
)


@dataclass(frozen=True, slots=True)
class BarGeometry:
    """Pixel geometry for one weekly bar."""

    week: TrainingWeek
    x0: float
    y0: float
    x1: float
    y1: float
    current: bool


def weekly_bar_layout(
    weeks: Sequence[TrainingWeek],
    width: int,
    height: int,
    *,
    reference: int = REFERENCE_WEEKLY_MINUTES,
    padding: int = 28,
) -> tuple[tuple[BarGeometry, ...], float]:
    """Return bar rectangles and the y position of the reference line.

    The scale always includes the reference so a quiet week still shows how
    far the 150-minute line is, and bars never overflow the canvas.

    Example:
        >>> bars, line = weekly_bar_layout([], 400, 200)
        >>> bars, round(line)
        ((), 28)
    """
    usable_width = max(1, width - padding * 2)
    usable_height = max(1, height - padding * 2)
    peak = max([reference, *(week.minutes for week in weeks)]) or 1
    baseline = height - padding

    def y_for(minutes: int) -> float:
        return baseline - usable_height * minutes / peak

    if not weeks:
        return (), y_for(reference)
    slot = usable_width / len(weeks)
    bar_width = slot * 0.58
    bars = tuple(
        BarGeometry(
            week=week,
            x0=padding + slot * index + (slot - bar_width) / 2,
            y0=y_for(week.minutes),
            x1=padding + slot * index + (slot + bar_width) / 2,
            y1=baseline,
            current=index == len(weeks) - 1,
        )
        for index, week in enumerate(weeks)
    )
    return bars, y_for(reference)


class WeeklyBarsCanvas(tk.Canvas):
    """Draw minutes per week with the WHO reference line."""

    def __init__(self, master: tk.Misc, palette: Mapping[str, str], language: str) -> None:
        super().__init__(master, height=210, highlightthickness=0, background=palette["panel_alt"])
        self.palette = dict(palette)
        self.language = language
        self.weeks: tuple[TrainingWeek, ...] = ()
        self.bind("<Configure>", lambda _event: self.redraw(), add="+")

    def set_weeks(self, weeks: Sequence[TrainingWeek]) -> None:
        """Replace the displayed weeks and redraw."""
        self.weeks = tuple(weeks)
        self.redraw()

    def redraw(self) -> None:
        """Render bars, labels and the reference line for the current size."""
        self.delete("all")
        width = max(self.winfo_width(), 320)
        height = max(self.winfo_height(), 180)
        bars, line_y = weekly_bar_layout(self.weeks, width, height)
        muted = self.palette["muted"]
        self.create_line(28, line_y, width - 28, line_y, fill=self.palette["warning"], dash=(5, 4), width=2)
        self.create_text(
            width - 30,
            line_y - 9,
            text=f"{REFERENCE_WEEKLY_MINUTES} min",
            fill=self.palette["warning"],
            anchor="e",
            font=("Segoe UI", 8, "bold"),
        )
        for bar in bars:
            color = self.palette["accent_alt"] if bar.current else self.palette["accent"]
            if bar.week.minutes:
                self.create_rectangle(bar.x0, bar.y0, bar.x1, bar.y1, fill=color, outline="")
                self.create_text(
                    (bar.x0 + bar.x1) / 2,
                    bar.y0 - 9,
                    text=str(bar.week.minutes),
                    fill=self.palette["text"],
                    font=("Segoe UI", 8, "bold"),
                )
            self.create_text(
                (bar.x0 + bar.x1) / 2,
                bar.y1 + 12,
                text=bar.week.week_start.strftime("%d/%m"),
                fill=muted,
                font=("Segoe UI", 8),
            )
        if not any(bar.week.minutes for bar in bars):
            self.create_text(
                width / 2,
                height / 2,
                text=tr(self.language, "training_empty"),
                fill=muted,
                width=width - 80,
                justify="center",
                font=("Segoe UI", 10),
            )


class TrainingPanel(ttk.Frame):
    """Log sessions and summarize recent training for the active profile.

    Args:
        master: Parent widget.
        store: Workout store bound to the app database.
        get_palette: Active palette callback.
        get_language: Active language callback.
        get_profile_name: Active profile display-name callback.
        on_status: Status-bar callback.
        on_error: Error-dialog callback.

    Example:
        >>> TrainingPanel(root, store, palette, language, name, status, error)  # doctest: +SKIP
    """

    def __init__(
        self,
        master: tk.Misc,
        store: WorkoutStore,
        get_palette: Callable[[], Mapping[str, str]],
        get_language: Callable[[], str],
        get_profile_name: Callable[[], str],
        on_status: Callable[[str], None],
        on_error: Callable[[str, Exception], None],
    ) -> None:
        super().__init__(master, style="Panel.TFrame", padding=4)
        self.store = store
        self.get_palette = get_palette
        self.get_language = get_language
        self.get_profile_name = get_profile_name
        self.on_status = on_status
        self.on_error = on_error
        self.sessions: list[WorkoutSession] = []
        self.snapshot: TrainingSnapshot = build_training_snapshot([])
        self._build()

    def t(self, key: str, **values: object) -> str:
        """Translate one key in the active language."""
        return tr(self.get_language(), key, **values)

    def _kind_labels(self) -> tuple[str, ...]:
        return tuple(self.t(f"workout_kind_{kind}") for kind in WORKOUT_KINDS)

    def _build(self) -> None:
        language = self.get_language()
        rtl = direction_for(language) == "rtl"
        anchor = "e" if rtl else "w"
        justify = "right" if rtl else "left"
        start_side = "right" if rtl else "left"
        self.columnconfigure(0 if not rtl else 1, weight=0)
        self.columnconfigure(1 if not rtl else 0, weight=1)
        self.rowconfigure(1, weight=1)

        header = ttk.Frame(self, style="Panel.TFrame", padding=(20, 12))
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        ttk.Label(
            header, text=self.t("training_title"), style="Panel.TLabel", font=("Segoe UI", 18, "bold")
        ).pack(anchor=anchor)
        ttk.Label(
            header, text=self.t("training_subtitle"), style="Panel.TLabel", justify=justify, wraplength=820
        ).pack(anchor=anchor, pady=(4, 0))

        form = ttk.Frame(self, style="Card.TFrame", padding=18)
        form.grid(row=1, column=0 if not rtl else 1, sticky="nsew", padx=(18, 10), pady=(4, 16))
        self._build_form(form, anchor, justify)

        body = ttk.Frame(self, style="Panel.TFrame", padding=(8, 4, 18, 16))
        body.grid(row=1, column=1 if not rtl else 0, sticky="nsew")
        body.columnconfigure((0, 1, 2), weight=1, uniform="training_cards")
        body.rowconfigure(3, weight=1)

        self.week_minutes_var = tk.StringVar()
        self.week_detail_var = tk.StringVar()
        self.streak_var = tk.StringVar()
        self.change_var = tk.StringVar()
        self.reference_var = tk.StringVar()
        cards = (
            ("training_this_week", self.week_minutes_var, self.week_detail_var),
            ("training_streak", self.streak_var, self.change_var),
            ("training_reference", self.reference_var, None),
        )
        for index, (title, value_var, detail_var) in enumerate(cards):
            column = 2 - index if rtl else index
            card = ttk.Frame(body, style="Card.TFrame", padding=14)
            card.grid(row=0, column=column, sticky="nsew", padx=6, pady=(0, 10))
            ttk.Label(card, text=self.t(title), style="CardTitle.TLabel").pack(anchor=anchor)
            ttk.Label(card, textvariable=value_var, style="CardValue.TLabel").pack(anchor=anchor, pady=(4, 2))
            if detail_var is not None:
                ttk.Label(
                    card, textvariable=detail_var, style="CardTitle.TLabel", justify=justify, wraplength=230
                ).pack(anchor=anchor)
            else:
                self.reference_bar = ttk.Progressbar(card, maximum=100)
                self.reference_bar.pack(fill="x", pady=(4, 0))

        chart_card = ttk.Frame(body, style="Card.TFrame", padding=(14, 10))
        chart_card.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=6, pady=(0, 10))
        ttk.Label(chart_card, text=self.t("training_weekly_minutes"), style="CardTitle.TLabel").pack(
            anchor=anchor
        )
        self.bars = WeeklyBarsCanvas(chart_card, self.get_palette(), language)
        self.bars.pack(fill="x", expand=True, pady=(6, 0))

        list_header = ttk.Frame(body, style="Panel.TFrame")
        list_header.grid(row=2, column=0, columnspan=3, sticky="ew", padx=6)
        ttk.Label(
            list_header, text=self.t("training_recent"), style="Panel.TLabel", font=("Segoe UI", 11, "bold")
        ).pack(side=start_side)
        ttk.Button(list_header, text=self.t("export_workouts_csv"), command=self._export_csv).pack(
            side="left" if rtl else "right"
        )
        ttk.Button(
            list_header, text=self.t("delete_workout"), style="Danger.TButton", command=self._delete_selected
        ).pack(side="left" if rtl else "right", padx=8)

        table = ttk.Frame(body, style="Panel.TFrame")
        table.grid(row=3, column=0, columnspan=3, sticky="nsew", padx=6, pady=(8, 0))
        columns = ("date", "kind", "minutes", "rpe", "distance", "load", "note")
        self.tree = ttk.Treeview(table, columns=columns, show="headings", selectmode="browse", height=7)
        headings = {
            "date": self.t("date"),
            "kind": self.t("workout_kind"),
            "minutes": self.t("workout_minutes"),
            "rpe": "RPE",
            "distance": "km",
            "load": self.t("training_load"),
            "note": self.t("note"),
        }
        widths = {"date": 100, "kind": 130, "minutes": 80, "rpe": 55, "distance": 70, "load": 70, "note": 220}
        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(
                column,
                width=widths[column],
                anchor="center" if column != "note" else ("e" if rtl else "w"),
            )
        scrollbar = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="right" if rtl else "left", fill="both", expand=True)
        scrollbar.pack(side="left" if rtl else "right", fill="y")
        self.scope_label = ttk.Label(
            body, text=self.t("training_scope"), style="Panel.TLabel", justify=justify, wraplength=760
        )
        self.scope_label.grid(row=4, column=0, columnspan=3, sticky=anchor, padx=6, pady=(10, 0))

    def _build_form(
        self, form: ttk.Frame, anchor: Literal["e", "w"], justify: Literal["left", "right"]
    ) -> None:
        self.date_var = tk.StringVar(value=date.today().isoformat())
        self.kind_var = tk.StringVar(value=self._kind_labels()[0])
        self.minutes_var = tk.StringVar()
        self.rpe_var = tk.IntVar(value=5)
        self.distance_var = tk.StringVar()
        self.note_var = tk.StringVar()
        ttk.Label(form, text=self.t("new_session"), style="CardValue.TLabel").pack(
            anchor=anchor, pady=(0, 10)
        )
        fields: tuple[tuple[str, tk.Variable, str], ...] = (
            (self.t("date") + " (YYYY-MM-DD)", self.date_var, "entry"),
            (self.t("workout_kind"), self.kind_var, "kind"),
            (self.t("workout_minutes"), self.minutes_var, "entry"),
            (self.t("workout_rpe"), self.rpe_var, "rpe"),
            (self.t("workout_distance"), self.distance_var, "entry"),
            (self.t("note"), self.note_var, "entry"),
        )
        for label, variable, kind in fields:
            ttk.Label(form, text=label, style="CardTitle.TLabel").pack(anchor=anchor, pady=(8, 2))
            if kind == "kind":
                ttk.Combobox(
                    form,
                    textvariable=variable,
                    values=self._kind_labels(),
                    state="readonly",
                    width=28,
                    justify=justify,
                ).pack(fill="x")
            elif kind == "rpe":
                ttk.Spinbox(
                    form, from_=1, to=10, textvariable=variable, width=6, justify=justify, wrap=False
                ).pack(anchor=anchor)
                ttk.Label(
                    form,
                    text=self.t("workout_rpe_hint"),
                    style="CardTitle.TLabel",
                    justify=justify,
                    wraplength=250,
                ).pack(anchor=anchor, pady=(3, 0))
            else:
                ttk.Entry(form, textvariable=variable, width=30, justify=justify).pack(fill="x")
        ttk.Button(form, text=self.t("save_workout"), style="Accent.TButton", command=self._save).pack(
            fill="x", pady=(18, 0)
        )

    def refresh(self, today: date | None = None) -> None:
        """Reload the active profile's sessions and update every widget."""
        self.sessions = self.store.list(None)
        self.snapshot = build_training_snapshot(self.sessions, today=today)
        snapshot = self.snapshot
        self.week_minutes_var.set(self.t("training_minutes_value", minutes=snapshot.this_week.minutes))
        self.week_detail_var.set(
            self.t(
                "training_sessions_value",
                sessions=snapshot.this_week.sessions,
                days=snapshot.this_week.active_days,
            )
        )
        self.streak_var.set(self.t("training_streak_value", weeks=snapshot.streak_weeks))
        self.change_var.set(self.t("training_vs_last_week", change=snapshot.minutes_change))
        self.reference_var.set(
            self.t(
                "training_reference_value",
                percent=snapshot.reference_percent,
                reference=snapshot.reference_minutes,
            )
        )
        self.reference_bar.configure(value=snapshot.reference_percent)
        self.bars.set_weeks(snapshot.weeks)
        self.tree.delete(*self.tree.get_children())
        for session in self.sessions[:200]:
            self.tree.insert(
                "",
                "end",
                iid=str(session.session_id),
                values=(
                    session.session_date.isoformat(),
                    self.t(f"workout_kind_{session.kind}"),
                    session.duration_min,
                    "" if session.rpe is None else session.rpe,
                    "" if session.distance_km is None else f"{session.distance_km:.1f}",
                    "" if session.load is None else session.load,
                    session.note or "",
                ),
            )

    def _save(self) -> None:
        try:
            labels = self._kind_labels()
            label = self.kind_var.get()
            kind = WORKOUT_KINDS[labels.index(label)] if label in labels else label
            session = self.store.add(
                WorkoutSession.build(
                    self.date_var.get(),
                    kind,
                    self.minutes_var.get(),
                    rpe=self.rpe_var.get(),
                    distance_km=self.distance_var.get(),
                    note=self.note_var.get(),
                )
            )
        except Exception as exc:
            self.on_error(self.t("workout_save_error"), exc)
            return
        self.minutes_var.set("")
        self.distance_var.set("")
        self.note_var.set("")
        self.refresh()
        self.on_status(
            self.t(
                "workout_saved",
                kind=self.t(f"workout_kind_{session.kind}"),
                minutes=session.duration_min,
                profile=self.get_profile_name(),
            )
        )

    def _delete_selected(self) -> None:
        selection = self.tree.selection()
        if not selection:
            self.on_status(self.t("workout_select_first"))
            return
        if not messagebox.askyesno(
            self.t("delete_workout"), self.t("confirm_delete_workout"), icon="warning"
        ):
            return
        try:
            self.store.delete(int(selection[0]))
        except Exception as exc:
            self.on_error(self.t("delete_workout"), exc)
            return
        self.refresh()
        self.on_status(self.t("workout_deleted"))

    def _export_csv(self) -> None:
        path = filedialog.asksaveasfilename(
            title=self.t("export_workouts_title"),
            defaultextension=".csv",
            initialfile="novafit-training.csv",
            filetypes=[("CSV", "*.csv")],
        )
        if not path:
            return
        try:
            count = export_workouts_csv(self.store, Path(path))
        except Exception as exc:
            self.on_error(self.t("export_workouts_csv"), exc)
            return
        self.on_status(self.t("workouts_exported", count=count, path=path))
