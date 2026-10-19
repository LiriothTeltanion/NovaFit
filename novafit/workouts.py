"""
Module: training sessions
Purpose: Record, validate, summarize, and export per-profile workout sessions
    beside the daily wellness log.
Author: Kevin "Lirioth" Cusnir
Date: 2026-10-19 | TZ: Asia/Jerusalem
Notes: Standard library only; descriptive summaries, never medical or training prescriptions.
"""

from __future__ import annotations

import csv
import random
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import Any

from .database import NovaFitDatabase
from .i18n import normalize_language, tr
from .validation import (
    MAX_NOTE_LENGTH,
    clean_text,
    parse_iso_date,
    validate_non_negative_float,
    validate_non_negative_int,
    validate_optional_int,
)

WORKOUT_KINDS: tuple[str, ...] = (
    "walking",
    "running",
    "cycling",
    "strength",
    "mobility",
    "swimming",
    "sport",
    "other",
)
MAX_DURATION_MIN = 600
MAX_DISTANCE_KM = 500.0
# General adult reference from the WHO 2020 guidelines (150 minutes of moderate
# activity per week). Shown for orientation only; it is not a personal target.
REFERENCE_WEEKLY_MINUTES = 150
CSV_FIELDS: tuple[str, ...] = ("id", "date", "kind", "duration_min", "rpe", "distance_km", "load", "note")

_KIND_ALIASES = {
    "walk": "walking",
    "run": "running",
    "bike": "cycling",
    "cycle": "cycling",
    "gym": "strength",
    "weights": "strength",
    "yoga": "mobility",
    "stretching": "mobility",
    "swim": "swimming",
}


def normalize_workout_kind(value: Any) -> str:
    """Return a stable workout kind from a code, alias, or localized label.

    Args:
        value: Raw kind such as ``running``, ``run`` or ``Correr``.

    Returns:
        One of ``WORKOUT_KINDS``.

    Raises:
        ValueError: If the kind is unknown.

    Example:
        >>> normalize_workout_kind("Run")
        'running'
    """
    text = str(value or "").strip()
    lowered = text.lower()
    if lowered in WORKOUT_KINDS:
        return lowered
    if lowered in _KIND_ALIASES:
        return _KIND_ALIASES[lowered]
    for language in ("en", "es", "he"):
        for kind in WORKOUT_KINDS:
            if tr(language, f"workout_kind_{kind}").lower() == lowered:
                return kind
    raise ValueError(f"Unknown workout type: {text or '—'}. Choose one of: {', '.join(WORKOUT_KINDS)}.")


@dataclass(frozen=True, slots=True)
class WorkoutSession:
    """Represent one validated training session.

    Attributes:
        session_date: Calendar day of the session.
        kind: Stable workout kind from ``WORKOUT_KINDS``.
        duration_min: Whole minutes, 1–600.
        rpe: Optional session effort on the 1–10 perceived-exertion scale.
        distance_km: Optional distance in kilometres.
        note: Optional private note.
        session_id: Database id once stored.

    Example:
        >>> WorkoutSession.build("2026-10-19", "running", 30, rpe=6).load
        180
    """

    session_date: date
    kind: str
    duration_min: int
    rpe: int | None = None
    distance_km: float | None = None
    note: str | None = None
    session_id: int | None = None

    @classmethod
    def build(
        cls,
        session_date: str | date,
        kind: Any,
        duration_min: Any,
        *,
        rpe: Any = None,
        distance_km: Any = None,
        note: Any = None,
        session_id: int | None = None,
    ) -> WorkoutSession:
        """Create a validated session from user-facing values.

        Raises:
            ValueError: If any value is malformed or outside safe bounds.
        """
        parsed_date = session_date if isinstance(session_date, date) else parse_iso_date(str(session_date))
        minutes = validate_non_negative_int(duration_min, "Duration", MAX_DURATION_MIN)
        if minutes < 1:
            raise ValueError("Duration must be at least 1 minute.")
        effort = validate_optional_int(rpe, "Effort (RPE)", 10)
        if effort is not None and effort < 1:
            raise ValueError("Effort (RPE) must be between 1 and 10.")
        distance = (
            None
            if distance_km is None or str(distance_km).strip() == ""
            else validate_non_negative_float(distance_km, "Distance", MAX_DISTANCE_KM)
        )
        return cls(
            session_date=parsed_date,
            kind=normalize_workout_kind(kind),
            duration_min=minutes,
            rpe=effort,
            distance_km=distance,
            note=clean_text(note, "Note", MAX_NOTE_LENGTH),
            session_id=session_id,
        )

    @property
    def load(self) -> int | None:
        """Return session load as minutes × RPE, or ``None`` without an RPE.

        This is the descriptive "session-RPE" bookkeeping used by coaches to
        compare weeks; it is not a physiological measurement.
        """
        return None if self.rpe is None else self.duration_min * self.rpe

    def to_row(self) -> dict[str, Any]:
        """Return a flat, export-friendly mapping."""
        return {
            "id": self.session_id,
            "date": self.session_date.isoformat(),
            "kind": self.kind,
            "duration_min": self.duration_min,
            "rpe": self.rpe,
            "distance_km": self.distance_km,
            "load": self.load,
            "note": self.note,
        }


