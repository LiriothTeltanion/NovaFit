"""
Module: recommendation panel
Purpose: Present explainable sport, recovery, hydration, and data-quality
    suggestions inside a colorful, scrollable Tkinter workspace.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Recommendations are general education, not medical advice.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
import tkinter as tk
from tkinter import filedialog, ttk
from pathlib import Path

from .config import AppSettings
from .i18n import direction_for, tr
from .models import HealthEntry, UserProfile
from .recommendations import RecommendationPlan, build_recommendation_plan, format_recommendation_plan
from .ui_components import ActivityOrbitCanvas


class RecommendationsPanel(ttk.Frame):
    """Display the Sport & Data Coach for the active user.

    Args:
        master: Parent widget.
        settings: Current goals.
        get_palette: Active palette callback.
        get_language: Active-language callback.
        on_status: Status callback.

    Example:
        >>> panel = RecommendationsPanel(root, settings, palette, language, status)  # doctest: +SKIP
    """

    def __init__(
        self,
        master: tk.Misc,
        settings: AppSettings,
        get_palette: Callable[[], Mapping[str, str]],
        get_language: Callable[[], str],
        on_status: Callable[[str], None],
    ) -> None:
        super().__init__(master, style="Panel.TFrame", padding=4)
        self.settings = settings
        self.get_palette = get_palette
        self.get_language = get_language
        self.on_status = on_status
        self.entries: list[HealthEntry] = []
        self.profile = UserProfile.build("Primary User")
        self.plan = build_recommendation_plan([], settings, self.profile)
        self._build()

    def _build(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        header = ttk.Frame(self, style="Panel.TFrame", padding=(20, 14))
        header.grid(row=0, column=0, sticky="ew")
        title = ttk.Frame(header, style="Panel.TFrame")
        title.pack(side="left", fill="x", expand=True)
        self.title_var = tk.StringVar(value=tr(self.get_language(), "recommendation_title"))
        self.summary_var = tk.StringVar(value=self.plan.summary)
        ttk.Label(title, textvariable=self.title_var, style="Panel.TLabel", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(title, textvariable=self.summary_var, style="Panel.TLabel", wraplength=760).pack(anchor="w", pady=(5, 0))
        self.orbit = ActivityOrbitCanvas(header, self.get_palette(), reduced_motion=self.settings.reduce_motion)
        self.orbit.pack(side="right")

        body = ttk.Frame(self, style="Panel.TFrame", padding=(18, 2, 18, 18))
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(1, weight=1)

        confidence_card = ttk.Frame(body, style="Card.TFrame", padding=16)
        confidence_card.grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=(0, 12))
        ttk.Label(confidence_card, text=tr(self.get_language(), "data_quality"), style="CardTitle.TLabel").pack(anchor="w")
        self.confidence_var = tk.StringVar(value="0%")
        ttk.Label(confidence_card, textvariable=self.confidence_var, style="CardValue.TLabel").pack(anchor="w", pady=(4, 6))
        self.confidence_bar = ttk.Progressbar(confidence_card, maximum=100)
        self.confidence_bar.pack(fill="x")

        actions = ttk.Frame(body, style="Card.TFrame", padding=16)
        actions.grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=(0, 12))
        ttk.Label(actions, text="Coach tools", style="CardTitle.TLabel").pack(anchor="w")
        ttk.Button(actions, text="Export recommendations", command=self._export).pack(fill="x", pady=(8, 4))
        ttk.Button(actions, text="Refresh from active data", command=self._refresh_current).pack(fill="x", pady=4)

        canvas = tk.Canvas(body, highlightthickness=0, background=self.get_palette()["bg"])
        canvas.grid(row=1, column=0, columnspan=2, sticky="nsew")
        scrollbar = ttk.Scrollbar(body, orient="vertical", command=canvas.yview)
        scrollbar.grid(row=1, column=2, sticky="ns")
        canvas.configure(yscrollcommand=scrollbar.set)
        self.cards = ttk.Frame(canvas, style="Panel.TFrame")
        window = canvas.create_window((0, 0), window=self.cards, anchor="nw")
        self.cards.bind("<Configure>", lambda _event: canvas.configure(scrollregion=canvas.bbox("all")), add="+")
        canvas.bind("<Configure>", lambda event: canvas.itemconfigure(window, width=event.width), add="+")
        self.canvas = canvas
        self._render_cards()

    def refresh(
        self,
        entries: Sequence[HealthEntry],
        settings: AppSettings,
        profile: UserProfile,
    ) -> None:
        """Rebuild recommendations from active profile data.

        Args:
            entries: Active profile records.
            settings: Current goals.
            profile: Active profile preferences.

        Returns:
            None.

        Example:
            >>> panel.refresh([], settings, profile)  # doctest: +SKIP
        """
        self.entries = list(entries)
        self.settings = settings
        self.profile = profile
        self.plan = build_recommendation_plan(self.entries, settings, profile, self.get_language())
        self.title_var.set(tr(self.get_language(), "recommendation_title"))
        self.summary_var.set(self.plan.summary)
        self.confidence_var.set(f"{self.plan.data_confidence_pct}%")
        self.confidence_bar["value"] = self.plan.data_confidence_pct
        self._render_cards()

    def apply_theme(self) -> None:
        """Apply the active palette to animated and scrollable surfaces."""
        palette = self.get_palette()
        self.orbit.set_palette(palette)
        self.orbit.set_reduced_motion(self.settings.reduce_motion)
        self.canvas.configure(background=palette["bg"])
        self._render_cards()

    def _render_cards(self) -> None:
        for child in self.cards.winfo_children():
            child.destroy()
        language = self.get_language()
        rtl = direction_for(language) == "rtl"
        anchor = "e" if rtl else "w"
        justify = "right" if rtl else "left"
        palette = self.get_palette()
        priorities = {"high": palette["danger"], "medium": palette["warning"], "low": palette["accent"]}

        for index, item in enumerate(self.plan.items):
            card = ttk.Frame(self.cards, style="Card.TFrame", padding=18)
            card.pack(fill="x", pady=6)
            title_row = ttk.Frame(card, style="Card.TFrame")
            title_row.pack(fill="x")
            ttk.Label(title_row, text=f"{index + 1:02d}  {item.title}", style="CardValue.TLabel").pack(side="right" if rtl else "left")
            priority = tk.Label(
                title_row,
                text=item.priority.upper(),
                bg=priorities[item.priority],
                fg=palette["bg"],
                padx=9,
                pady=3,
                font=("Segoe UI", 8, "bold"),
            )
            priority.pack(side="left" if rtl else "right")
            ttk.Label(card, text=item.action, style="CardTitle.TLabel", wraplength=940, justify=justify).pack(anchor=anchor, pady=(10, 4))
            ttk.Label(card, text=f"{tr(language, 'why_this')}: {item.reason}", style="CardTitle.TLabel", wraplength=940, justify=justify).pack(anchor=anchor)

        weekly = ttk.Frame(self.cards, style="Card.TFrame", padding=18)
        weekly.pack(fill="x", pady=(12, 6))
        ttk.Label(weekly, text=tr(language, "weekly_plan"), style="CardValue.TLabel").pack(anchor=anchor)
        for item in self.plan.weekly_plan:
            ttk.Label(weekly, text=f"• {item}", style="CardTitle.TLabel", wraplength=940, justify=justify).pack(anchor=anchor, pady=3)
        disclaimer = ttk.Frame(self.cards, style="Card.TFrame", padding=18)
        disclaimer.pack(fill="x", pady=(6, 20))
        ttk.Label(disclaimer, text="⚠  " + self.plan.disclaimer, style="CardTitle.TLabel", wraplength=940, justify=justify).pack(anchor=anchor)

    def _refresh_current(self) -> None:
        self.refresh(self.entries, self.settings, self.profile)
        self.on_status("Recommendations refreshed from the active profile. ✅")

    def _export(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Export NovaFit recommendations",
            initialfile=f"novafit-recommendations-{self.profile.display_name.lower().replace(' ', '-')}.txt",
            defaultextension=".txt",
            filetypes=[("Text document", "*.txt")],
        )
        if not path:
            return
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(format_recommendation_plan(self.plan, self.profile) + "\n", encoding="utf-8")
        self.on_status(f"Recommendations saved to {destination} ✅")
