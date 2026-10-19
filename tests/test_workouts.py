"""
Module: training log tests
Purpose: Protect workout validation, per-profile storage, the schema 4 → 5
    upgrade, weekly summaries, CLI actions and the training panel.
Author: Kevin "Lirioth" Cusnir
Date: 2026-10-19 | TZ: Asia/Jerusalem
Notes: Generated data only; Tk checks skip when no display is available.
"""

from __future__ import annotations

import contextlib
import csv
import io
import sqlite3
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

from novafit.cli import main
from novafit.database import SCHEMA_VERSION, NovaFitDatabase
from novafit.i18n import TRANSLATIONS
from novafit.models import HealthEntry, UserProfile
from novafit.training_panel import weekly_bar_layout
from novafit.workouts import (
    WORKOUT_KINDS,
    TrainingWeek,
    WorkoutSession,
    WorkoutStore,
    build_training_snapshot,
    export_workouts_csv,
    format_training_summary,
    generate_demo_workouts,
    normalize_workout_kind,
    week_start,
    weekly_training_summary,
)

MONDAY = date(2026, 10, 19)


class WorkoutSessionTests(unittest.TestCase):
    """Validate the session contract at the boundary."""

    def test_build_normalizes_aliases_and_localized_labels(self) -> None:
        self.assertEqual(normalize_workout_kind("Run"), "running")
        self.assertEqual(normalize_workout_kind("Correr"), "running")
        self.assertEqual(normalize_workout_kind("ריצה"), "running")
        self.assertEqual(normalize_workout_kind("yoga"), "mobility")
        with self.assertRaises(ValueError):
            normalize_workout_kind("teleporting")

    def test_build_validates_bounds_and_optional_fields(self) -> None:
        session = WorkoutSession.build(
            "2026-10-19", "running", "30", rpe="6", distance_km="", note="  easy  "
        )
        self.assertEqual(session.duration_min, 30)
        self.assertEqual(session.load, 180)
        self.assertIsNone(session.distance_km)
        self.assertEqual(session.note, "easy")
        self.assertIsNone(WorkoutSession.build("2026-10-19", "walking", 20).load)
        for bad in (0, 601, -5, "abc", 12.5):
            with self.assertRaises(ValueError):
                WorkoutSession.build("2026-10-19", "walking", bad)
        for bad_rpe in (0, 11):
            with self.assertRaises(ValueError):
                WorkoutSession.build("2026-10-19", "walking", 20, rpe=bad_rpe)
        with self.assertRaises(ValueError):
            WorkoutSession.build("2026-02-30", "walking", 20)
        with self.assertRaises(ValueError):
            WorkoutSession.build("2026-10-19", "cycling", 60, distance_km=501)


