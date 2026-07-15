"""
Module: ultimate Tkinter desktop interface
Purpose: Provide a colorful, multilingual, multi-profile wellness command center
    with analytics, motivation, recommendations, portable backups, and settings.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: ttk-first; comments in ENGLISH; decorative animation respects reduced motion.
"""

from __future__ import annotations

import logging
import sqlite3
import tkinter as tk
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import replace
from datetime import date, timedelta
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Callable, TypeVar

from . import APP_NAME, __version__
from .analytics import calculate_dashboard
from .backup import BACKUP_DIR, create_complete_backup
from .charts import CHART_VIEWS
from .config import (
    CONFIG_PATH,
    CSV_EXPORT_PATH,
    DB_PATH,
    EXPORT_PATH,
    AppSettings,
    load_settings,
    save_settings,
)
from .dashboard_panel import DashboardPanel
from .database import NovaFitDatabase
from .icon_factory import IconFactory
from .i18n import (
    direction_for,
    language_label,
    language_labels,
    normalize_language,
    tr,
)
from .io_utils import (
    ImportResult,
    export_csv,
    export_json,
    generate_demo_data,
    import_csv,
    import_json,
    initialize_sample_data,
)
from .models import HealthEntry, UserProfile
from .motivation_panel import MotivationCenterPanel
from .profile_panel import ProfileManagerPanel
from .recommendations_panel import RecommendationsPanel
from .reporting import export_html_report
from .themes import (
    accessible_text_color,
    get_theme,
    next_theme,
    normalize_theme_id,
    theme_label,
    theme_labels,
)
from .ui_components import UltimateHeroCanvas
from .weather import format_weather, get_weather

LOGGER = logging.getLogger(__name__)
JobResult = TypeVar("JobResult")


