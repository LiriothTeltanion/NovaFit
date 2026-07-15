"""
Module: profile manager panel
Purpose: Provide local multi-user profile creation, selection, editing, and
    preference management inside the Tkinter desktop application.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: ttk only; profile data remains in the same local SQLite database.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping
import tkinter as tk
from tkinter import messagebox, ttk

from .database import NovaFitDatabase
from .i18n import direction_for, language_label, language_labels, normalize_language, tr
from .models import ACTIVITY_LEVELS, PROFILE_AVATARS, SPORT_FOCUSES, UserProfile
from .themes import normalize_theme_id, theme_label, theme_labels


class ProfileManagerPanel(ttk.Frame):
    """Manage local users and their visual/recommendation preferences.

    Args:
        master: Parent widget.
        database: Shared NovaFit database.
        get_palette: Callback returning the active theme palette.
        get_language: Callback returning the active language.
        on_profile_selected: Called after the active profile changes.
        on_status: Status-bar callback.
        on_error: Error-dialog callback.

    Example:
        >>> panel = ProfileManagerPanel(root, db, palette, language, select, status, error)  # doctest: +SKIP
    """

    def __init__(
        self,
        master: tk.Misc,
        database: NovaFitDatabase,
        get_palette: Callable[[], Mapping[str, str]],
        get_language: Callable[[], str],
        on_profile_selected: Callable[[UserProfile], None],
        on_status: Callable[[str], None],
        on_error: Callable[[str, Exception], None],
    ) -> None:
        super().__init__(master, style="Panel.TFrame", padding=18)
        self.database = database
        self.get_palette = get_palette
        self.get_language = get_language
        self.on_profile_selected = on_profile_selected
        self.on_status = on_status
        self.on_error = on_error
        self.profile_id_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.avatar_var = tk.StringVar(value="nova")
        self.language_var = tk.StringVar(value=language_label(get_language()))
        self.theme_var = tk.StringVar(value=theme_label("aurora"))
        self.step_goal_var = tk.StringVar(value="10000")
        self.water_goal_var = tk.StringVar(value="2.0")
        self.calorie_goal_var = tk.StringVar(value="2000")
        self.activity_level_var = tk.StringVar(value="balanced")
        self.sport_focus_var = tk.StringVar(value="mixed")
        self._build()
        self.refresh()

    def _build(self) -> None:
        self.columnconfigure(0, weight=3)
        self.columnconfigure(1, weight=2)
        self.rowconfigure(1, weight=1)
        header = ttk.Frame(self, style="Panel.TFrame")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        ttk.Label(header, text="👥  Local User Profiles", style="Panel.TLabel", font=("Segoe UI", 18, "bold")).pack(anchor="w")
        ttk.Label(
            header,
            text="Each profile has isolated daily records, goals, language, theme, and activity preferences.",
            style="Panel.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        list_card = ttk.Frame(self, style="Card.TFrame", padding=14)
        list_card.grid(row=1, column=0, sticky="nsew", padx=(0, 14))
        columns = ("id", "name", "language", "theme", "focus", "records")
        self.tree = ttk.Treeview(list_card, columns=columns, show="headings", selectmode="browse")
        headings = {
            "id": "ID",
            "name": "User",
            "language": "Language",
            "theme": "Theme",
            "focus": "Activity",
            "records": "Records",
        }
        widths = {"id": 45, "name": 160, "language": 90, "theme": 130, "focus": 100, "records": 70}
        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], anchor="center" if column != "name" else "w")
        self.tree.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(list_card, orient="vertical", command=self.tree.yview)
        scroll.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.bind("<<TreeviewSelect>>", self._load_selected, add="+")
        self.tree.bind("<Double-1>", self._activate_selected, add="+")

        form = ttk.Frame(self, style="Card.TFrame", padding=18)
        form.grid(row=1, column=1, sticky="nsew")
        ttk.Label(form, text="Profile Studio", style="CardValue.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))
        fields = (
            ("Display name", self.name_var, None),
            ("Avatar", self.avatar_var, PROFILE_AVATARS),
            ("Language", self.language_var, language_labels()),
            ("Theme", self.theme_var, theme_labels()),
            ("Activity level", self.activity_level_var, ACTIVITY_LEVELS),
            ("Sport focus", self.sport_focus_var, SPORT_FOCUSES),
            ("Step goal", self.step_goal_var, None),
            ("Water goal (L)", self.water_goal_var, None),
            ("Calorie reference", self.calorie_goal_var, None),
        )
        for row_index, (label, variable, values) in enumerate(fields, start=1):
            ttk.Label(form, text=label, style="CardTitle.TLabel").grid(row=row_index, column=0, sticky="w", pady=5)
            if values is None:
                widget: ttk.Entry | ttk.Combobox = ttk.Entry(form, textvariable=variable)
            else:
                widget = ttk.Combobox(form, textvariable=variable, values=values, state="readonly")
            widget.grid(row=row_index, column=1, sticky="ew", padx=(12, 0), pady=5)
        form.columnconfigure(1, weight=1)

        actions = ttk.Frame(form, style="Card.TFrame")
        actions.grid(row=10, column=0, columnspan=2, sticky="ew", pady=(16, 0))
        ttk.Button(actions, text="Create", style="Accent.TButton", command=self._create).pack(side="left")
        ttk.Button(actions, text="Update", command=self._update).pack(side="left", padx=7)
        ttk.Button(actions, text="Activate", command=self._activate_selected).pack(side="left")
        ttk.Button(actions, text="Delete", style="Danger.TButton", command=self._delete).pack(side="right")
        ttk.Button(form, text="Clear form", command=self._clear_form).grid(row=11, column=0, columnspan=2, sticky="ew", pady=(10, 0))

    def refresh(self) -> None:
        """Reload profiles and preserve the active selection.

        Returns:
            None.

        Example:
            >>> panel.refresh()  # doctest: +SKIP
        """
        active_id = self.database.active_profile_id
        self.tree.delete(*self.tree.get_children())
        selected_item: str | None = None
        for profile in self.database.list_profiles():
            item = self.tree.insert(
                "",
                "end",
                values=(
                    profile.profile_id,
                    profile.display_name,
                    language_label(profile.language),
                    theme_label(profile.theme),
                    profile.sport_focus,
                    self.database.count(profile.profile_id),
                ),
            )
            if profile.profile_id == active_id:
                selected_item = item
        if selected_item:
            self.tree.selection_set(selected_item)
            self.tree.focus(selected_item)
            self.tree.see(selected_item)
            self._load_selected()

    def apply_theme(self) -> None:
        """Refresh visual content after a theme change.

        Returns:
            None.
        """
        self.refresh()

    def refresh_language(self) -> None:
        """Update layout direction metadata and profile language selector.

        Returns:
            None.
        """
        anchor = "e" if direction_for(self.get_language()) == "rtl" else "w"
        for child in self.winfo_children():
            try:
                child.configure(anchor=anchor)
            except tk.TclError:
                continue

    def _selected_profile_id(self) -> int | None:
        selected = self.tree.selection()
        if not selected:
            return None
        return int(self.tree.item(selected[0], "values")[0])

    def _load_selected(self, _event: tk.Event[tk.Misc] | None = None) -> None:
        profile_id = self._selected_profile_id()
        if profile_id is None:
            return
        profile = self.database.get_profile(profile_id)
        if profile is None:
            return
        self.profile_id_var.set(str(profile.profile_id))
        self.name_var.set(profile.display_name)
        self.avatar_var.set(profile.avatar)
        self.language_var.set(language_label(profile.language))
        self.theme_var.set(theme_label(profile.theme))
        self.step_goal_var.set(str(profile.step_goal))
        self.water_goal_var.set(str(profile.water_goal_l))
        self.calorie_goal_var.set(str(profile.calorie_goal))
        self.activity_level_var.set(profile.activity_level)
        self.sport_focus_var.set(profile.sport_focus)

    def _profile_from_form(self, profile_id: int | None = None) -> UserProfile:
        return UserProfile.build(
            self.name_var.get(),
            profile_id=profile_id,
            avatar=self.avatar_var.get(),
            language=normalize_language(self.language_var.get()),
            theme=normalize_theme_id(self.theme_var.get()),
            step_goal=self.step_goal_var.get(),
            water_goal_l=self.water_goal_var.get(),
            calorie_goal=self.calorie_goal_var.get(),
            activity_level=self.activity_level_var.get(),
            sport_focus=self.sport_focus_var.get(),
        )

    def _create(self) -> None:
        try:
            profile = self.database.create_profile(self._profile_from_form())
            self.database.set_active_profile(profile.profile_id or 1)
            self.on_profile_selected(profile)
            self.on_status(f"Created profile {profile.display_name} ✅")
            self.refresh()
        except (ValueError, sqlite3.Error) as exc:
            self.on_error("Could not create profile", exc)

    def _update(self) -> None:
        profile_id = self._selected_profile_id()
        if profile_id is None:
            self.on_error("Could not update profile", ValueError("Select a profile first."))
            return
        try:
            profile = self.database.update_profile(self._profile_from_form(profile_id))
            if profile_id == self.database.active_profile_id:
                self.on_profile_selected(profile)
            self.on_status(f"Updated profile {profile.display_name} ✅")
            self.refresh()
        except (ValueError, sqlite3.Error) as exc:
            self.on_error("Could not update profile", exc)

    def _activate_selected(self, _event: tk.Event[tk.Misc] | None = None) -> None:
        profile_id = self._selected_profile_id()
        if profile_id is None:
            self.on_error("Could not activate profile", ValueError("Select a profile first."))
            return
        try:
            profile = self.database.set_active_profile(profile_id)
            self.on_profile_selected(profile)
            self.on_status(f"Active profile: {profile.display_name} ✅")
            self.refresh()
        except ValueError as exc:
            self.on_error("Could not activate profile", exc)

    def _delete(self) -> None:
        profile_id = self._selected_profile_id()
        if profile_id is None:
            return
        profile = self.database.get_profile(profile_id)
        if profile is None:
            return
        if not messagebox.askyesno(
            "Delete profile",
            f"Delete {profile.display_name} and all of this profile's records? This cannot be undone.",
            icon="warning",
        ):
            return
        try:
            deleted = self.database.delete_profile(profile_id)
            if deleted:
                primary = self.database.set_active_profile(1)
                self.on_profile_selected(primary)
                self.on_status(f"Deleted profile {profile.display_name} ✅")
            self.refresh()
        except (ValueError, sqlite3.Error) as exc:
            self.on_error("Could not delete profile", exc)

    def _clear_form(self) -> None:
        self.profile_id_var.set("")
        self.name_var.set("")
        self.avatar_var.set("nova")
        self.language_var.set(language_label(self.get_language()))
        self.theme_var.set(theme_label("aurora"))
        self.step_goal_var.set("10000")
        self.water_goal_var.set("2.0")
        self.calorie_goal_var.set("2000")
        self.activity_level_var.set("balanced")
        self.sport_focus_var.set("mixed")