class WorkoutStoreTests(unittest.TestCase):
    """Keep sessions isolated per profile and consistent with the schema."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database = NovaFitDatabase(Path(self.temp_dir.name) / "training.db")
        self.database.initialize()
        self.store = WorkoutStore(self.database)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_crud_and_ordering(self) -> None:
        first = self.store.add(WorkoutSession.build("2026-10-12", "walking", 40))
        second = self.store.add(WorkoutSession.build("2026-10-19", "running", 30, rpe=6))
        self.assertIsNotNone(first.session_id)
        self.assertEqual(
            [item.session_id for item in self.store.list()], [second.session_id, first.session_id]
        )
        self.assertEqual(self.store.count(), 2)
        self.assertEqual(len(self.store.search("2026-10-13", "2026-10-31")), 1)
        with self.assertRaises(ValueError):
            self.store.search("2026-10-31", "2026-10-01")
        self.assertTrue(self.store.delete(first.session_id or 0))
        self.assertFalse(self.store.delete(first.session_id or 0))
        self.assertEqual(self.store.count(), 1)

    def test_profiles_are_isolated_and_deletion_cascades(self) -> None:
        other = self.database.create_profile(UserProfile.build("Second Athlete"))
        other_id = other.profile_id or 0
        mine = self.store.add(WorkoutSession.build("2026-10-19", "strength", 45, rpe=7))
        self.store.add(WorkoutSession.build("2026-10-19", "cycling", 60), other_id)
        self.assertEqual(self.store.count(), 1)
        self.assertEqual(self.store.count(other_id), 1)
        self.assertFalse(self.store.delete(mine.session_id or 0, other_id))
        self.database.delete_profile(other_id)
        with contextlib.closing(sqlite3.connect(self.database.path)) as connection:
            orphans = connection.execute("SELECT COUNT(*) FROM workouts WHERE user_id = ?", (other_id,))
            self.assertEqual(orphans.fetchone()[0], 0)

    def test_schema_four_upgrade_is_additive(self) -> None:
        self.database.upsert(HealthEntry.build("2026-10-18", 9000, 2.1, note="kept"))
        with contextlib.closing(sqlite3.connect(self.database.path)) as connection:
            connection.execute("DROP TABLE workouts")
            connection.execute("UPDATE app_meta SET value = '4' WHERE key = 'schema_version'")
            connection.commit()
        self.database.initialize()
        self.assertEqual(SCHEMA_VERSION, 5)
        with contextlib.closing(sqlite3.connect(self.database.path)) as connection:
            version = connection.execute("SELECT value FROM app_meta WHERE key = 'schema_version'").fetchone()
            tables = {
                row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")
            }
        self.assertEqual(version[0], "5")
        self.assertIn("workouts", tables)
        kept = self.database.get("2026-10-18")
        self.assertIsNotNone(kept)
        self.assertEqual(kept.note if kept else None, "kept")

    def test_csv_export_and_deterministic_demo(self) -> None:
        inserted = generate_demo_workouts(self.store, 4, end_date=MONDAY)
        self.assertGreater(inserted, 0)
        replay = WorkoutStore(NovaFitDatabase(Path(self.temp_dir.name) / "replay.db"))
        replay.database.initialize()
        self.assertEqual(generate_demo_workouts(replay, 4, end_date=MONDAY), inserted)
        destination = Path(self.temp_dir.name) / "out" / "training.csv"
        self.assertEqual(export_workouts_csv(self.store, destination), inserted)
        with destination.open(encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), inserted)
        self.assertEqual(rows[0]["kind"] in WORKOUT_KINDS, True)
        with self.assertRaises(ValueError):
            generate_demo_workouts(self.store, 0)


class TrainingSummaryTests(unittest.TestCase):
    """Check weekly aggregation and the descriptive snapshot."""

    def test_weeks_are_monday_based_and_oldest_first(self) -> None:
        sessions = [
            WorkoutSession.build("2026-10-19", "running", 30, rpe=6),
            WorkoutSession.build("2026-10-25", "walking", 20),
            WorkoutSession.build("2026-10-18", "strength", 40, rpe=5),
            WorkoutSession.build("2026-01-01", "walking", 99),
        ]
        weeks = weekly_training_summary(sessions, today=date(2026, 10, 22), weeks=3)
        self.assertEqual([week.week_start for week in weeks], [date(2026, 10, 5), date(2026, 10, 12), MONDAY])
        self.assertEqual(weeks[-1].minutes, 50)
        self.assertEqual(weeks[-1].sessions, 2)
        self.assertEqual(weeks[-1].load, 180)
        self.assertEqual(weeks[1].minutes, 40)
        self.assertEqual(week_start(date(2026, 10, 25)), MONDAY)
        with self.assertRaises(ValueError):
            weekly_training_summary(sessions, today=MONDAY, weeks=0)

    def test_streak_survives_an_empty_current_week(self) -> None:
        sessions = [
            WorkoutSession.build(MONDAY - timedelta(weeks=offset, days=2), "walking", 30)
            for offset in range(3)
        ]
        snapshot = build_training_snapshot(sessions, today=MONDAY)
        self.assertEqual(snapshot.this_week.sessions, 0)
        self.assertEqual(snapshot.streak_weeks, 3)
        sessions.append(WorkoutSession.build(MONDAY, "running", 200))
        snapshot = build_training_snapshot(sessions, today=MONDAY)
        self.assertEqual(snapshot.streak_weeks, 4)
        self.assertEqual(snapshot.reference_percent, 100)
        self.assertEqual(snapshot.minutes_change, 170)
        self.assertEqual(snapshot.favorite_kind, "walking")

    def test_formatted_summary_is_localized(self) -> None:
        snapshot = build_training_snapshot([WorkoutSession.build(MONDAY, "running", 30)], today=MONDAY)
        self.assertIn("REGISTRO DE ENTRENAMIENTOS", format_training_summary(snapshot, "es"))
        hebrew = format_training_summary(snapshot, "he")
        self.assertIn("יומן אימונים", hebrew)
        self.assertIn("ריצה", hebrew)

    def test_training_keys_exist_in_every_language(self) -> None:
        for key in (
            "nav_training",
            "tab_training",
            "training_scope",
            *(f"workout_kind_{k}" for k in WORKOUT_KINDS),
        ):
            for code in ("en", "es", "he"):
                self.assertIn(key, TRANSLATIONS[code])


class TrainingCliTests(unittest.TestCase):
    """Exercise the documented training flags end to end."""

    def test_training_flags(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db = ["--db", str(Path(temp_dir) / "cli.db")]
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(
                    main(
                        [
                            *db,
                            "--add-workout",
                            "2026-10-19",
                            "--kind",
                            "running",
                            "--minutes",
                            "32",
                            "--rpe",
                            "6",
                        ]
                    ),
                    0,
                )
                self.assertEqual(main([*db, "--seed-workouts", "2"]), 0)
                self.assertEqual(main([*db, "--workouts", "5"]), 0)
                self.assertEqual(main([*db, "--training", "4", "--language", "es"]), 0)
                csv_path = Path(temp_dir) / "sessions.csv"
                self.assertEqual(main([*db, "--export-workouts-csv", str(csv_path)]), 0)
                self.assertEqual(main([*db, "--delete-workout", "1"]), 0)
                self.assertEqual(main([*db, "--add-workout", "2026-10-19", "--kind", "running"]), 1)
            text = output.getvalue()
            self.assertIn("Saved session 1", text)
            self.assertIn("REGISTRO DE ENTRENAMIENTOS", text)
            self.assertIn("Deleted session 1", text)
            self.assertIn("--minutes", text)
            self.assertTrue(csv_path.exists())


class TrainingPanelTests(unittest.TestCase):
    """Keep the chart geometry sane and the Tk panel constructible."""

    def test_bar_layout_stays_inside_the_canvas(self) -> None:
        weeks = [
            TrainingWeek(week_start=MONDAY - timedelta(weeks=3 - index), minutes=minutes)
            for index, minutes in enumerate((0, 90, 400, 120))
        ]
        bars, line_y = weekly_bar_layout(weeks, 400, 200)
        self.assertEqual(len(bars), 4)
        self.assertTrue(bars[-1].current)
        self.assertFalse(bars[0].current)
        for bar in bars:
            self.assertGreaterEqual(bar.y0, 28 - 0.001)
            self.assertLessEqual(bar.x1, 400 - 28 + 0.001)
            self.assertLessEqual(bar.y0, bar.y1)
        self.assertAlmostEqual(bars[2].y0, 28)
        self.assertGreater(line_y, bars[2].y0)

    def test_panel_builds_and_refreshes_in_every_language(self) -> None:
        import tkinter as tk

        try:
            root = tk.Tk()
        except tk.TclError as exc:  # Headless CI without a display.
            self.skipTest(f"Tk unavailable: {exc}")
        root.withdraw()
        try:
            from novafit.themes import get_theme
            from novafit.training_panel import TrainingPanel

            with tempfile.TemporaryDirectory() as temp_dir:
                database = NovaFitDatabase(Path(temp_dir) / "panel.db")
                database.initialize()
                store = WorkoutStore(database)
                generate_demo_workouts(store, 3, end_date=MONDAY)
                palette = dict(get_theme("aurora").ui)
                errors: list[Exception] = []
                for language in ("en", "es", "he"):
                    panel = TrainingPanel(
                        root,
                        store,
                        lambda: palette,
                        lambda language=language: language,
                        lambda: "Test Athlete",
                        lambda _message: None,
                        lambda _title, exc: errors.append(exc),
                    )
                    panel.refresh(today=MONDAY)
                    self.assertEqual(len(panel.tree.get_children()), store.count())
                    panel.minutes_var.set("25")
                    panel._save()
                    self.assertEqual(errors, [])
                    panel.destroy()
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
