"""
Module: command-line interface
Purpose: Offer self-documented automation flags and a friendly interactive NovaFit menu.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Minimal deps; comments in ENGLISH; emojis sparingly.
"""

from __future__ import annotations

import argparse
import logging
import os
import sqlite3
import sys
from datetime import date
from pathlib import Path
from typing import Callable

from . import __version__
from .analytics import calculate_dashboard, format_dashboard
from .backup import BACKUP_DIR, create_complete_backup
from .charts import SUPPORTED_VIEWS, save_analytics_chart
from .config import (
    CONFIG_PATH,
    CSV_EXPORT_PATH,
    DB_PATH,
    EXPORT_PATH,
    LOG_PATH,
    AppSettings,
    load_settings,
    save_settings,
)
from .database import NovaFitDatabase
from .io_utils import (
    export_csv,
    export_json,
    generate_demo_data,
    import_csv,
    import_json,
    initialize_sample_data,
)
from .logging_config import configure_logging
from .i18n import language_label, normalize_language
from .models import ACTIVITY_LEVELS, PROFILE_AVATARS, SPORT_FOCUSES, HealthEntry, UserProfile
from .recommendations import build_recommendation_plan, format_recommendation_plan
from .motivation import build_motivation_snapshot, format_motivation
from .themes import normalize_theme_id, theme_ids, theme_label
from .reporting import export_html_report
from .weather import format_weather, get_weather

LOGGER = logging.getLogger(__name__)