@dataclass(frozen=True, slots=True)
class TrainingWeek:
    """Aggregate one Monday-based training week."""

    week_start: date
    sessions: int = 0
    minutes: int = 0
    active_days: int = 0
    load: int = 0
    kinds: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class TrainingSnapshot:
    """Summarize recent training for dashboards and the CLI."""

    this_week: TrainingWeek
    last_week: TrainingWeek
    weeks: tuple[TrainingWeek, ...]
    streak_weeks: int
    favorite_kind: str | None
    total_sessions: int
    reference_minutes: int = REFERENCE_WEEKLY_MINUTES

    @property
    def reference_percent(self) -> int:
        """Return this week's minutes against the general reference, capped at 100."""
        if self.reference_minutes <= 0:
            return 0
        return min(100, round(self.this_week.minutes * 100 / self.reference_minutes))

    @property
    def minutes_change(self) -> int:
        """Return this week's minute difference against last week."""
        return self.this_week.minutes - self.last_week.minutes


class WorkoutStore:
    """Persist workout sessions for the profiles of one NovaFit database.

    Args:
        database: Initialized database; its active profile is the default owner.

    Example:
        >>> store = WorkoutStore(NovaFitDatabase(Path('data/example.db')))  # doctest: +SKIP
        >>> store.add(WorkoutSession.build('2026-10-19', 'walking', 40)).session_id  # doctest: +SKIP
        1
    """

    def __init__(self, database: NovaFitDatabase) -> None:
        self.database = database

    def add(self, session: WorkoutSession, profile_id: int | None = None) -> WorkoutSession:
        """Store one session and return it with its new id."""
        user_id = self.database.resolve_profile_id(profile_id)
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO workouts(user_id, date, kind, duration_min, rpe, distance_km, note)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    session.session_date.isoformat(),
                    session.kind,
                    session.duration_min,
                    session.rpe,
                    session.distance_km,
                    session.note,
                ),
            )
            connection.commit()
            new_id = int(cursor.lastrowid or 0)
        return WorkoutSession(
            session_date=session.session_date,
            kind=session.kind,
            duration_min=session.duration_min,
            rpe=session.rpe,
            distance_km=session.distance_km,
            note=session.note,
            session_id=new_id,
        )

    def list(self, limit: int | None = 30, profile_id: int | None = None) -> list[WorkoutSession]:
        """List sessions from newest to oldest for one profile.

        Raises:
            ValueError: If a supplied limit is not positive.
        """
        if limit is not None and limit <= 0:
            raise ValueError("Limit must be greater than zero.")
        user_id = self.database.resolve_profile_id(profile_id)
        query = (
            "SELECT id, date, kind, duration_min, rpe, distance_km, note FROM workouts "
            "WHERE user_id = ? ORDER BY date DESC, id DESC"
        )
        parameters: tuple[Any, ...] = (user_id,)
        if limit is not None:
            query += " LIMIT ?"
            parameters = (user_id, limit)
        with self.database.connect() as connection:
            rows = connection.execute(query, parameters).fetchall()
        return [self._row_to_session(row) for row in rows]

    def search(
        self, start_date: str | date, end_date: str | date, profile_id: int | None = None
    ) -> list[WorkoutSession]:
        """Return sessions inside an inclusive date range, newest first."""
        start = start_date if isinstance(start_date, date) else parse_iso_date(str(start_date))
        end = end_date if isinstance(end_date, date) else parse_iso_date(str(end_date))
        if start > end:
            raise ValueError("Start date cannot be after end date.")
        user_id = self.database.resolve_profile_id(profile_id)
        with self.database.connect() as connection:
            rows = connection.execute(
                """
                SELECT id, date, kind, duration_min, rpe, distance_km, note FROM workouts
                WHERE user_id = ? AND date BETWEEN ? AND ?
                ORDER BY date DESC, id DESC
                """,
                (user_id, start.isoformat(), end.isoformat()),
            ).fetchall()
        return [self._row_to_session(row) for row in rows]

    def delete(self, session_id: int, profile_id: int | None = None) -> bool:
        """Delete one session owned by the selected profile."""
        user_id = self.database.resolve_profile_id(profile_id)
        with self.database.connect() as connection:
            cursor = connection.execute(
                "DELETE FROM workouts WHERE id = ? AND user_id = ?", (int(session_id), user_id)
            )
            connection.commit()
            return cursor.rowcount > 0

    def count(self, profile_id: int | None = None) -> int:
        """Return how many sessions one profile has."""
        user_id = self.database.resolve_profile_id(profile_id)
        with self.database.connect() as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS total FROM workouts WHERE user_id = ?", (user_id,)
            ).fetchone()
        return int(row["total"])

    @staticmethod
    def _row_to_session(row: Any) -> WorkoutSession:
        return WorkoutSession.build(
            row["date"],
            row["kind"],
            row["duration_min"],
            rpe=row["rpe"],
            distance_km=row["distance_km"],
            note=row["note"],
            session_id=int(row["id"]),
        )


