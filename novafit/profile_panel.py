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
        self.language = normalize_language(get_language())
        self._rtl = direction_for(self.language) == "rtl"
        self._activity_labels = {value: tr(self.language, f"activity_{value}") for value in ACTIVITY_LEVELS}
        self._sport_labels = {value: tr(self.language, f"sport_{value}") for value in SPORT_FOCUSES}
        self.profile_id_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.avatar_var = tk.StringVar(value="nova")
        self.language_var = tk.StringVar(value=language_label(get_language()))
        self.theme_var = tk.StringVar(value=theme_label("aurora"))
        self.step_goal_var = tk.StringVar(value="10000")
        self.water_goal_var = tk.StringVar(value="2.0")
        self.calorie_goal_var = tk.StringVar(value="2000")
        self.activity_level_var = tk.StringVar(value=self._activity_labels["balanced"])
        self.sport_focus_var = tk.StringVar(value=self._sport_labels["mixed"])
        self._build()
        self.refresh()

    def _build(self) -> None:
        anchor = "e" if self._rtl else "w"
        justify = "right" if self._rtl else "left"
        start_side = "right" if self._rtl else "left"
        end_side = "left" if self._rtl else "right"
        list_column = 1 if self._rtl else 0
        form_column = 0 if self._rtl else 1
        self.columnconfigure(list_column, weight=3)
        self.columnconfigure(form_column, weight=2)
        self.rowconfigure(1, weight=1)
        header = ttk.Frame(self, style="Panel.TFrame")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 14))
        ttk.Label(
            header,
            text=tr(self.language, "profile_header"),
            style="Panel.TLabel",
            font=("Segoe UI", 18, "bold"),
            anchor=anchor,
            justify=justify,
        ).pack(anchor=anchor)
        ttk.Label(
            header,
            text=tr(self.language, "profile_subtitle"),
            style="Panel.TLabel",
            anchor=anchor,
            justify=justify,
        ).pack(anchor=anchor, pady=(4, 0))

        list_card = ttk.Frame(self, style="Card.TFrame", padding=14)
        list_card.grid(row=1, column=list_column, sticky="nsew", padx=7)
        columns = ("id", "name", "language", "theme", "focus", "records")
        self.tree = ttk.Treeview(list_card, columns=columns, show="headings", selectmode="browse")
        self.tree.configure(displaycolumns=tuple(reversed(columns)) if self._rtl else columns)
        headings = {
            "id": "ID",
            "name": tr(self.language, "user"),
            "language": tr(self.language, "language"),
            "theme": tr(self.language, "theme"),
            "focus": tr(self.language, "profile_activity"),
            "records": tr(self.language, "profile_records"),
        }
        widths = {"id": 45, "name": 160, "language": 90, "theme": 130, "focus": 100, "records": 70}
        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], anchor="center" if column != "name" else anchor)
        self.tree.pack(side=start_side, fill="both", expand=True)
        scroll = ttk.Scrollbar(list_card, orient="vertical", command=self.tree.yview)
        scroll.pack(side=end_side, fill="y")
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.bind("<<TreeviewSelect>>", self._load_selected, add="+")
        self.tree.bind("<Double-1>", self._activate_selected, add="+")

        form = ttk.Frame(self, style="Card.TFrame", padding=18)
        form.grid(row=1, column=form_column, sticky="nsew")
        ttk.Label(form, text=tr(self.language, "profile_studio"), style="CardValue.TLabel").grid(
            row=0,
            column=0,
            columnspan=2,
            sticky=anchor,
            pady=(0, 12),
        )
        fields = (
            (tr(self.language, "display_name"), self.name_var, None),
            (tr(self.language, "avatar"), self.avatar_var, PROFILE_AVATARS),
            (tr(self.language, "language"), self.language_var, language_labels()),
            (tr(self.language, "theme"), self.theme_var, theme_labels()),
            (
                tr(self.language, "activity_level"),
                self.activity_level_var,
                tuple(self._activity_labels.values()),
            ),
            (tr(self.language, "sport_focus"), self.sport_focus_var, tuple(self._sport_labels.values())),
            (tr(self.language, "step_goal"), self.step_goal_var, None),
            (tr(self.language, "water_goal"), self.water_goal_var, None),
            (tr(self.language, "calorie_reference"), self.calorie_goal_var, None),
        )
        for row_index, (label, variable, values) in enumerate(fields, start=1):
            label_column = 1 if self._rtl else 0
            input_column = 0 if self._rtl else 1
            ttk.Label(form, text=label, style="CardTitle.TLabel").grid(
                row=row_index,
                column=label_column,
                sticky=anchor,
                pady=5,
            )
            if values is None:
                widget: ttk.Entry | ttk.Combobox = ttk.Entry(form, textvariable=variable, justify=justify)
            else:
                widget = ttk.Combobox(
                    form,
                    textvariable=variable,
                    values=values,
                    state="readonly",
                    justify=justify,
                )
            widget.grid(row=row_index, column=input_column, sticky="ew", padx=6, pady=5)
        form.columnconfigure(0 if self._rtl else 1, weight=1)

        actions = ttk.Frame(form, style="Card.TFrame")
        actions.grid(row=10, column=0, columnspan=2, sticky="ew", pady=(16, 0))
        ttk.Button(
            actions, text=tr(self.language, "create"), style="Accent.TButton", command=self._create
        ).pack(side=start_side)
        ttk.Button(actions, text=tr(self.language, "update"), command=self._update).pack(
            side=start_side, padx=7
        )
        ttk.Button(actions, text=tr(self.language, "activate"), command=self._activate_selected).pack(
            side=start_side
        )
        ttk.Button(
            actions, text=tr(self.language, "delete"), style="Danger.TButton", command=self._delete
        ).pack(side=end_side)
        ttk.Button(form, text=tr(self.language, "clear_form"), command=self._clear_form).grid(
            row=11,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(10, 0),
        )

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
                    self._sport_labels.get(profile.sport_focus, profile.sport_focus),
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
        """Rebuild localized labels and RTL geometry after a language change.

        Returns:
            None.
        """
        self.language = normalize_language(self.get_language())
        self._rtl = direction_for(self.language) == "rtl"
        self._activity_labels = {value: tr(self.language, f"activity_{value}") for value in ACTIVITY_LEVELS}
        self._sport_labels = {value: tr(self.language, f"sport_{value}") for value in SPORT_FOCUSES}
        for child in self.winfo_children():
            child.destroy()
        self._build()
        self.refresh()

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
        self.activity_level_var.set(self._activity_labels.get(profile.activity_level, profile.activity_level))
        self.sport_focus_var.set(self._sport_labels.get(profile.sport_focus, profile.sport_focus))

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
            activity_level=self._value_from_label(self.activity_level_var.get(), self._activity_labels),
            sport_focus=self._value_from_label(self.sport_focus_var.get(), self._sport_labels),
        )

    @staticmethod
    def _value_from_label(label: str, labels: Mapping[str, str]) -> str:
        """Resolve a localized combobox label to its stable model value."""
        for value, localized_label in labels.items():
            if label == localized_label:
                return value
        return label

    def _create(self) -> None:
        try:
            profile = self.database.create_profile(self._profile_from_form())
            self.database.set_active_profile(profile.profile_id or 1)
            self.on_profile_selected(profile)
            self.on_status(tr(self.language, "profile_created", name=profile.display_name))
            self.refresh()
        except (ValueError, sqlite3.Error) as exc:
            self.on_error(tr(self.language, "create_profile_error"), exc)

    def _update(self) -> None:
        profile_id = self._selected_profile_id()
        if profile_id is None:
            self.on_error(
                tr(self.language, "update_profile_error"),
                ValueError(tr(self.language, "select_profile_first")),
            )
            return
        try:
            profile = self.database.update_profile(self._profile_from_form(profile_id))
            if profile_id == self.database.active_profile_id:
                self.on_profile_selected(profile)
            self.on_status(tr(self.language, "profile_updated", name=profile.display_name))
            self.refresh()
        except (ValueError, sqlite3.Error) as exc:
            self.on_error(tr(self.language, "update_profile_error"), exc)

    def _activate_selected(self, _event: tk.Event[tk.Misc] | None = None) -> None:
        profile_id = self._selected_profile_id()
        if profile_id is None:
            self.on_error(
                tr(self.language, "activate_profile_error"),
                ValueError(tr(self.language, "select_profile_first")),
            )
            return
        try:
            profile = self.database.set_active_profile(profile_id)
            self.on_profile_selected(profile)
            self.on_status(tr(self.language, "profile_activated", name=profile.display_name))
            self.refresh()
        except ValueError as exc:
            self.on_error(tr(self.language, "activate_profile_error"), exc)

    def _delete(self) -> None:
        profile_id = self._selected_profile_id()
        if profile_id is None:
            return
        profile = self.database.get_profile(profile_id)
        if profile is None:
            return
        if not messagebox.askyesno(
            tr(self.language, "delete_profile_title"),
            tr(self.language, "delete_profile_confirm", name=profile.display_name),
            icon="warning",
        ):
            return
        try:
            deleted = self.database.delete_profile(profile_id)
            if deleted:
                primary = self.database.set_active_profile(1)
                self.on_profile_selected(primary)
                self.on_status(tr(self.language, "profile_deleted", name=profile.display_name))
            self.refresh()
        except (ValueError, sqlite3.Error) as exc:
            self.on_error(tr(self.language, "delete_profile_error"), exc)

    def _clear_form(self) -> None:
        self.profile_id_var.set("")
        self.name_var.set("")
        self.avatar_var.set("nova")
        self.language_var.set(language_label(self.get_language()))
        self.theme_var.set(theme_label("aurora"))
        self.step_goal_var.set("10000")
        self.water_goal_var.set("2.0")
        self.calorie_goal_var.set("2000")
        self.activity_level_var.set(self._activity_labels["balanced"])
        self.sport_focus_var.set(self._sport_labels["mixed"])