class NovaFitApp(tk.Tk):
    """Run the complete NovaFit Ultimate desktop experience.

    Args:
        database_path: SQLite file used by this GUI session.

    Example:
        >>> app = NovaFitApp(Path('data/example.db'))  # doctest: +SKIP
        >>> app.mainloop()  # doctest: +SKIP
    """

    def __init__(self, database_path: Path = DB_PATH) -> None:
        super().__init__()
        self.database = NovaFitDatabase(database_path)
        self.database.initialize()
        self.settings = load_settings()
        try:
            self.active_profile = self.database.set_active_profile(self.settings.active_profile_id)
        except ValueError:
            self.active_profile = self.database.set_active_profile(1)
            self.settings.active_profile_id = 1
        self._sync_settings_from_profile(self.active_profile, persist=False)
        self._status_after_id: str | None = None
        self._closing = False
        self._background_jobs: set[Future[object]] = set()
        self._executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="novafit")

        self.title(f"{APP_NAME} {__version__} — {self.t('app_subtitle')}")
        self.minsize(1024, 680)
        self._set_initial_geometry()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.tk.call("tk", "scaling", self.settings.ui_scale)

        self.status_var = tk.StringVar(value=self.t("ready") + " 💙")
        self.theme_var = tk.StringVar(value=self.settings.theme)
        self.theme_choice_var = tk.StringVar(value=theme_label(self.settings.theme))
        self.language_choice_var = tk.StringVar(value=language_label(self.settings.language))
        self.profile_choice_var = tk.StringVar()
        self._create_variables()
        self.icon_factory = IconFactory(self)
        self._apply_window_icon()
        self._configure_style()
        self._build_menu()
        self._build_layout()
        self._bind_shortcuts()
        self.refresh_all()
        self.after(350, self.dashboard_panel.finalize_layout)
        self.after(700, self.dashboard_panel.finalize_layout)
        self.after_idle(self._animate_window_entry)

    @property
    def palette(self) -> dict[str, str]:
        """Return the active theme palette.

        Returns:
            Mutable color mapping consumed by widgets.

        Example:
            >>> app.palette['bg']  # doctest: +SKIP
            '#061314'
        """
        return dict(get_theme(self.theme_var.get()).ui)

    def _set_initial_geometry(self) -> None:
        """Fit and center the command center across laptop and desktop displays."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        width = min(1580, max(1024, screen_width - 80))
        height = min(980, max(680, screen_height - 110))
        x = max(0, (screen_width - width) // 2)
        y = max(0, (screen_height - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    @property
    def language(self) -> str:
        """Return the active interface language.

        Returns:
            ``en``, ``es``, or ``he``.

        Example:
            >>> app.language  # doctest: +SKIP
            'en'
        """
        return normalize_language(self.settings.language)

    def t(self, key: str, **values: object) -> str:
        """Translate one interface key.

        Args:
            key: Translation key.
            **values: Optional formatting values.

        Returns:
            Translated text.

        Example:
            >>> app.t('theme')  # doctest: +SKIP
            'Theme'
        """
        return tr(self.language, key, **values)

    def _create_variables(self) -> None:
        today = date.today().isoformat()
        self.entry_date_var = tk.StringVar(value=today)
        self.steps_var = tk.StringVar()
        self.water_var = tk.StringVar()
        self.calories_var = tk.StringVar()
        self.mood_var = tk.StringVar(value=self.t("mood_focused"))
        self.note_var = tk.StringVar()
        self.search_start_var = tk.StringVar(value=(date.today() - timedelta(days=30)).isoformat())
        self.search_end_var = tk.StringVar(value=today)
        self.weather_city_var = tk.StringVar(value=self.settings.default_city)
        self.weather_result_var = tk.StringVar(value=self.t("weather_on_demand"))
        self.step_goal_var = tk.StringVar(value=str(self.settings.step_goal))
        self.water_goal_var = tk.StringVar(value=str(self.settings.water_goal_l))
        self.calorie_goal_var = tk.StringVar(value=str(self.settings.calorie_goal))
        self.chart_days_var = tk.StringVar(value=str(self.settings.chart_days))
        self.chart_view_var = tk.StringVar(value=self._localized_chart_view(self.settings.chart_view))
        self.reduce_motion_var = tk.BooleanVar(value=self.settings.reduce_motion)
        self.ui_scale_var = tk.StringVar(value=str(self.settings.ui_scale))

    def _configure_style(self) -> None:
        palette = self.palette
        on_accent = accessible_text_color(palette["accent"])
        on_accent_alt = accessible_text_color(palette["accent_alt"])
        on_danger = accessible_text_color(palette["danger"])
        on_warning = accessible_text_color(palette["warning"])
        rtl = direction_for(self.language) == "rtl"
        anchor = "e" if rtl else "w"
        self.configure(background=palette["bg"])
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        font_scale = max(0.9, min(1.25, self.settings.ui_scale))
        body = max(9, round(10 * font_scale))
        small = max(8, round(8 * font_scale))
        hero = max(19, round(24 * font_scale))
        style.configure("TFrame", background=palette["bg"])
        style.configure("Panel.TFrame", background=palette["panel"])
        style.configure("Card.TFrame", background=palette["panel_alt"], relief="flat")
        style.configure("Topbar.TFrame", background=palette["panel"])
        style.configure(
            "TLabel", background=palette["bg"], foreground=palette["text"], font=("Segoe UI", body)
        )
        style.configure(
            "Panel.TLabel", background=palette["panel"], foreground=palette["text"], font=("Segoe UI", body)
        )
        style.configure(
            "CardTitle.TLabel",
            background=palette["panel_alt"],
            foreground=palette["muted"],
            font=("Segoe UI", small, "bold"),
        )
        style.configure(
            "CardValue.TLabel",
            background=palette["panel_alt"],
            foreground=palette["accent"],
            font=("Segoe UI", max(13, body + 4), "bold"),
        )
        style.configure(
            "Hero.TLabel",
            background=palette["panel"],
            foreground=palette["text"],
            font=("Segoe UI", hero, "bold"),
            anchor=anchor,
        )
        style.configure(
            "Subtitle.TLabel",
            background=palette["panel"],
            foreground=palette["muted"],
            font=("Segoe UI", body),
            anchor=anchor,
        )
        style.configure(
            "TButton",
            padding=(12, 8),
            background=palette["panel_alt"],
            foreground=palette["text"],
            font=("Segoe UI", body, "bold"),
        )
        style.map(
            "TButton",
            background=[("active", palette["accent"])],
            foreground=[("active", on_accent)],
        )
        style.configure(
            "Accent.TButton",
            background=palette["accent"],
            foreground=on_accent,
            padding=(14, 9),
        )
        style.map(
            "Accent.TButton",
            background=[("active", palette["accent_alt"])],
            foreground=[("active", on_accent_alt)],
        )
        style.configure("Danger.TButton", background=palette["danger"], foreground=on_danger)
        style.map(
            "Danger.TButton",
            background=[("active", palette["warning"])],
            foreground=[("active", on_warning)],
        )
        style.configure(
            "TEntry",
            fieldbackground=palette["panel_alt"],
            foreground=palette["text"],
            insertcolor=palette["text"],
            bordercolor=palette["border"],
            padding=7,
        )
        style.configure(
            "TCombobox",
            fieldbackground=palette["panel_alt"],
            foreground=palette["text"],
            arrowcolor=palette["accent"],
            padding=6,
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", palette["panel_alt"])],
            foreground=[("readonly", palette["text"])],
        )
        style.configure(
            "Treeview",
            background=palette["panel_alt"],
            fieldbackground=palette["panel_alt"],
            foreground=palette["text"],
            rowheight=max(26, round(30 * font_scale)),
            bordercolor=palette["border"],
        )
        style.configure(
            "Treeview.Heading",
            background=palette["panel"],
            foreground=palette["accent"],
            font=("Segoe UI", body, "bold"),
            padding=7,
        )
        style.map(
            "Treeview",
            background=[("selected", palette["accent"])],
            foreground=[("selected", on_accent)],
        )
        style.configure("Hidden.TNotebook", background=palette["bg"], borderwidth=0)
        style.configure("Hidden.TNotebook.Tab", padding=0, width=0, borderwidth=0)
        # The sidebar is the visible navigation. Removing the tab layout avoids
        # duplicate English tabs and keeps Hebrew/Spanish workspaces fully coherent.
        style.layout("Hidden.TNotebook.Tab", [])
        style.configure("Sidebar.TFrame", background=palette["panel"])
        style.configure("SidebarCard.TFrame", background=palette["panel_alt"])
        style.configure(
            "SidebarTitle.TLabel",
            background=palette["panel"],
            foreground=palette["text"],
            font=("Segoe UI", max(14, body + 5), "bold"),
            anchor=anchor,
        )
        style.configure(
            "SidebarSubtitle.TLabel",
            background=palette["panel"],
            foreground=palette["muted"],
            font=("Segoe UI", small),
            anchor=anchor,
        )
        style.configure(
            "SidebarMuted.TLabel",
            background=palette["panel_alt"],
            foreground=palette["muted"],
            font=("Segoe UI", small),
            anchor=anchor,
        )
        style.configure(
            "Nav.TButton",
            background=palette["panel"],
            foreground=palette["muted"],
            anchor=anchor,
            padding=(13, 10),
            borderwidth=0,
            font=("Segoe UI", body, "bold"),
        )
        style.map(
            "Nav.TButton",
            background=[("active", palette["panel_alt"])],
            foreground=[("active", palette["text"])],
        )
        style.configure(
            "NavActive.TButton",
            background=palette["panel_alt"],
            foreground=palette["accent"],
            anchor=anchor,
            padding=(13, 10),
            borderwidth=0,
            font=("Segoe UI", body, "bold"),
        )
        style.configure(
            "Horizontal.TProgressbar",
            troughcolor=palette["panel_alt"],
            background=palette["accent"],
            bordercolor=palette["panel_alt"],
        )
        style.configure("TCheckbutton", background=palette["panel_alt"], foreground=palette["text"])

    def _apply_window_icon(self) -> None:
        """Apply a retained, theme-aware NovaFit heart-pulse window icon."""
        try:
            self.app_icon = self.icon_factory.get("app", self.palette, 64, state="active")
            self.iconphoto(True, self.app_icon)
        except (ImportError, tk.TclError, ValueError) as exc:
            LOGGER.debug("Window icon could not be applied: %s", exc)

    def _build_menu(self) -> None:
        menu = tk.Menu(self)
        file_menu = tk.Menu(menu, tearoff=False)
        file_menu.add_command(
            label=self.t("export_json"), command=self._export_json_dialog, accelerator="Ctrl+E"
        )
        file_menu.add_command(label=self.t("export_csv"), command=self._export_csv_dialog)
        file_menu.add_command(label=self.t("export_report"), command=self._export_html_dialog)
        file_menu.add_command(
            label=self.t("create_complete_backup"),
            command=self._export_complete_backup_dialog,
        )
        file_menu.add_separator()
        file_menu.add_command(label=self.t("exit"), command=self._on_close, accelerator="Ctrl+Q")
        menu.add_cascade(label=self.t("file"), menu=file_menu)
        view_menu = tk.Menu(menu, tearoff=False)
        view_menu.add_command(label=self.t("cycle_theme"), command=self._toggle_theme, accelerator="Ctrl+T")
        view_menu.add_command(
            label=self.t("nav_motivation"),
            command=lambda: self._select_page("motivation"),
            accelerator="Ctrl+M",
        )
        view_menu.add_command(
            label=self.t("nav_recommendations"),
            command=lambda: self._select_page("recommendations"),
            accelerator="Ctrl+K",
        )
        view_menu.add_command(label=self.t("refresh"), command=self.refresh_all, accelerator="Ctrl+R")
        menu.add_cascade(label=self.t("view"), menu=view_menu)
        help_menu = tk.Menu(menu, tearoff=False)
        help_menu.add_command(label=self.t("about"), command=self._show_about, accelerator="F1")
        menu.add_cascade(label=self.t("help"), menu=help_menu)
        self.configure(menu=menu)

    def _build_layout(self) -> None:
        rtl = direction_for(self.language) == "rtl"
        root = ttk.Frame(self)
        root.pack(fill="both", expand=True)
        topbar = ttk.Frame(root, style="Topbar.TFrame", padding=(20, 11))
        topbar.pack(fill="x")
        title_block = ttk.Frame(topbar, style="Topbar.TFrame")
        title_block.pack(side="right" if rtl else "left", fill="x", expand=True)
        ttk.Label(title_block, text=self.t("app_title") + " 💙", style="Hero.TLabel").pack(
            anchor="e" if rtl else "w"
        )
        ttk.Label(title_block, text=self.t("app_subtitle"), style="Subtitle.TLabel").pack(
            anchor="e" if rtl else "w", pady=(2, 0)
        )
        selectors = ttk.Frame(topbar, style="Topbar.TFrame")
        selectors.pack(side="left" if rtl else "right")
        self._selector(
            selectors,
            self.t("user"),
            self.profile_choice_var,
            self._profile_selector_values(),
            self._profile_combo_changed,
            width=20,
        )
        self._selector(
            selectors,
            self.t("language"),
            self.language_choice_var,
            language_labels(),
            self._language_changed,
            width=10,
        )
        self._selector(
            selectors, self.t("theme"), self.theme_choice_var, theme_labels(), self._theme_changed, width=17
        )

        self.hero = UltimateHeroCanvas(
            root,
            self.palette,
            reduced_motion=self.settings.reduce_motion,
            profile_name=self.active_profile.display_name,
            language=self.language,
        )
        self.hero.pack(fill="x", padx=18, pady=(3, 8))

        workspace = ttk.Frame(root)
        workspace.pack(fill="both", expand=True)
        sidebar = ttk.Frame(workspace, style="Sidebar.TFrame", padding=(13, 14), width=246)
        sidebar.pack(side="right" if rtl else "left", fill="y")
        sidebar.pack_propagate(False)
        ttk.Label(sidebar, text="NOVA / FIT 4", style="SidebarTitle.TLabel").pack(anchor="e" if rtl else "w")
        ttk.Label(sidebar, text=f"ULTIMATE {__version__} · LOCAL-FIRST", style="SidebarSubtitle.TLabel").pack(
            anchor="e" if rtl else "w", pady=(1, 14)
        )

        self.nav_buttons: dict[str, ttk.Button] = {}
        navigation = (
            ("analytics", "dashboard", self.t("nav_dashboard")),
            ("motivation", "motivation", self.t("nav_motivation")),
            ("recommendations", "recommendations", self.t("nav_recommendations")),
            ("add", "add", self.t("nav_add")),
            ("entries", "records", self.t("nav_records")),
            ("profiles", "profiles", self.t("nav_profiles")),
            ("tools", "tools", self.t("nav_tools")),
        )
        self.nav_images: dict[str, object] = {}
        self.nav_icon_names: dict[str, str] = {}
        for key, icon_name, label in navigation:
            image = self.icon_factory.get(icon_name, self.palette, 28)
            self.nav_images[key] = image
            self.nav_icon_names[key] = icon_name
            button = ttk.Button(
                sidebar,
                text=label,
                image=image,
                compound="right" if rtl else "left",
                style="Nav.TButton",
                command=lambda page=key: self._select_page(page),
            )
            button.pack(fill="x", pady=2)
            self.nav_buttons[key] = button
        ttk.Separator(sidebar).pack(fill="x", pady=(15, 12))
        privacy = ttk.Frame(sidebar, style="SidebarCard.TFrame", padding=12)
        privacy.pack(fill="x")
        ttk.Label(privacy, text="🔒  " + self.t("privacy_title"), style="CardTitle.TLabel").pack(
            anchor="e" if rtl else "w"
        )
        ttk.Label(
            privacy,
            text=self.t("privacy_body"),
            style="SidebarMuted.TLabel",
            justify="right" if rtl else "left",
            wraplength=190,
        ).pack(anchor="e" if rtl else "w", pady=(7, 0))
        ttk.Frame(sidebar, style="Sidebar.TFrame").pack(fill="both", expand=True)
        ttk.Label(
            sidebar,
            text="Python · ttk · SQLite\nMatplotlib · Pillow · i18n\nProfiles · CLI · JSON/CSV",
            style="SidebarSubtitle.TLabel",
            justify="right" if rtl else "left",
        ).pack(anchor="e" if rtl else "w", pady=(10, 0))

        content = ttk.Frame(workspace, padding=(16, 4, 18, 10))
        content.pack(side="left" if rtl else "right", fill="both", expand=True)
        self.notebook = ttk.Notebook(content, style="Hidden.TNotebook")
        self.notebook.pack(fill="both", expand=True)
        self.dashboard_tab = ttk.Frame(self.notebook, style="Panel.TFrame", padding=0)
        self.motivation_tab = ttk.Frame(self.notebook, style="Panel.TFrame", padding=0)
        self.recommendations_tab = ttk.Frame(self.notebook, style="Panel.TFrame", padding=0)
        self.add_tab = ttk.Frame(self.notebook, style="Panel.TFrame", padding=18)
        self.entries_tab = ttk.Frame(self.notebook, style="Panel.TFrame", padding=18)
        self.profiles_tab = ttk.Frame(self.notebook, style="Panel.TFrame", padding=0)
        self.tools_tab = ttk.Frame(self.notebook, style="Panel.TFrame", padding=18)
        tabs = (
            (self.dashboard_tab, self.t("tab_analytics")),
            (self.motivation_tab, self.t("tab_motivation")),
            (self.recommendations_tab, self.t("tab_coach")),
            (self.add_tab, self.t("tab_add")),
            (self.entries_tab, self.t("tab_records")),
            (self.profiles_tab, self.t("tab_profiles")),
            (self.tools_tab, self.t("tab_tools")),
        )
        for frame, label in tabs:
            self.notebook.add(frame, text=label)
        self.page_frames = {
            "analytics": self.dashboard_tab,
            "motivation": self.motivation_tab,
            "recommendations": self.recommendations_tab,
            "add": self.add_tab,
            "entries": self.entries_tab,
            "profiles": self.profiles_tab,
            "tools": self.tools_tab,
        }
        self._build_dashboard_tab()
        self._build_motivation_tab()
        self._build_recommendations_tab()
        self._build_add_tab()
        self._build_entries_tab()
        self._build_profiles_tab()
        self._build_tools_tab()
        ttk.Label(
            content, textvariable=self.status_var, style="Subtitle.TLabel", anchor="e" if rtl else "w"
        ).pack(fill="x", pady=(7, 0))
        self.current_page = getattr(self, "current_page", "analytics")
        self._select_page(self.current_page if self.current_page in self.page_frames else "analytics")

    def _selector(
        self,
        parent: ttk.Frame,
        label: str,
        variable: tk.StringVar,
        values: tuple[str, ...],
        callback: object,
        *,
        width: int,
    ) -> None:
        rtl = direction_for(self.language) == "rtl"
        block = ttk.Frame(parent, style="Topbar.TFrame")
        block.pack(side="right" if rtl else "left", padx=5)
        ttk.Label(block, text=label, style="Subtitle.TLabel").pack(anchor="e" if rtl else "w")
        combo = ttk.Combobox(
            block,
            textvariable=variable,
            values=values,
            state="readonly",
            width=width,
            justify="right" if rtl else "left",
        )
        combo.pack()
        combo.bind("<<ComboboxSelected>>", callback, add="+")

    def _select_page(self, page_key: str) -> None:
        frame = self.page_frames[page_key]
        self.notebook.select(frame)
        self.current_page = page_key
        for key, button in self.nav_buttons.items():
            is_active = key == page_key
            image = self.icon_factory.get(
                self.nav_icon_names[key],
                self.palette,
                28,
                state="active" if is_active else "default",
            )
            self.nav_images[key] = image
            button.configure(
                style="NavActive.TButton" if is_active else "Nav.TButton",
                image=image,
            )
        self._update_motion_activity()

    def _update_motion_activity(self) -> None:
        """Run decorative motion only for the currently visible workspace."""
        if hasattr(self, "hero"):
            self.hero.set_active(True)
        if hasattr(self, "motivation_panel"):
            active = self.current_page == "motivation"
            self.motivation_panel.galaxy.set_active(active)
            self.motivation_panel.focus_canvas.set_active(active)
        if hasattr(self, "recommendations_panel"):
            self.recommendations_panel.orbit.set_active(self.current_page == "recommendations")

    def _animate_window_entry(self) -> None:
        """Reveal the window with a short, reduced-motion-aware fade."""
        if self.settings.reduce_motion:
            return
        try:
            self.attributes("-alpha", 0.88)
        except tk.TclError:
            return

        def advance(step: int = 0) -> None:
            if self._closing:
                return
            alpha = min(1.0, 0.88 + (step * 0.02))
            try:
                self.attributes("-alpha", alpha)
            except tk.TclError:
                return
            if alpha < 1.0:
                self.after(24, advance, step + 1)

        advance()

    def _run_background_job(
        self,
        status: str,
        operation: Callable[[], JobResult],
        on_success: Callable[[JobResult], None],
        *,
        error_title: str,
    ) -> None:
        """Execute blocking I/O away from Tk's event loop and poll safely."""
        if self._closing:
            return
        self._set_status(status)
        future: Future[JobResult] = self._executor.submit(operation)
        self._background_jobs.add(future)

        def poll() -> None:
            if self._closing:
                return
            if not future.done():
                self.after(60, poll)
                return
            self._background_jobs.discard(future)
            try:
                result = future.result()
            except Exception as exc:
                self._show_error(error_title, exc)
            else:
                on_success(result)

        self.after(60, poll)

    def _build_dashboard_tab(self) -> None:
        self.dashboard_panel = DashboardPanel(
            self.dashboard_tab, self.settings, lambda: self.palette, self._set_status, self._show_error
        )
        self.dashboard_panel.pack(fill="both", expand=True)

    def _build_motivation_tab(self) -> None:
        self.motivation_panel = MotivationCenterPanel(
            self.motivation_tab,
            self.settings,
            lambda: self.palette,
            self._save_motivation_preferences,
            self._set_status,
        )
        self.motivation_panel.pack(fill="both", expand=True, padx=4, pady=4)

    def _build_recommendations_tab(self) -> None:
        self.recommendations_panel = RecommendationsPanel(
            self.recommendations_tab,
            self.settings,
            lambda: self.palette,
            lambda: self.language,
            self._set_status,
        )
        self.recommendations_panel.pack(fill="both", expand=True)

    def _build_profiles_tab(self) -> None:
        self.profile_panel = ProfileManagerPanel(
            self.profiles_tab,
            self.database,
            lambda: self.palette,
            lambda: self.language,
            self._profile_activated,
            self._set_status,
            self._show_error,
        )
        self.profile_panel.pack(fill="both", expand=True)

    def _build_add_tab(self) -> None:
        rtl = direction_for(self.language) == "rtl"
        anchor = "e" if rtl else "w"
        self.add_tab.columnconfigure(0, weight=2)
        self.add_tab.columnconfigure(1, weight=1)
        form = ttk.Frame(self.add_tab, style="Panel.TFrame")
        form.grid(row=0, column=0 if not rtl else 1, sticky="nsew", padx=(0, 28) if not rtl else (28, 0))
        preview = ttk.Frame(self.add_tab, style="Card.TFrame", padding=22)
        preview.grid(row=0, column=1 if not rtl else 0, sticky="nsew")
        ttk.Label(form, text=self.t("nav_add"), style="Panel.TLabel", font=("Segoe UI", 17, "bold")).grid(
            row=0, column=0, columnspan=2, sticky=anchor, pady=(0, 14)
        )
        fields = (
            (self.t("date") + " (YYYY-MM-DD)", self.entry_date_var),
            (self.t("steps"), self.steps_var),
            (self.t("water"), self.water_var),
            (self.t("calories"), self.calories_var),
        )
        for row_index, (label, variable) in enumerate(fields, start=1):
            ttk.Label(form, text=label, style="Panel.TLabel").grid(
                row=row_index, column=0, sticky=anchor, pady=7
            )
            ttk.Entry(form, textvariable=variable, width=34, justify="right" if rtl else "left").grid(
                row=row_index, column=1, sticky="ew", padx=(15, 0), pady=7
            )
        form.columnconfigure(1, weight=1)
        ttk.Label(form, text=self.t("mood"), style="Panel.TLabel").grid(
            row=5, column=0, sticky=anchor, pady=7
        )
        ttk.Combobox(
            form,
            textvariable=self.mood_var,
            values=tuple(label for _canonical, label in self._mood_options()),
            state="readonly",
            justify="right" if rtl else "left",
        ).grid(row=5, column=1, sticky="ew", padx=(15, 0), pady=7)
        ttk.Label(form, text=self.t("note"), style="Panel.TLabel").grid(
            row=6, column=0, sticky=anchor, pady=7
        )
        ttk.Entry(form, textvariable=self.note_var, justify="right" if rtl else "left").grid(
            row=6, column=1, sticky="ew", padx=(15, 0), pady=7
        )
        buttons = ttk.Frame(form, style="Panel.TFrame")
        buttons.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(18, 0))
        ttk.Button(
            buttons, text=self.t("save_record"), style="Accent.TButton", command=self._save_entry
        ).pack(side="right" if rtl else "left")
        ttk.Button(buttons, text=self.t("clear_form"), command=self._clear_entry_form).pack(
            side="right" if rtl else "left", padx=10
        )
        ttk.Button(buttons, text=self.t("edit"), command=self._load_selected_into_form).pack(
            side="right" if rtl else "left"
        )
        ttk.Label(preview, text="🔐  " + self.t("privacy_title"), style="CardValue.TLabel").pack(
            anchor=anchor
        )
        ttk.Label(
            preview,
            text=self.t("record_rules", profile=self.active_profile.display_name),
            style="CardTitle.TLabel",
            justify="right" if rtl else "left",
            wraplength=340,
        ).pack(anchor=anchor, pady=(16, 0))

    def _build_entries_tab(self) -> None:
        rtl = direction_for(self.language) == "rtl"
        filters = ttk.Frame(self.entries_tab, style="Panel.TFrame")
        filters.pack(fill="x", pady=(0, 12))
        ttk.Label(
            filters,
            text=self.t("date") + " — " + self.t("from_date"),
            style="Panel.TLabel",
        ).pack(side="right" if rtl else "left")
        ttk.Entry(filters, textvariable=self.search_start_var, width=13).pack(
            side="right" if rtl else "left", padx=7
        )
        ttk.Label(filters, text=self.t("to_date"), style="Panel.TLabel").pack(side="right" if rtl else "left")
        ttk.Entry(filters, textvariable=self.search_end_var, width=13).pack(
            side="right" if rtl else "left", padx=7
        )
        ttk.Button(filters, text=self.t("search"), command=self._apply_filter).pack(
            side="right" if rtl else "left", padx=5
        )
        ttk.Button(filters, text=self.t("show_all"), command=self._show_all_entries).pack(
            side="right" if rtl else "left", padx=5
        )
        ttk.Button(
            filters, text=self.t("delete"), style="Danger.TButton", command=self._delete_selected
        ).pack(side="left" if rtl else "right")
        table_frame = ttk.Frame(self.entries_tab, style="Panel.TFrame")
        table_frame.pack(fill="both", expand=True)
        columns = ("date", "steps", "water", "calories", "mood", "note")
        self.entries_tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        headings = {
            "date": self.t("date"),
            "steps": self.t("steps"),
            "water": self.t("water"),
            "calories": self.t("calories"),
            "mood": self.t("mood"),
            "note": self.t("note"),
        }
        widths = {"date": 110, "steps": 105, "water": 90, "calories": 100, "mood": 130, "note": 430}
        for column in columns:
            self.entries_tree.heading(column, text=headings[column])
            self.entries_tree.column(
                column, width=widths[column], anchor="center" if column != "note" else ("e" if rtl else "w")
            )
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.entries_tree.yview)
        self.entries_tree.configure(yscrollcommand=scrollbar.set)
        self.entries_tree.pack(side="right" if rtl else "left", fill="both", expand=True)
        scrollbar.pack(side="left" if rtl else "right", fill="y")
        self.entries_tree.bind("<Double-1>", lambda _event: self._load_selected_into_form())

    def _build_tools_tab(self) -> None:
        rtl = direction_for(self.language) == "rtl"
        primary_side = "right" if rtl else "left"
        secondary_side = "left" if rtl else "right"
        anchor = "e" if rtl else "w"
        tools = ttk.Frame(self.tools_tab, style="Panel.TFrame")
        tools.pack(fill="both", expand=True)
        tools.columnconfigure(0, weight=1)
        tools.columnconfigure(1, weight=1)
        weather_card = self._tool_card(tools, self.t("weather"), 0, 0)
        weather_row = ttk.Frame(weather_card, style="Card.TFrame")
        weather_row.pack(fill="x", pady=(10, 8))
        ttk.Combobox(
            weather_row,
            textvariable=self.weather_city_var,
            values=("beersheba", "tel aviv", "jerusalem", "haifa", "eilat", "ashdod", "netanya"),
            justify="right" if rtl else "left",
        ).pack(side=primary_side, fill="x", expand=True)
        ttk.Button(weather_row, text=self.t("check_weather"), command=self._lookup_weather).pack(
            side=secondary_side,
            padx=(0, 8) if rtl else (8, 0),
        )
        ttk.Label(
            weather_card,
            textvariable=self.weather_result_var,
            style="CardTitle.TLabel",
            wraplength=450,
            justify="right" if rtl else "left",
        ).pack(anchor=anchor)
        portability = self._tool_card(tools, self.t("backup_reports"), 0, 1)
        for label, command in (
            (self.t("create_complete_backup"), self._export_complete_backup_dialog),
            (self.t("export_json"), self._export_json_dialog),
            (self.t("import_json"), self._import_json_dialog),
            (self.t("export_csv"), self._export_csv_dialog),
            (self.t("import_csv"), self._import_csv_dialog),
            (self.t("export_report"), self._export_html_dialog),
        ):
            ttk.Button(portability, text=label, command=command).pack(fill="x", pady=4)
        data_card = self._tool_card(tools, self.t("data_management"), 1, 0)
        ttk.Button(data_card, text=self.t("add_sample"), command=self._add_sample_data).pack(fill="x", pady=4)
        ttk.Button(data_card, text=self.t("generate_demo"), command=self._generate_demo_data).pack(
            fill="x", pady=4
        )
        ttk.Button(
            data_card,
            text=self.t("export_analytics_png"),
            command=self.dashboard_panel.export_png,
        ).pack(fill="x", pady=4)
        ttk.Button(
            data_card, text=self.t("clear_data"), style="Danger.TButton", command=self._clear_all_data
        ).pack(fill="x", pady=(14, 4))
        settings_card = self._tool_card(tools, self.t("goals"), 1, 1)
        for label, variable in (
            (self.t("step_goal"), self.step_goal_var),
            (self.t("water_goal"), self.water_goal_var),
            (self.t("calorie_reference"), self.calorie_goal_var),
            (self.t("chart_range") + " (7–365)", self.chart_days_var),
            (self.t("ui_scale"), self.ui_scale_var),
        ):
            row = ttk.Frame(settings_card, style="Card.TFrame")
            row.pack(fill="x", pady=4)
            ttk.Label(row, text=label, style="CardTitle.TLabel").pack(side=primary_side)
            ttk.Entry(row, textvariable=variable, width=12, justify="right" if rtl else "left").pack(
                side=secondary_side
            )
        for label, variable, values in (
            (self.t("theme"), self.theme_choice_var, theme_labels()),
            (self.t("language"), self.language_choice_var, language_labels()),
            (
                self.t("chart_view"),
                self.chart_view_var,
                tuple(label for _key, label in self._chart_view_options()),
            ),
        ):
            row = ttk.Frame(settings_card, style="Card.TFrame")
            row.pack(fill="x", pady=4)
            ttk.Label(row, text=label, style="CardTitle.TLabel").pack(side=primary_side)
            ttk.Combobox(
                row,
                textvariable=variable,
                values=values,
                state="readonly",
                width=20,
                justify="right" if rtl else "left",
            ).pack(side=secondary_side)
        ttk.Checkbutton(settings_card, text=self.t("reduced_motion"), variable=self.reduce_motion_var).pack(
            anchor=anchor, pady=(8, 2)
        )
        ttk.Button(
            settings_card,
            text=self.t("save_preferences"),
            style="Accent.TButton",
            command=self._save_preferences,
        ).pack(fill="x", pady=(12, 4))
        ttk.Label(
            settings_card,
            text=self.t("config_path", path=CONFIG_PATH),
            style="CardTitle.TLabel",
            wraplength=450,
            justify="right" if rtl else "left",
        ).pack(anchor=anchor, pady=(8, 0))

    def _tool_card(self, parent: ttk.Frame, title: str, row: int, column: int) -> ttk.Frame:
        card = ttk.Frame(parent, style="Card.TFrame", padding=18)
        card.grid(row=row, column=column, sticky="nsew", padx=7, pady=7)
        ttk.Label(card, text=title, style="CardValue.TLabel").pack(
            anchor="e" if direction_for(self.language) == "rtl" else "w"
        )
        return card

    def _mood_options(self) -> tuple[tuple[str, str], ...]:
        keys = ("focused", "calm", "energetic", "happy", "motivated", "tired", "stressed")
        return tuple((key.title(), self.t(f"mood_{key}")) for key in keys)

    def _canonical_mood(self, value: str) -> str:
        normalized = value.strip().casefold()
        for canonical, _label in self._mood_options():
            if normalized == canonical.casefold():
                return canonical
            key = f"mood_{canonical.lower()}"
            if any(normalized == tr(language, key).casefold() for language in ("en", "es", "he")):
                return canonical
        return value.strip()

    def _localized_mood(self, value: str | None) -> str:
        if not value:
            return ""
        canonical = self._canonical_mood(value)
        key = f"mood_{canonical.lower()}"
        try:
            return self.t(key)
        except KeyError:
            return value

    def _chart_view_options(self) -> tuple[tuple[str, str], ...]:
        return tuple((key, self.t(f"chart_view_{key}")) for key in CHART_VIEWS)

    def _canonical_chart_view(self, value: str) -> str:
        normalized = value.strip().casefold()
        for key, english_label in CHART_VIEWS.items():
            if normalized in {key.casefold(), english_label.casefold()}:
                return key
            translation_key = f"chart_view_{key}"
            if any(normalized == tr(language, translation_key).casefold() for language in ("en", "es", "he")):
                return key
        raise ValueError(f"Unsupported chart view: {value}")

    def _localized_chart_view(self, value: str) -> str:
        key = value if value in CHART_VIEWS else self._canonical_chart_view(value)
        return self.t(f"chart_view_{key}")

    def _bind_shortcuts(self) -> None:
        self.bind("<Control-s>", lambda _event: self._save_entry())
        self.bind("<Control-r>", lambda _event: self.refresh_all())
        self.bind("<Control-e>", lambda _event: self._export_json_dialog())
        self.bind("<Control-b>", lambda _event: self._export_complete_backup_dialog())
        self.bind("<Control-t>", lambda _event: self._toggle_theme())
        self.bind("<Control-m>", lambda _event: self._select_page("motivation"))
        self.bind("<Control-k>", lambda _event: self._select_page("recommendations"))
        self.bind("<Control-q>", lambda _event: self._on_close())
        self.bind("<F1>", lambda _event: self._show_about())

    def refresh_all(self) -> None:
        try:
            entries = self.database.list(limit=None)
            self._populate_tree(entries)
            stats = calculate_dashboard(entries, self.settings)
            self.dashboard_panel.refresh(entries, stats, self.settings)
            self.motivation_panel.refresh(entries, stats, self.settings)
            self.recommendations_panel.refresh(entries, self.settings, self.active_profile)
            self.profile_panel.refresh()
            self._refresh_profile_selector()
            self.hero.set_profile_name(self.active_profile.display_name)
            self._set_status(
                self.t(
                    "records_status",
                    profile=self.active_profile.display_name,
                    count=len(entries),
                    path=self.database.path,
                )
            )
        except Exception as exc:
            LOGGER.exception("GUI refresh failed")
            self._show_error(self.t("refresh_failed"), exc)

    def _populate_tree(self, entries: list[HealthEntry]) -> None:
        self.entries_tree.delete(*self.entries_tree.get_children())
        for entry in entries:
            self.entries_tree.insert(
                "",
                "end",
                values=(
                    entry.entry_date.isoformat(),
                    f"{entry.steps:,}",
                    f"{entry.water_l:.2f}",
                    "" if entry.calories is None else f"{entry.calories:,}",
                    self._localized_mood(entry.mood),
                    entry.note or "",
                ),
            )

    def _save_entry(self) -> None:
        try:
            entry = HealthEntry.build(
                self.entry_date_var.get(),
                self.steps_var.get(),
                self.water_var.get(),
                self.calories_var.get(),
                self._canonical_mood(self.mood_var.get()),
                self.note_var.get(),
            )
            self.database.upsert(entry)
            self._set_status(
                f"{self.t('success_saved')}: {entry.entry_date} · {self.active_profile.display_name} ✅"
            )
            self.refresh_all()
        except Exception as exc:
            self._show_error(self.t("save_record_error"), exc)

    def _clear_entry_form(self) -> None:
        self.entry_date_var.set(date.today().isoformat())
        self.steps_var.set("")
        self.water_var.set("")
        self.calories_var.set("")
        self.mood_var.set(self.t("mood_focused"))
        self.note_var.set("")

    def _selected_date(self) -> str | None:
        selected = self.entries_tree.selection()
        if not selected:
            return None
        return str(self.entries_tree.item(selected[0], "values")[0])

    def _load_selected_into_form(self) -> None:
        selected_date = self._selected_date()
        if not selected_date:
            self._set_status(self.t("select_record"))
            return
        entry = self.database.get(selected_date)
        if entry is None:
            self._set_status(self.t("record_missing"))
            return
        self.entry_date_var.set(entry.entry_date.isoformat())
        self.steps_var.set(str(entry.steps))
        self.water_var.set(str(entry.water_l))
        self.calories_var.set("" if entry.calories is None else str(entry.calories))
        self.mood_var.set(self._localized_mood(entry.mood))
        self.note_var.set(entry.note or "")
        self._select_page("add")

    def _delete_selected(self) -> None:
        selected_date = self._selected_date()
        if not selected_date:
            self._set_status(self.t("select_record"))
            return
        if not messagebox.askyesno(
            self.t("delete_record"),
            self.t(
                "delete_record_confirm",
                date=selected_date,
                profile=self.active_profile.display_name,
            ),
            icon="warning",
        ):
            return
        try:
            self.database.delete(selected_date)
            self._set_status(self.t("deleted_record", date=selected_date))
            self.refresh_all()
        except Exception as exc:
            self._show_error(self.t("delete_failed"), exc)

    def _apply_filter(self) -> None:
        try:
            self._populate_tree(self.database.search(self.search_start_var.get(), self.search_end_var.get()))
            self._set_status(self.t("filter_applied"))
        except Exception as exc:
            self._show_error(self.t("filter_failed"), exc)

    def _show_all_entries(self) -> None:
        self._populate_tree(self.database.list(limit=None))
        self._set_status(self.t("showing_all_records"))

    def _lookup_weather(self) -> None:
        city = self.weather_city_var.get()

        def completed(formatted: str) -> None:
            self.weather_result_var.set(formatted)
            self._set_status(self.t("weather_updated"))

        self._run_background_job(
            self.t("weather_loading"),
            lambda: format_weather(get_weather(city)),
            completed,
            error_title=self.t("weather_lookup_failed"),
        )

    def _export_json_dialog(self) -> None:
        slug = self.active_profile.display_name.lower().replace(" ", "-")
        path = filedialog.asksaveasfilename(
            title=self.t("export_json"),
            initialdir=str(EXPORT_PATH.parent),
            initialfile=f"novafit-{slug}.json",
            defaultextension=".json",
            filetypes=[("JSON", "*.json")],
        )
        if not path:
            return
        self._run_background_job(
            self.t("exporting_json"),
            lambda: export_json(self.database, Path(path)),
            lambda count: self._set_status(self.t("exported_records", count=count, path=path)),
            error_title=self.t("json_export_failed"),
        )

    def _import_json_dialog(self) -> None:
        path = filedialog.askopenfilename(title=self.t("import_json"), filetypes=[("JSON", "*.json")])
        if not path:
            return

        def completed(result: ImportResult) -> None:
            self._set_status(self.t("imported_records", imported=result.imported, invalid=result.invalid))
            self.refresh_all()

        self._run_background_job(
            self.t("importing_json"),
            lambda: import_json(self.database, Path(path), strategy="replace"),
            completed,
            error_title=self.t("json_import_failed"),
        )

    def _export_csv_dialog(self) -> None:
        slug = self.active_profile.display_name.lower().replace(" ", "-")
        path = filedialog.asksaveasfilename(
            title=self.t("export_csv"),
            initialdir=str(CSV_EXPORT_PATH.parent),
            initialfile=f"novafit-{slug}.csv",
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
        )
        if not path:
            return
        self._run_background_job(
            self.t("exporting_csv"),
            lambda: export_csv(self.database, Path(path)),
            lambda count: self._set_status(self.t("exported_records", count=count, path=path)),
            error_title=self.t("csv_export_failed"),
        )

    def _import_csv_dialog(self) -> None:
        path = filedialog.askopenfilename(title=self.t("import_csv"), filetypes=[("CSV", "*.csv")])
        if not path:
            return

        def completed(result: ImportResult) -> None:
            self._set_status(self.t("imported_records", imported=result.imported, invalid=result.invalid))
            self.refresh_all()

        self._run_background_job(
            self.t("importing_csv"),
            lambda: import_csv(self.database, Path(path), strategy="replace"),
            completed,
            error_title=self.t("csv_import_failed"),
        )

    def _export_html_dialog(self) -> None:
        slug = self.active_profile.display_name.lower().replace(" ", "-")
        path = filedialog.asksaveasfilename(
            title=self.t("export_report"),
            initialdir=str(EXPORT_PATH.parent),
            initialfile=f"novafit-report-{slug}.html",
            defaultextension=".html",
            filetypes=[("HTML", "*.html")],
        )
        if not path:
            return
        try:
            days, view = self.dashboard_panel.selected_preferences()
            entries = self.database.list(limit=None)
            settings = replace(self.settings)
        except Exception as exc:
            self._show_error(self.t("html_report_failed"), exc)
            return
        self._run_background_job(
            self.t("rendering_report"),
            lambda: export_html_report(
                entries,
                settings,
                Path(path),
                days=days,
                theme=settings.theme,
                view=view,
            ),
            lambda destination: self._set_status(self.t("visual_report_saved", path=destination)),
            error_title=self.t("html_report_failed"),
        )

    def _export_complete_backup_dialog(self) -> None:
        path = filedialog.asksaveasfilename(
            title=self.t("complete_backup_title"),
            initialdir=str(BACKUP_DIR.parent),
            initialfile=f"novafit-complete-{date.today():%Y%m%d}.zip",
            defaultextension=".zip",
            filetypes=[(self.t("zip_backup"), "*.zip")],
        )
        if not path:
            return
        self._run_background_job(
            self.t("creating_complete_backup"),
            lambda: create_complete_backup(self.database, Path(path)),
            lambda destination: self._set_status(self.t("complete_backup_saved", path=destination)),
            error_title=self.t("complete_backup_failed"),
        )

    def _add_sample_data(self) -> None:
        try:
            count = initialize_sample_data(self.database)
            self._set_status(
                self.t(
                    "starter_records_added",
                    count=count,
                    profile=self.active_profile.display_name,
                )
            )
            self.refresh_all()
        except Exception as exc:
            self._show_error(self.t("sample_data_failed"), exc)

    def _generate_demo_data(self) -> None:
        if not messagebox.askyesno(
            self.t("generate_demo_title"),
            self.t("generate_demo_confirm", profile=self.active_profile.display_name),
        ):
            return

        def completed(count: int) -> None:
            self._set_status(self.t("demo_records_generated", count=count))
            self.refresh_all()

        self._run_background_job(
            self.t("creating_demo"),
            lambda: generate_demo_data(self.database, 30),
            completed,
            error_title=self.t("demo_generation_failed"),
        )

    def _clear_all_data(self) -> None:
        if not messagebox.askyesno(
            self.t("clear_profile_data"),
            self.t("clear_profile_confirm", profile=self.active_profile.display_name),
            icon="warning",
        ):
            return
        if not messagebox.askyesno(
            self.t("final_confirmation"),
            self.t("cannot_undo"),
            icon="warning",
        ):
            return
        try:
            count = self.database.clear()
            self._set_status(self.t("records_deleted", count=count))
            self.refresh_all()
        except Exception as exc:
            self._show_error(self.t("clear_operation_failed"), exc)

    def _save_preferences(self) -> None:
        try:
            updated = AppSettings(
                step_goal=int(self.step_goal_var.get()),
                water_goal_l=float(self.water_goal_var.get()),
                calorie_goal=int(self.calorie_goal_var.get()),
                default_city=self.weather_city_var.get().strip().lower(),
                theme=normalize_theme_id(self.theme_choice_var.get()),
                show_achievements=self.settings.show_achievements,
                chart_days=int(self.chart_days_var.get()),
                chart_view=self._canonical_chart_view(self.chart_view_var.get()),
                reduce_motion=self.reduce_motion_var.get(),
                personal_why=self.settings.personal_why,
                weekly_focus=self.settings.weekly_focus,
                reward_note=self.settings.reward_note,
                language=normalize_language(self.language_choice_var.get()),
                active_profile_id=self.active_profile.profile_id or 1,
                ui_scale=float(self.ui_scale_var.get()),
            ).validate()
            old_theme, old_language, old_scale = (
                self.settings.theme,
                self.settings.language,
                self.settings.ui_scale,
            )
            self.settings = updated
            self._persist_profile_preferences()
            save_settings(updated)
            self.theme_var.set(updated.theme)
            self.theme_choice_var.set(theme_label(updated.theme))
            self.language_choice_var.set(language_label(updated.language))
            if (old_theme, old_language, old_scale) != (updated.theme, updated.language, updated.ui_scale):
                self._rebuild_interface()
            else:
                self._apply_visual_theme()
                self.refresh_all()
            self._set_status(self.t("settings_saved") + " ✅")
        except Exception as exc:
            self._show_error(self.t("preferences_save_error"), exc)

    def _save_motivation_preferences(self, personal_why: str, weekly_focus: str, reward_note: str) -> None:
        try:
            self.settings.personal_why = personal_why
            self.settings.weekly_focus = weekly_focus
            self.settings.reward_note = reward_note
            self.settings.validate()
            save_settings(self.settings)
            self._set_status(self.t("motivation_saved"))
            self.refresh_all()
        except Exception as exc:
            self._show_error(self.t("motivation_save_error"), exc)

    def _profile_selector_values(self) -> tuple[str, ...]:
        return tuple(
            f"{profile.profile_id} · {profile.display_name}" for profile in self.database.list_profiles()
        )

    def _refresh_profile_selector(self) -> None:
        values = self._profile_selector_values()
        current = f"{self.active_profile.profile_id} · {self.active_profile.display_name}"
        self.profile_choice_var.set(current)
        # Find the topbar combobox through its variable and update available values.
        for widget in self.winfo_children():
            self._update_combobox_values(widget, self.profile_choice_var, values)

    def _update_combobox_values(
        self, widget: tk.Misc, variable: tk.StringVar, values: tuple[str, ...]
    ) -> None:
        for child in widget.winfo_children():
            if isinstance(child, ttk.Combobox) and str(child.cget("textvariable")) == str(variable):
                child.configure(values=values)
            self._update_combobox_values(child, variable, values)

    def _profile_combo_changed(self, _event: tk.Event[tk.Misc] | None = None) -> None:
        raw = self.profile_choice_var.get().split("·", maxsplit=1)[0].strip()
        try:
            profile = self.database.set_active_profile(int(raw))
            self._profile_activated(profile)
        except (ValueError, sqlite3.Error) as exc:
            self._show_error(self.t("profile_switch_error"), exc)

    def _profile_activated(self, profile: UserProfile) -> None:
        self.active_profile = profile
        self._sync_settings_from_profile(profile)
        self.theme_var.set(profile.theme)
        self.theme_choice_var.set(theme_label(profile.theme))
        self.language_choice_var.set(language_label(profile.language))
        self._rebuild_interface()
        self._set_status(f"{self.t('profile_switched')}: {profile.display_name} ✅")

    def _language_changed(self, _event: tk.Event[tk.Misc] | None = None) -> None:
        try:
            self.settings.language = normalize_language(self.language_choice_var.get())
            self._persist_profile_preferences()
            save_settings(self.settings)
            self._rebuild_interface()
        except Exception as exc:
            self._show_error(self.t("language_change_error"), exc)

    def _theme_changed(self, _event: tk.Event[tk.Misc] | None = None) -> None:
        try:
            self.settings.theme = normalize_theme_id(self.theme_choice_var.get())
            self.theme_var.set(self.settings.theme)
            self._persist_profile_preferences()
            save_settings(self.settings)
            self._apply_visual_theme()
            self.refresh_all()
        except Exception as exc:
            self._show_error(self.t("theme_change_error"), exc)

    def _toggle_theme(self) -> None:
        self.settings.theme = next_theme(self.settings.theme)
        self.theme_var.set(self.settings.theme)
        self.theme_choice_var.set(theme_label(self.settings.theme))
        try:
            self._persist_profile_preferences()
            save_settings(self.settings)
        except Exception as exc:
            LOGGER.warning("Theme preference was not persisted: %s", exc)
        self._apply_visual_theme()
        self.refresh_all()
        self._set_status(self.t("theme_label_status", theme=theme_label(self.settings.theme)))

    def _persist_profile_preferences(self) -> None:
        updated = UserProfile.build(
            self.active_profile.display_name,
            profile_id=self.active_profile.profile_id,
            avatar=self.active_profile.avatar,
            language=self.settings.language,
            theme=self.settings.theme,
            step_goal=self.settings.step_goal,
            water_goal_l=self.settings.water_goal_l,
            calorie_goal=self.settings.calorie_goal,
            activity_level=self.active_profile.activity_level,
            sport_focus=self.active_profile.sport_focus,
        )
        self.active_profile = self.database.update_profile(updated)
        self.settings.active_profile_id = self.active_profile.profile_id or 1

    def _sync_settings_from_profile(self, profile: UserProfile, *, persist: bool = True) -> None:
        self.settings.step_goal = profile.step_goal
        self.settings.water_goal_l = profile.water_goal_l
        self.settings.calorie_goal = profile.calorie_goal
        self.settings.theme = profile.theme
        self.settings.language = profile.language
        self.settings.active_profile_id = profile.profile_id or 1
        if persist:
            save_settings(self.settings)
        if hasattr(self, "step_goal_var"):
            self.step_goal_var.set(str(profile.step_goal))
            self.water_goal_var.set(str(profile.water_goal_l))
            self.calorie_goal_var.set(str(profile.calorie_goal))

    def _apply_visual_theme(self) -> None:
        self._configure_style()
        self.icon_factory.clear()
        self._apply_window_icon()
        self.hero.set_palette(self.palette)
        self.hero.set_reduced_motion(self.settings.reduce_motion)
        self.hero.set_language(self.language)
        self.dashboard_panel.settings = self.settings
        self.dashboard_panel.apply_theme()
        self.motivation_panel.settings = self.settings
        self.motivation_panel.apply_theme()
        self.motivation_panel.galaxy.set_language(self.language)
        self.motivation_panel.focus_canvas.set_language(self.language)
        self.recommendations_panel.settings = self.settings
        self.recommendations_panel.apply_theme()
        self.recommendations_panel.orbit.set_language(self.language)
        self.profile_panel.apply_theme()
        self._select_page(self.current_page)
        self.update_idletasks()

    def _rebuild_interface(self) -> None:
        current_page = getattr(self, "current_page", "analytics")
        current_mood = self._canonical_mood(self.mood_var.get())
        current_chart_view = self._canonical_chart_view(self.chart_view_var.get())
        for child in self.winfo_children():
            child.destroy()
        self.tk.call("tk", "scaling", self.settings.ui_scale)
        self.title(f"{APP_NAME} {__version__} — {self.t('app_subtitle')}")
        self.status_var.set(self.t("ready") + " 💙")
        self.theme_var.set(self.settings.theme)
        self.theme_choice_var.set(theme_label(self.settings.theme))
        self.language_choice_var.set(language_label(self.settings.language))
        self.mood_var.set(self._localized_mood(current_mood))
        self.chart_view_var.set(self._localized_chart_view(current_chart_view))
        self._configure_style()
        self._build_menu()
        self.current_page = current_page
        self._build_layout()
        self.refresh_all()
        self.after(300, self.dashboard_panel.finalize_layout)

    def _show_about(self) -> None:
        messagebox.showinfo(
            self.t("about"),
            self.t("about_body", version=__version__),
        )

    def _show_error(self, title: str, error: Exception) -> None:
        LOGGER.warning("%s: %s", title, error)
        messagebox.showerror(title, f"{error}\n\n{self.t('error_next_step')}")
        self._set_status(f"{title}: {error}")

    def _set_status(self, message: str) -> None:
        self.status_var.set(message)
        if self._status_after_id is not None:
            try:
                self.after_cancel(self._status_after_id)
            except tk.TclError:
                pass
        self._status_after_id = self.after(12_000, lambda: self.status_var.set(self.t("ready") + " 💙"))

    def _on_close(self) -> None:
        self._closing = True
        try:
            save_settings(self.settings)
        except Exception as exc:
            LOGGER.warning("Settings were not saved during close: %s", exc)
        for future in tuple(self._background_jobs):
            future.cancel()
        self._executor.shutdown(wait=False, cancel_futures=True)
        self.destroy()


def run_gui(database_path: Path = DB_PATH) -> None:
    """Launch the NovaFit desktop application.

    Args:
        database_path: SQLite file to use.

    Returns:
        None after the Tkinter event loop exits.

    Example:
        >>> run_gui(Path('data/novafit.db'))  # doctest: +SKIP
    """
    app = NovaFitApp(database_path)
    app.mainloop()