def week_start(day: date) -> date:
    """Return the Monday that starts the ISO week containing ``day``."""
    return day - timedelta(days=day.weekday())


def weekly_training_summary(
    sessions: Iterable[WorkoutSession], *, today: date | None = None, weeks: int = 8
) -> tuple[TrainingWeek, ...]:
    """Aggregate sessions into consecutive Monday-based weeks, oldest first.

    Args:
        sessions: Sessions of one profile, in any order.
        today: Reference day; the current week is the last element.
        weeks: Number of weeks, 1–52.

    Raises:
        ValueError: If ``weeks`` is outside 1–52.

    Example:
        >>> weekly_training_summary([], today=date(2026, 10, 19), weeks=2)[-1].week_start.isoformat()
        '2026-10-19'
    """
    if not 1 <= weeks <= 52:
        raise ValueError("Weeks must be between 1 and 52.")
    current = week_start(today or date.today())
    starts = [current - timedelta(weeks=offset) for offset in range(weeks - 1, -1, -1)]
    buckets: dict[date, list[WorkoutSession]] = {start: [] for start in starts}
    for session in sessions:
        bucket = buckets.get(week_start(session.session_date))
        if bucket is not None:
            bucket.append(session)
    return tuple(_aggregate_week(start, buckets[start]) for start in starts)


def _aggregate_week(start: date, sessions: Sequence[WorkoutSession]) -> TrainingWeek:
    kinds = Counter(session.kind for session in sessions)
    return TrainingWeek(
        week_start=start,
        sessions=len(sessions),
        minutes=sum(session.duration_min for session in sessions),
        active_days=len({session.session_date for session in sessions}),
        load=sum(session.load or 0 for session in sessions),
        kinds=dict(sorted(kinds.items())),
    )


def build_training_snapshot(
    sessions: Sequence[WorkoutSession], *, today: date | None = None, weeks: int = 8
) -> TrainingSnapshot:
    """Build the descriptive training overview shown in the GUI and CLI.

    The streak counts consecutive weeks with at least one session, ending with
    the current week when it already has one, otherwise with last week, so a
    Monday morning does not "break" a streak that is still alive.
    """
    reference_day = today or date.today()
    summary = weekly_training_summary(sessions, today=reference_day, weeks=max(2, weeks))
    history = weekly_training_summary(sessions, today=reference_day, weeks=52)
    streak = 0
    ordered = list(reversed(history))
    if ordered and ordered[0].sessions == 0:
        ordered = ordered[1:]
    for week in ordered:
        if week.sessions == 0:
            break
        streak += 1
    recent_floor = reference_day - timedelta(days=27)
    recent = Counter(session.kind for session in sessions if session.session_date >= recent_floor)
    favorite = min(recent, key=lambda kind: (-recent[kind], WORKOUT_KINDS.index(kind))) if recent else None
    return TrainingSnapshot(
        this_week=summary[-1],
        last_week=summary[-2],
        weeks=summary[-weeks:] if weeks >= 1 else summary,
        streak_weeks=streak,
        favorite_kind=favorite,
        total_sessions=len(sessions),
    )