class Console:
    """Provide optional ANSI formatting while keeping messages readable.

    Example:
        >>> Console.success('Saved')
        'Saved ✅'
    """

    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[96m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    PURPLE = "\033[95m"

    @classmethod
    def enabled(cls) -> bool:
        """Return whether ANSI output should be emitted.

        Returns:
            ``True`` for an interactive terminal unless ``NO_COLOR`` is set.

        Raises:
            None.

        Example:
            >>> isinstance(Console.enabled(), bool)
            True
        """
        return sys.stdout.isatty() and "NO_COLOR" not in os.environ

    @classmethod
    def style(cls, text: str, color: str = "", *, bold: bool = False) -> str:
        """Apply terminal styling when supported.

        Args:
            text: Content to display.
            color: ANSI color prefix.
            bold: Whether to use bold weight.

        Returns:
            Styled or plain text.

        Raises:
            None.

        Example:
            >>> 'NovaFit' in Console.style('NovaFit')
            True
        """
        if not cls.enabled():
            return text
        prefix = (cls.BOLD if bold else "") + color
        return f"{prefix}{text}{cls.RESET}"

    @staticmethod
    def success(message: str) -> str:
        """Append one success emoji to a message.

        Args:
            message: Success description.

        Returns:
            Friendly success line.

        Raises:
            None.

        Example:
            >>> Console.success('Saved')
            'Saved ✅'
        """
        return f"{message} ✅"

    @staticmethod
    def warning(message: str) -> str:
        """Append one warning emoji to a message.

        Args:
            message: Warning description.

        Returns:
            Friendly warning line.

        Raises:
            None.

        Example:
            >>> Console.warning('Missing')
            'Missing ⚠️'
        """
        return f"{message} ⚠️"

    @staticmethod
    def error(message: str) -> str:
        """Append one failure emoji to a message.

        Args:
            message: Error description.

        Returns:
            Friendly error line.

        Raises:
            None.

        Example:
            >>> Console.error('Failed')
            'Failed ❌'
        """
        return f"{message} ❌"


def build_parser() -> argparse.ArgumentParser:
    """Build the NovaFit command-line contract.

    Returns:
        Configured ``ArgumentParser`` with one primary action at a time.

    Raises:
        None.

    Example:
        >>> build_parser().prog
        'novafit'
    """
    parser = argparse.ArgumentParser(
        prog="novafit",
        description="NovaFit — local-first health tracking from CLI or Tkinter GUI.",
        epilog="Run without an action to open the interactive menu.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Console and file logging level.",
    )
    parser.add_argument("--debug", action="store_true", help="Show diagnostic exceptions.")
    parser.add_argument("--db", type=Path, default=DB_PATH, help="SQLite database path.")
    parser.add_argument("--user", help="Active profile id or display name.")
    parser.add_argument(
        "--language", choices=("en", "es", "he"), help="Language used by multilingual output."
    )
    parser.add_argument(
        "--theme", choices=theme_ids() + ("dark", "light"), help="Theme override for this command."
    )

    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--gui", action="store_true", help="Open the Tkinter desktop interface.")
    actions.add_argument("--menu", action="store_true", help="Open the interactive terminal menu.")
    actions.add_argument("--add", metavar="DATE", help="Add or update an entry for YYYY-MM-DD.")
    actions.add_argument("--list", nargs="?", const=10, type=int, metavar="N", help="List recent entries.")
    actions.add_argument("--dashboard", action="store_true", help="Show dashboard statistics.")
    actions.add_argument(
        "--motivation", action="store_true", help="Show the grounded Motivation Center summary."
    )
    actions.add_argument(
        "--recommendations", action="store_true", help="Show the conservative Sport & Data Coach plan."
    )
    actions.add_argument("--profiles", action="store_true", help="List local user profiles.")
    actions.add_argument("--create-user", metavar="NAME", help="Create a local user profile.")
    actions.add_argument("--delete-user", type=int, metavar="ID", help="Delete a non-primary user profile.")
    actions.add_argument("--delete", metavar="DATE", help="Delete an entry by date.")
    actions.add_argument("--seed", type=int, metavar="N", help="Generate N demo days.")
    actions.add_argument("--sample", action="store_true", help="Insert seven starter records.")
    actions.add_argument("--export-json", type=Path, metavar="PATH", help="Export JSON backup.")
    actions.add_argument("--import-json", type=Path, metavar="PATH", help="Import JSON backup.")
    actions.add_argument("--export-csv", type=Path, metavar="PATH", help="Export CSV file.")
    actions.add_argument("--import-csv", type=Path, metavar="PATH", help="Import CSV file.")
    actions.add_argument(
        "--backup",
        nargs="?",
        const=BACKUP_DIR,
        type=Path,
        metavar="ZIP_OR_DIR",
        help="Create a complete all-profile ZIP backup with checksums.",
    )
    actions.add_argument("--weather", metavar="CITY", help="Show current weather.")
    actions.add_argument("--chart", type=Path, metavar="PNG", help="Save an analytics dashboard PNG.")
    actions.add_argument(
        "--report-html", type=Path, metavar="HTML", help="Export a self-contained offline HTML report."
    )
    actions.add_argument("--settings", action="store_true", help="Show current settings.")

    parser.add_argument("--steps", type=int, help="Step count used with --add.")
    parser.add_argument("--water", type=float, help="Water liters used with --add.")
    parser.add_argument("--calories", type=int, help="Optional calories used with --add.")
    parser.add_argument("--mood", help="Optional mood used with --add.")
    parser.add_argument("--note", help="Optional private note used with --add.")
    parser.add_argument(
        "--avatar", choices=PROFILE_AVATARS, default="nova", help="Avatar used with --create-user."
    )
    parser.add_argument(
        "--activity-level",
        choices=ACTIVITY_LEVELS,
        default="balanced",
        help="Activity preference used with --create-user.",
    )
    parser.add_argument(
        "--sport-focus",
        choices=SPORT_FOCUSES,
        default="mixed",
        help="Sport preference used with --create-user.",
    )
    parser.add_argument(
        "--import-strategy",
        choices=["replace", "skip"],
        default="replace",
        help="How imports handle an existing date.",
    )
    parser.add_argument("--city", default=None, help="City used by weather menu operations.")
    parser.add_argument(
        "--chart-view",
        choices=SUPPORTED_VIEWS,
        default="overview",
        help="Analytics view used by --chart and --report-html.",
    )
    parser.add_argument(
        "--chart-days",
        type=int,
        default=None,
        help="Calendar days displayed in exported analytics (7–365).",
    )
    parser.add_argument(
        "--chart-theme",
        choices=theme_ids() + ("dark", "light"),
        default=None,
        help="Theme override for exported analytics.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run NovaFit CLI actions and return a process status code.

    Args:
        argv: Optional argument list for tests; ``sys.argv`` is used by default.

    Returns:
        ``0`` on success and ``1`` for a recoverable user-facing failure.

    Raises:
        None. Expected errors are converted to concise messages.

    Example:
        >>> main(['--version'])  # doctest: +SKIP
        0
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        configure_logging(args.log_level, log_file=LOG_PATH, debug=args.debug)
        database = NovaFitDatabase(args.db)
        database.initialize()
        settings = load_settings()
        profile = _prepare_cli_context(args, database, settings)
        return _dispatch(args, database, settings, profile)
    except (ValueError, FileNotFoundError, json_error_types(), sqlite3.Error, OSError) as exc:
        LOGGER.debug("Recoverable CLI failure", exc_info=args.debug)
        print(Console.style(Console.error(str(exc)), Console.RED))
        print("Use --help for valid options or run verify_windows.bat.")
        return 1
    except Exception as exc:  # Keep unexpected stack traces behind --debug.
        LOGGER.error("Unexpected NovaFit failure: %s", exc, exc_info=args.debug)
        print(Console.style(Console.error(f"Unexpected error: {exc}"), Console.RED))
        if not args.debug:
            print("Run again with --debug for diagnostic details.")
        return 1


def _prepare_cli_context(
    args: argparse.Namespace,
    database: NovaFitDatabase,
    settings: AppSettings,
) -> UserProfile:
    """Resolve the active user and merge per-profile preferences into settings.

    Args:
        args: Parsed CLI arguments.
        database: Initialized database.
        settings: Loaded application settings.

    Returns:
        Active local profile.

    Raises:
        ValueError: If a requested user cannot be found.

    Example:
        >>> db = NovaFitDatabase(Path('data/example.db'))
        >>> db.initialize(); _prepare_cli_context(argparse.Namespace(user=None, language=None, theme=None), db, AppSettings()).profile_id
        1
    """
    requested = args.user
    profile: UserProfile | None
    if requested is None:
        profile = database.get_profile(settings.active_profile_id) or database.get_profile(1)
    elif requested.isdigit():
        profile = database.get_profile(int(requested))
    else:
        profile = database.profile_by_name(requested)
    if profile is None:
        raise ValueError(f"User profile not found: {requested}")
    database.set_active_profile(profile.profile_id or 1)
    settings.active_profile_id = profile.profile_id or 1
    settings.step_goal = profile.step_goal
    settings.water_goal_l = profile.water_goal_l
    settings.calorie_goal = profile.calorie_goal
    settings.language = normalize_language(args.language or profile.language)
    settings.theme = normalize_theme_id(args.theme or profile.theme)
    return profile


def print_profiles(database: NovaFitDatabase) -> None:
    """Print local profiles and isolated record counts.

    Args:
        database: Initialized NovaFit database.

    Returns:
        None.

    Example:
        >>> db = NovaFitDatabase(Path('data/example.db'))
        >>> db.initialize(); print_profiles(db)  # doctest: +ELLIPSIS
        LOCAL USER PROFILES...
    """
    print(Console.style("LOCAL USER PROFILES", Console.CYAN, bold=True))
    print("-" * 86)
    print(f"{'ID':>3}  {'Name':<22} {'Language':<10} {'Theme':<18} {'Focus':<11} {'Records':>7}")
    print("-" * 86)
    for profile in database.list_profiles():
        active = "*" if profile.profile_id == database.active_profile_id else " "
        print(
            f"{active}{profile.profile_id:>2}  {profile.display_name:<22.22} "
            f"{language_label(profile.language):<10.10} {theme_label(profile.theme):<18.18} "
            f"{profile.sport_focus:<11.11} {database.count(profile.profile_id):>7}"
        )


def _menu_switch_profile(database: NovaFitDatabase, settings: AppSettings) -> None:
    """Select a local user inside the interactive menu.

    Args:
        database: Shared database.
        settings: Mutable settings.

    Returns:
        None.
    """
    print_profiles(database)
    raw = input("Profile id or name: ").strip()
    profile = database.get_profile(int(raw)) if raw.isdigit() else database.profile_by_name(raw)
    if profile is None:
        raise ValueError(f"Profile not found: {raw}")
    database.set_active_profile(profile.profile_id or 1)
    settings.active_profile_id = profile.profile_id or 1
    settings.step_goal = profile.step_goal
    settings.water_goal_l = profile.water_goal_l
    settings.calorie_goal = profile.calorie_goal
    settings.language = profile.language
    settings.theme = profile.theme
    save_settings(settings)
    print(Console.success(f"Active profile: {profile.display_name}"))


def json_error_types() -> type[Exception]:
    """Return the JSON decode exception without a module-level import cycle.

    Returns:
        ``json.JSONDecodeError`` class.

    Raises:
        None.

    Example:
        >>> issubclass(json_error_types(), Exception)
        True
    """
    import json

    return json.JSONDecodeError


def _dispatch(
    args: argparse.Namespace,
    database: NovaFitDatabase,
    settings: AppSettings,
    profile: UserProfile,
) -> int:
    if args.gui:
        save_settings(settings)
        return launch_gui(database.path)
    if args.add:
        _require_add_fields(args)
        entry = HealthEntry.build(
            args.add,
            args.steps,
            args.water,
            args.calories,
            args.mood,
            args.note,
        )
        database.upsert(entry)
        print(Console.style(Console.success(f"Saved entry for {entry.entry_date}"), Console.GREEN))
        return 0
    if args.list is not None:
        print_entries(database.list(args.list))
        return 0
    if args.dashboard:
        print(format_dashboard(calculate_dashboard(database.list(None), settings), settings))
        return 0
    if args.motivation:
        entries = database.list(None)
        print(format_motivation(build_motivation_snapshot(entries, settings), settings))
        return 0
    if args.recommendations:
        plan = build_recommendation_plan(
            database.list(None), settings, profile, args.language or profile.language
        )
        print(format_recommendation_plan(plan, profile))
        return 0
    if args.profiles:
        print_profiles(database)
        return 0
    if args.create_user:
        created = database.create_profile(
            UserProfile.build(
                args.create_user,
                avatar=args.avatar,
                language=args.language or "en",
                theme=args.theme or "aurora",
                step_goal=settings.step_goal,
                water_goal_l=settings.water_goal_l,
                calorie_goal=settings.calorie_goal,
                activity_level=args.activity_level,
                sport_focus=args.sport_focus,
            )
        )
        print(Console.success(f"Created profile {created.profile_id}: {created.display_name}"))
        return 0
    if args.delete_user is not None:
        deleted = database.delete_profile(args.delete_user)
        print(
            Console.success(f"Deleted profile {args.delete_user}")
            if deleted
            else Console.warning("Profile not found")
        )
        return 0
    if args.delete:
        deleted = database.delete(args.delete)
        message = f"Deleted entry for {args.delete}" if deleted else f"No entry found for {args.delete}"
        print(Console.success(message) if deleted else Console.warning(message))
        return 0
    if args.seed is not None:
        count = generate_demo_data(database, args.seed)
        print(Console.success(f"Generated {count} demo record(s)"))
        return 0
    if args.sample:
        count = initialize_sample_data(database)
        print(Console.success(f"Added {count} starter record(s)"))
        return 0
    if args.export_json:
        count = export_json(database, args.export_json)
        print(Console.success(f"Saved {count} records to {args.export_json}"))
        return 0
    if args.import_json:
        result = import_json(database, args.import_json, strategy=args.import_strategy)
        print_import_result(result.imported, result.skipped, result.invalid)
        return 0
    if args.export_csv:
        count = export_csv(database, args.export_csv)
        print(Console.success(f"Saved {count} records to {args.export_csv}"))
        return 0
    if args.import_csv:
        result = import_csv(database, args.import_csv, strategy=args.import_strategy)
        print_import_result(result.imported, result.skipped, result.invalid)
        return 0
    if args.backup:
        destination = create_complete_backup(database, args.backup)
        print(Console.success(f"Saved complete verified backup to {destination}"))
        return 0
    if args.weather:
        print(format_weather(get_weather(args.weather)))
        return 0
    if args.chart:
        destination = save_analytics_chart(
            database.list(None),
            settings,
            args.chart,
            view=args.chart_view,
            days=args.chart_days,
            theme=args.chart_theme or settings.theme,
        )
        print(Console.success(f"Saved {args.chart_view} analytics to {destination}"))
        return 0
    if args.report_html:
        destination = export_html_report(
            database.list(None),
            settings,
            args.report_html,
            view=args.chart_view,
            days=args.chart_days,
            theme=args.chart_theme,
        )
        print(Console.success(f"Saved offline HTML report to {destination}"))
        return 0
    if args.settings:
        print_settings(settings)
        return 0
    return interactive_menu(database, settings)


def _require_add_fields(args: argparse.Namespace) -> None:
    missing = [name for name in ("steps", "water") if getattr(args, name) is None]
    if missing:
        joined = ", ".join(f"--{name}" for name in missing)
        raise ValueError(f"--add also requires {joined}.")


def print_entries(entries: list[HealthEntry]) -> None:
    """Print health entries in an aligned terminal table.

    Args:
        entries: Records ordered for display.

    Returns:
        None.

    Raises:
        None.

    Example:
        >>> print_entries([])
        No entries found. Add one with --add or --sample. 💡
    """
    if not entries:
        print("No entries found. Add one with --add or --sample. 💡")
        return
    print(Console.style("NovaFit Health Entries", Console.CYAN, bold=True))
    print("-" * 88)
    print(f"{'Date':<12} {'Steps':>9} {'Water':>8} {'Calories':>10} {'Mood':<14} Note")
    print("-" * 88)
    for entry in entries:
        calories = "—" if entry.calories is None else f"{entry.calories:,}"
        note = (entry.note or "")[:24]
        print(
            f"{entry.entry_date.isoformat():<12} {entry.steps:>9,} "
            f"{entry.water_l:>6.2f} L {calories:>10} {(entry.mood or '—'):<14.14} {note}"
        )


def print_import_result(imported: int, skipped: int, invalid: int) -> None:
    """Print one compact import summary.

    Args:
        imported: Number of records written.
        skipped: Number of existing records preserved.
        invalid: Number of malformed rows ignored.

    Returns:
        None.

    Raises:
        None.

    Example:
        >>> print_import_result(2, 1, 0)
        Imported 2, skipped 1, invalid 0 ✅
    """
    print(Console.success(f"Imported {imported}, skipped {skipped}, invalid {invalid}"))


def print_settings(settings: AppSettings) -> None:
    """Print current local goals and interface preferences.

    Args:
        settings: Validated application settings.

    Returns:
        None.

    Raises:
        ValueError: If settings are invalid.

    Example:
        >>> print_settings(AppSettings())
        NovaFit Settings
        ...
    """
    settings.validate()
    print("NovaFit Settings")
    print("=" * 32)
    print(f"Step goal: {settings.step_goal:,}")
    print(f"Water goal: {settings.water_goal_l:.1f} L")
    print(f"Calorie reference: {settings.calorie_goal:,}")
    print(f"Default city: {settings.default_city.title()}")
    print(f"Theme: {theme_label(settings.theme)} ({settings.theme})")
    print(f"Chart range: {settings.chart_days} days")
    print(f"Chart view: {settings.chart_view}")
    print(f"Reduced motion: {settings.reduce_motion}")
    print(f"Personal why: {settings.personal_why or 'Not set'}")
    print(f"Weekly focus: {settings.weekly_focus or 'Automatic'}")
    print(f"Reward note: {settings.reward_note or 'Not set'}")
    print(f"Configuration: {CONFIG_PATH}")


def launch_gui(database_path: Path = DB_PATH) -> int:
    """Open the Tkinter GUI using the selected database.

    Args:
        database_path: SQLite database path passed to the GUI.

    Returns:
        ``0`` after the window closes.

    Raises:
        RuntimeError: If Tkinter cannot initialize.

    Example:
        >>> launch_gui(Path('data/example.db'))  # doctest: +SKIP
        0
    """
    from .gui import run_gui

    run_gui(database_path)
    return 0


def interactive_menu(database: NovaFitDatabase, settings: AppSettings) -> int:
    """Run the keyboard-driven NovaFit terminal menu.

    Args:
        database: Active data store.
        settings: Mutable local preferences for menu operations.

    Returns:
        ``0`` when the user exits normally.

    Raises:
        None. Invalid inputs are shown and the menu continues.

    Example:
        >>> interactive_menu(NovaFitDatabase(Path('data/example.db')), AppSettings())  # doctest: +SKIP
        0
    """
    actions: dict[str, tuple[str, Callable[[], None]]] = {
        "1": ("Add or update entry", lambda: _menu_add(database)),
        "2": ("List recent entries", lambda: _menu_list(database)),
        "3": (
            "Dashboard",
            lambda: print(format_dashboard(calculate_dashboard(database.list(None), settings), settings)),
        ),
        "4": (
            "Motivation Center",
            lambda: print(
                format_motivation(build_motivation_snapshot(database.list(None), settings), settings)
            ),
        ),
        "5": (
            "Sport & Data Coach",
            lambda: print(
                format_recommendation_plan(
                    build_recommendation_plan(
                        database.list(None),
                        settings,
                        database.get_profile(database.active_profile_id) or UserProfile.build("Primary User"),
                        settings.language,
                    ),
                    database.get_profile(database.active_profile_id) or UserProfile.build("Primary User"),
                )
            ),
        ),
        "6": ("Switch local user", lambda: _menu_switch_profile(database, settings)),
        "7": ("List user profiles", lambda: print_profiles(database)),
        "8": ("Search date range", lambda: _menu_search(database)),
        "9": ("Delete entry", lambda: _menu_delete(database)),
        "10": (
            "Weather",
            lambda: print(
                format_weather(
                    get_weather(input(f"City [{settings.default_city}]: ").strip() or settings.default_city)
                )
            ),
        ),
        "11": (
            "Export JSON",
            lambda: print(
                Console.success(f"Saved {export_json(database, EXPORT_PATH)} records to {EXPORT_PATH}")
            ),
        ),
        "12": ("Import JSON", lambda: _menu_import_json(database)),
        "13": (
            "Export CSV",
            lambda: print(
                Console.success(f"Saved {export_csv(database, CSV_EXPORT_PATH)} records to {CSV_EXPORT_PATH}")
            ),
        ),
        "14": ("Import CSV", lambda: _menu_import_csv(database)),
        "15": ("Generate demo data", lambda: _menu_seed(database)),
        "16": ("Open GUI", lambda: launch_gui(database.path)),
        "17": ("Edit goals, theme, and purpose", lambda: _menu_settings(database, settings)),
        "18": (
            "Export analytics PNG",
            lambda: print(
                Console.success(
                    f"Saved chart to {save_analytics_chart(database.list(None), settings, Path('data/novafit-dashboard.png'), view=settings.chart_view, days=settings.chart_days, theme=settings.theme)}"
                )
            ),
        ),
        "19": (
            "Export visual HTML report",
            lambda: print(
                Console.success(
                    f"Saved report to {export_html_report(database.list(None), settings, Path('data/novafit-report.html'), view=settings.chart_view)}"
                )
            ),
        ),
        "20": ("Clear active-profile data", lambda: _menu_clear(database)),
    }
    while True:
        _print_menu(actions)
        try:
            choice = input("Choose an option: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye — keep building healthy habits. 💙")
            return 0
        if choice == "0":
            print("Goodbye — keep building healthy habits. 💙")
            return 0
        selected = actions.get(choice)
        if selected is None:
            print(Console.warning("Invalid option; choose a listed number"))
            continue
        try:
            selected[1]()
        except (ValueError, FileNotFoundError, OSError, sqlite3.Error) as exc:
            print(Console.error(str(exc)))


def _print_menu(actions: dict[str, tuple[str, Callable[[], None]]]) -> None:
    print()
    print(Console.style("╔════════════════════════════════════════════════════╗", Console.PURPLE, bold=True))
    print(Console.style("║  NOVAFIT ULTIMATE · LOCAL WELLNESS COMMAND CENTER ║", Console.CYAN, bold=True))
    print(Console.style("╚════════════════════════════════════════════════════╝", Console.PURPLE, bold=True))
    for key, (label, _) in actions.items():
        print(f"{key:>2}) {label}")
    print(" 0) Exit")
    print("=" * 42)


def _menu_add(database: NovaFitDatabase) -> None:
    today = date.today().isoformat()
    entry = HealthEntry.build(
        input(f"Date [{today}]: ").strip() or today,
        input("Steps: ").strip(),
        input("Water liters: ").strip(),
        input("Calories [optional]: ").strip(),
        input("Mood [optional]: ").strip(),
        input("Note [optional]: ").strip(),
    )
    database.upsert(entry)
    print(Console.success(f"Saved entry for {entry.entry_date}"))


def _menu_list(database: NovaFitDatabase) -> None:
    raw = input("How many entries [10]: ").strip()
    print_entries(database.list(int(raw) if raw else 10))


def _menu_search(database: NovaFitDatabase) -> None:
    start = input("Start date YYYY-MM-DD: ").strip()
    end = input("End date YYYY-MM-DD: ").strip()
    print_entries(database.search(start, end))


def _menu_delete(database: NovaFitDatabase) -> None:
    target = input("Date to delete YYYY-MM-DD: ").strip()
    if input(f"Delete {target}? Type YES: ").strip() != "YES":
        print("Deletion cancelled.")
        return
    print(
        Console.success(f"Deleted {target}")
        if database.delete(target)
        else Console.warning("Entry not found")
    )


def _menu_import_json(database: NovaFitDatabase) -> None:
    path = Path(input(f"JSON path [{EXPORT_PATH}]: ").strip() or EXPORT_PATH)
    result = import_json(database, path, strategy="replace")
    print_import_result(result.imported, result.skipped, result.invalid)


def _menu_import_csv(database: NovaFitDatabase) -> None:
    path = Path(input(f"CSV path [{CSV_EXPORT_PATH}]: ").strip() or CSV_EXPORT_PATH)
    result = import_csv(database, path, strategy="replace")
    print_import_result(result.imported, result.skipped, result.invalid)


def _menu_seed(database: NovaFitDatabase) -> None:
    raw = input("Demo days [30]: ").strip()
    count = generate_demo_data(database, int(raw) if raw else 30)
    print(Console.success(f"Generated {count} demo record(s)"))


def _menu_settings(database: NovaFitDatabase, settings: AppSettings) -> None:
    """Edit persistent goals, theme, accessibility, and purpose fields.

    Args:
        database: Active profile store.
        settings: Mutable settings object used by the current menu session.

    Returns:
        None.

    Example:
        >>> _menu_settings(NovaFitDatabase(Path('data/example.db')), AppSettings())  # doctest: +SKIP
    """
    print(f"Available themes: {', '.join(theme_ids())}")
    updated = AppSettings(
        step_goal=int(input(f"Step goal [{settings.step_goal}]: ").strip() or settings.step_goal),
        water_goal_l=float(input(f"Water goal [{settings.water_goal_l}]: ").strip() or settings.water_goal_l),
        calorie_goal=int(
            input(f"Calorie reference [{settings.calorie_goal}]: ").strip() or settings.calorie_goal
        ),
        default_city=input(f"Default city [{settings.default_city}]: ").strip() or settings.default_city,
        theme=input(f"Theme [{settings.theme}]: ").strip() or settings.theme,
        show_achievements=settings.show_achievements,
        chart_days=int(input(f"Chart days [{settings.chart_days}]: ").strip() or settings.chart_days),
        chart_view=input(
            f"Chart view command_center/trend_lab/consistency_map/training_atlas [{settings.chart_view}]: "
        ).strip()
        or settings.chart_view,
        reduce_motion=(
            input(f"Reduce motion y/n [{'y' if settings.reduce_motion else 'n'}]: ").strip().lower()
            or ("y" if settings.reduce_motion else "n")
        )
        in {"y", "yes"},
        personal_why=input(f"Personal why [{settings.personal_why}]: ").strip() or settings.personal_why,
        weekly_focus=input(f"Weekly focus [{settings.weekly_focus or 'automatic'}]: ").strip(),
        reward_note=input(f"Reward note [{settings.reward_note}]: ").strip() or settings.reward_note,
        language=normalize_language(
            input(f"Language en/es/he [{settings.language}]: ").strip() or settings.language
        ),
        active_profile_id=settings.active_profile_id,
        ui_scale=settings.ui_scale,
    ).validate()
    profile = database.get_profile(database.active_profile_id)
    if profile is None:
        raise ValueError("The active profile no longer exists.")
    database.update_profile(
        UserProfile.build(
            profile.display_name,
            profile_id=profile.profile_id,
            avatar=profile.avatar,
            language=updated.language,
            theme=updated.theme,
            step_goal=updated.step_goal,
            water_goal_l=updated.water_goal_l,
            calorie_goal=updated.calorie_goal,
            activity_level=profile.activity_level,
            sport_focus=profile.sport_focus,
        )
    )
    save_settings(updated)
    for field_name in (
        "step_goal",
        "water_goal_l",
        "calorie_goal",
        "default_city",
        "theme",
        "show_achievements",
        "chart_days",
        "chart_view",
        "reduce_motion",
        "personal_why",
        "weekly_focus",
        "reward_note",
        "language",
        "active_profile_id",
        "ui_scale",
    ):
        setattr(settings, field_name, getattr(updated, field_name))
    print(Console.success("Settings saved"))


def _menu_clear(database: NovaFitDatabase) -> None:
    if input("Type DELETE ALL to remove every record: ").strip() != "DELETE ALL":
        print("Clear operation cancelled.")
        return
    print(Console.success(f"Deleted {database.clear()} record(s)"))


if __name__ == "__main__":
    raise SystemExit(main())