def format_training_summary(snapshot: TrainingSnapshot, language: str = "en") -> str:
    """Render a compact, localized terminal summary.

    Example:
        >>> snapshot = build_training_snapshot([], today=date(2026, 10, 19))
        >>> print(format_training_summary(snapshot))  # doctest: +ELLIPSIS
        TRAINING LOG...
    """
    code = normalize_language(language)
    lines = [
        tr(code, "training_report_title"),
        "-" * 64,
        tr(
            code,
            "training_this_week_line",
            minutes=snapshot.this_week.minutes,
            sessions=snapshot.this_week.sessions,
            days=snapshot.this_week.active_days,
        ),
        tr(code, "training_last_week_line", minutes=snapshot.last_week.minutes),
        tr(
            code,
            "training_reference_line",
            percent=snapshot.reference_percent,
            reference=snapshot.reference_minutes,
        ),
        tr(code, "training_streak_line", weeks=snapshot.streak_weeks),
    ]
    if snapshot.favorite_kind:
        lines.append(
            tr(code, "training_favorite_line", kind=tr(code, f"workout_kind_{snapshot.favorite_kind}"))
        )
    lines.append("")
    lines.append(tr(code, "training_weeks_heading"))
    peak = max((week.minutes for week in snapshot.weeks), default=0) or 1
    for week in snapshot.weeks:
        bar = "█" * round(week.minutes * 24 / peak)
        lines.append(f"{week.week_start.isoformat()}  {week.minutes:>4} min  {week.sessions:>2}×  {bar}")
    lines.append("")
    lines.append(tr(code, "training_scope"))
    return "\n".join(lines)


def export_workouts_csv(store: WorkoutStore, path: Path, profile_id: int | None = None) -> int:
    """Write every session of one profile to a UTF-8 CSV file.

    Returns:
        Number of exported sessions.
    """
    sessions = store.list(None, profile_id)
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for session in sessions:
            writer.writerow({key: "" if value is None else value for key, value in session.to_row().items()})
    return len(sessions)


def generate_demo_workouts(
    store: WorkoutStore,
    weeks: int = 6,
    *,
    end_date: date | None = None,
    seed: int = 20261019,
    profile_id: int | None = None,
) -> int:
    """Insert a deterministic, plausible demo training history.

    Args:
        store: Destination store.
        weeks: Number of weeks to generate, 1–52.
        end_date: Latest possible session day; today by default.
        seed: Random seed so screenshots and tests are reproducible.

    Returns:
        Number of inserted sessions.

    Raises:
        ValueError: If ``weeks`` is outside 1–52.
    """
    if not 1 <= weeks <= 52:
        raise ValueError("Demo weeks must be between 1 and 52.")
    generator = random.Random(seed)
    last_day = end_date or date.today()
    first_day = last_day - timedelta(days=weeks * 7 - 1)
    plans = (
        ("walking", (25, 60), (3, 5), (2.0, 5.5)),
        ("running", (20, 45), (5, 8), (3.0, 8.0)),
        ("strength", (30, 55), (6, 8), None),
        ("mobility", (15, 30), (2, 4), None),
        ("cycling", (30, 75), (4, 7), (8.0, 25.0)),
    )
    inserted = 0
    day = first_day
    while day <= last_day:
        if generator.random() < 0.52:
            kind, minutes, effort, distance = plans[generator.randrange(len(plans))]
            store.add(
                WorkoutSession.build(
                    day,
                    kind,
                    generator.randint(*minutes),
                    rpe=generator.randint(*effort),
                    distance_km=None if distance is None else round(generator.uniform(*distance), 1),
                ),
                profile_id,
            )
            inserted += 1
        day += timedelta(days=1)
    return inserted
