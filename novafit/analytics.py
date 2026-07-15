"""
Module: health analytics
Purpose: Derive trustworthy dashboard, consistency, streak, rhythm, and chart summaries.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Minimal deps; comments in ENGLISH; emojis sparingly.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from statistics import mean
from typing import Any, Iterable, Sequence

from .config import AppSettings
from .models import HealthEntry

WEEKDAY_LABELS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")


@dataclass(frozen=True, slots=True)
class DashboardStats:
    """Store calculated dashboard values for CLI and GUI rendering.

    Attributes:
        entry_count: Number of tracked days.
        total_steps: Sum of steps across all entries.
        average_steps: Mean daily steps.
        average_water_l: Mean daily water intake.
        average_calories: Mean calories for entries that provide them.
        step_goal_days: Number of days meeting the step goal.
        water_goal_days: Number of days meeting the hydration goal.
        perfect_goal_days: Number of days meeting both goals.
        current_streak_days: Consecutive tracked days ending at the latest record.
        longest_tracking_streak_days: Longest consecutive tracking sequence.
        longest_goal_streak_days: Longest consecutive sequence meeting both goals.
        best_steps: Highest step count.
        best_date: Date associated with the highest step count.
        recent_step_change_pct: Recent seven-record average change versus the prior seven.
        dominant_mood: Most frequently recorded mood.
        tracking_coverage_pct: Tracked dates divided by the represented calendar span.
        consistency_score: Transparent routine score from tracking and goal completion.
        best_weekday: Weekday with the highest average steps.
        active_last_7_days: Number of tracked days in the latest seven-day window.
        latest_date: Most recent tracked date.

    Example:
        >>> DashboardStats.empty().consistency_score
        0
    """

    entry_count: int
    total_steps: int
    average_steps: int
    average_water_l: float
    average_calories: int | None
    step_goal_days: int
    water_goal_days: int
    perfect_goal_days: int
    current_streak_days: int
    longest_tracking_streak_days: int
    longest_goal_streak_days: int
    best_steps: int
    best_date: str | None
    recent_step_change_pct: float | None
    dominant_mood: str | None
    tracking_coverage_pct: float
    consistency_score: int
    best_weekday: str | None
    active_last_7_days: int
    latest_date: str | None

    @classmethod
    def empty(cls) -> "DashboardStats":
        """Create an all-zero dashboard for an empty database.

        Returns:
            Empty dashboard values.

        Raises:
            None.

        Example:
            >>> DashboardStats.empty().total_steps
            0
        """
        return cls(
            entry_count=0,
            total_steps=0,
            average_steps=0,
            average_water_l=0.0,
            average_calories=None,
            step_goal_days=0,
            water_goal_days=0,
            perfect_goal_days=0,
            current_streak_days=0,
            longest_tracking_streak_days=0,
            longest_goal_streak_days=0,
            best_steps=0,
            best_date=None,
            recent_step_change_pct=None,
            dominant_mood=None,
            tracking_coverage_pct=0.0,
            consistency_score=0,
            best_weekday=None,
            active_last_7_days=0,
            latest_date=None,
        )

    @property
    def step_goal_rate_pct(self) -> float:
        """Return the percentage of entries meeting the step goal.

        Returns:
            Goal-completion percentage from zero to one hundred.

        Raises:
            None.

        Example:
            >>> DashboardStats.empty().step_goal_rate_pct
            0.0
        """
        return 0.0 if not self.entry_count else (self.step_goal_days / self.entry_count) * 100

    @property
    def water_goal_rate_pct(self) -> float:
        """Return the percentage of entries meeting the hydration goal.

        Returns:
            Goal-completion percentage from zero to one hundred.

        Raises:
            None.

        Example:
            >>> DashboardStats.empty().water_goal_rate_pct
            0.0
        """
        return 0.0 if not self.entry_count else (self.water_goal_days / self.entry_count) * 100

    @property
    def perfect_goal_rate_pct(self) -> float:
        """Return the percentage of entries meeting both tracked goals.

        Returns:
            Combined-goal percentage from zero to one hundred.

        Raises:
            None.

        Example:
            >>> DashboardStats.empty().perfect_goal_rate_pct
            0.0
        """
        return 0.0 if not self.entry_count else (self.perfect_goal_days / self.entry_count) * 100

    def to_dict(self) -> dict[str, Any]:
        """Convert dashboard values and derived rates to a serializable dictionary.

        Returns:
            Dictionary containing dashboard fields and percentage properties.

        Raises:
            None.

        Example:
            >>> DashboardStats.empty().to_dict()['entry_count']
            0
        """
        payload = asdict(self)
        payload.update(
            step_goal_rate_pct=round(self.step_goal_rate_pct, 1),
            water_goal_rate_pct=round(self.water_goal_rate_pct, 1),
            perfect_goal_rate_pct=round(self.perfect_goal_rate_pct, 1),
        )
        return payload


@dataclass(frozen=True, slots=True)
class CalendarMatrix:
    """Represent a Monday-first calendar matrix for consistency heatmaps.

    Attributes:
        week_labels: One label per week column.
        weekday_labels: Monday-first row labels.
        values: Routine-score values where ``None`` means no tracked record.
        dates: ISO date labels matching ``values``.

    Example:
        >>> matrix = build_calendar_matrix([], AppSettings(), days=14, end_date=date(2026, 7, 15))
        >>> len(matrix.values)
        7
    """

    week_labels: tuple[str, ...]
    weekday_labels: tuple[str, ...]
    values: tuple[tuple[float | None, ...], ...]
    dates: tuple[tuple[str | None, ...], ...]


def calculate_dashboard(
    entries: Iterable[HealthEntry],
    settings: AppSettings | None = None,
) -> DashboardStats:
    """Calculate reusable summary statistics from health entries.

    Args:
        entries: Any iterable of validated records.
        settings: Goal preferences; defaults are used when omitted.

    Returns:
        A complete dashboard summary.

    Raises:
        ValueError: If supplied settings are invalid.

    Example:
        >>> item = HealthEntry.build('2026-07-15', 10000, 2.5, 2000, 'Focused')
        >>> calculate_dashboard([item]).perfect_goal_days
        1
    """
    active_settings = (settings or AppSettings()).validate()
    rows = _sorted_unique(entries)
    if not rows:
        return DashboardStats.empty()

    calorie_values = [item.calories for item in rows if item.calories is not None]
    best = max(rows, key=lambda item: (item.steps, item.entry_date))
    mood_counts = Counter(item.mood for item in rows if item.mood)
    first_date = rows[0].entry_date
    latest_date = rows[-1].entry_date
    represented_days = max(1, (latest_date - first_date).days + 1)
    coverage = min(100.0, (len(rows) / represented_days) * 100)

    step_goal_days = sum(item.steps >= active_settings.step_goal for item in rows)
    water_goal_days = sum(item.water_l >= active_settings.water_goal_l for item in rows)
    perfect_goal_days = sum(_meets_both_goals(item, active_settings) for item in rows)
    recent_window_start = latest_date - timedelta(days=6)
    active_last_7 = sum(item.entry_date >= recent_window_start for item in rows)

    # 💡 This is a transparent routine score, not a medical or fitness assessment.
    step_rate = (step_goal_days / len(rows)) * 100
    water_rate = (water_goal_days / len(rows)) * 100
    recent_rate = (active_last_7 / 7) * 100
    consistency_score = round(
        (coverage * 0.30)
        + (step_rate * 0.25)
        + (water_rate * 0.25)
        + (recent_rate * 0.20)
    )

    return DashboardStats(
        entry_count=len(rows),
        total_steps=sum(item.steps for item in rows),
        average_steps=round(mean(item.steps for item in rows)),
        average_water_l=round(mean(item.water_l for item in rows), 2),
        average_calories=round(mean(calorie_values)) if calorie_values else None,
        step_goal_days=step_goal_days,
        water_goal_days=water_goal_days,
        perfect_goal_days=perfect_goal_days,
        current_streak_days=calculate_tracking_streak(rows),
        longest_tracking_streak_days=calculate_longest_tracking_streak(rows),
        longest_goal_streak_days=calculate_longest_goal_streak(rows, active_settings),
        best_steps=best.steps,
        best_date=best.entry_date.isoformat(),
        recent_step_change_pct=calculate_recent_change(rows),
        dominant_mood=mood_counts.most_common(1)[0][0] if mood_counts else None,
        tracking_coverage_pct=round(coverage, 1),
        consistency_score=max(0, min(100, consistency_score)),
        best_weekday=_best_weekday(rows),
        active_last_7_days=active_last_7,
        latest_date=latest_date.isoformat(),
    )


def calculate_tracking_streak(entries: Iterable[HealthEntry]) -> int:
    """Calculate consecutive tracked dates ending at the newest record.

    Args:
        entries: Health entries in any order.

    Returns:
        Number of consecutive calendar days represented at the end of the data.

    Raises:
        None.

    Example:
        >>> rows = [HealthEntry.build('2026-07-14', 1, 1), HealthEntry.build('2026-07-15', 1, 1)]
        >>> calculate_tracking_streak(rows)
        2
    """
    unique_dates = sorted({item.entry_date for item in entries}, reverse=True)
    if not unique_dates:
        return 0
    streak = 1
    expected = unique_dates[0] - timedelta(days=1)
    for tracked_date in unique_dates[1:]:
        if tracked_date != expected:
            break
        streak += 1
        expected -= timedelta(days=1)
    return streak


def calculate_longest_tracking_streak(entries: Iterable[HealthEntry]) -> int:
    """Calculate the longest consecutive sequence of tracked dates.

    Args:
        entries: Health entries in any order.

    Returns:
        Longest tracking streak in calendar days.

    Raises:
        None.

    Example:
        >>> rows = [HealthEntry.build('2026-07-13', 1, 1), HealthEntry.build('2026-07-14', 1, 1)]
        >>> calculate_longest_tracking_streak(rows)
        2
    """
    dates = sorted({item.entry_date for item in entries})
    if not dates:
        return 0
    longest = current = 1
    for previous, current_date in zip(dates, dates[1:]):
        if current_date == previous + timedelta(days=1):
            current += 1
            longest = max(longest, current)
        else:
            current = 1
    return longest


def calculate_longest_goal_streak(
    entries: Iterable[HealthEntry],
    settings: AppSettings,
) -> int:
    """Calculate the longest consecutive run meeting both daily goals.

    Args:
        entries: Health entries in any order.
        settings: Step and hydration goals.

    Returns:
        Longest calendar-day streak where both goals were met.

    Raises:
        ValueError: If settings are invalid.

    Example:
        >>> rows = [HealthEntry.build('2026-07-14', 10000, 2), HealthEntry.build('2026-07-15', 10000, 2)]
        >>> calculate_longest_goal_streak(rows, AppSettings())
        2
    """
    settings.validate()
    rows = _sorted_unique(entries)
    longest = current = 0
    previous_date: date | None = None
    for entry in rows:
        meets = _meets_both_goals(entry, settings)
        consecutive = previous_date is not None and entry.entry_date == previous_date + timedelta(days=1)
        if meets:
            current = current + 1 if consecutive else 1
            longest = max(longest, current)
        else:
            current = 0
        previous_date = entry.entry_date
    return longest


def calculate_recent_change(entries: Iterable[HealthEntry]) -> float | None:
    """Compare recent and previous seven-record average steps.

    Args:
        entries: Health entries in any order.

    Returns:
        Percentage change, or ``None`` when fewer than fourteen records exist.

    Raises:
        None.

    Example:
        >>> calculate_recent_change([]) is None
        True
    """
    rows = _sorted_unique(entries)
    if len(rows) < 14:
        return None
    recent = mean(item.steps for item in rows[-7:])
    previous = mean(item.steps for item in rows[-14:-7])
    if previous == 0:
        return 100.0 if recent > 0 else 0.0
    return round(((recent - previous) / previous) * 100, 1)


def build_daily_series(
    entries: Iterable[HealthEntry],
    days: int = 14,
    *,
    end_date: date | None = None,
) -> list[dict[str, Any]]:
    """Build a gap-aware daily series for charts and progress views.

    Args:
        entries: Health records in any order.
        days: Number of calendar days to include.
        end_date: Last day in the series; latest tracked date is used by default.

    Returns:
        List of dictionaries containing date, steps, water, calories, and mood.

    Raises:
        ValueError: If ``days`` is outside the supported 1–365 range.

    Example:
        >>> len(build_daily_series([], 3, end_date=date(2026, 7, 15)))
        3
    """
    if not 1 <= days <= 365:
        raise ValueError("Days must be between 1 and 365.")
    rows = _sorted_unique(entries)
    inferred_end = max((item.entry_date for item in rows), default=date.today())
    final_day = end_date or inferred_end
    by_date = {item.entry_date: item for item in rows}

    series: list[dict[str, Any]] = []
    first_day = final_day - timedelta(days=days - 1)
    for offset in range(days):
        current = first_day + timedelta(days=offset)
        entry = by_date.get(current)
        series.append(
            {
                "date": current.isoformat(),
                "steps": entry.steps if entry else 0,
                "water_l": entry.water_l if entry else 0.0,
                "calories": entry.calories if entry else None,
                "mood": entry.mood if entry else None,
                "tracked": entry is not None,
            }
        )
    return series


def rolling_average(values: Sequence[float | int], window: int = 7) -> list[float | None]:
    """Calculate a trailing rolling average without external data libraries.

    Args:
        values: Numeric values in chronological order.
        window: Positive trailing-window size.

    Returns:
        One value per input position; early positions are ``None`` until full.

    Raises:
        ValueError: If ``window`` is not positive.

    Example:
        >>> rolling_average([1, 2, 3], 2)
        [None, 1.5, 2.5]
    """
    if window <= 0:
        raise ValueError("Rolling-average window must be positive.")
    result: list[float | None] = []
    for index in range(len(values)):
        start = index - window + 1
        if start < 0:
            result.append(None)
            continue
        result.append(round(mean(values[start : index + 1]), 2))
    return result


def build_weekday_profile(entries: Iterable[HealthEntry]) -> list[dict[str, Any]]:
    """Aggregate average steps and hydration by weekday.

    Args:
        entries: Health records in any order.

    Returns:
        Seven Monday-first dictionaries with counts and averages.

    Raises:
        None.

    Example:
        >>> len(build_weekday_profile([]))
        7
    """
    step_values: dict[int, list[int]] = defaultdict(list)
    water_values: dict[int, list[float]] = defaultdict(list)
    for item in entries:
        weekday = item.entry_date.weekday()
        step_values[weekday].append(item.steps)
        water_values[weekday].append(item.water_l)
    return [
        {
            "weekday": WEEKDAY_LABELS[index],
            "count": len(step_values[index]),
            "average_steps": round(mean(step_values[index])) if step_values[index] else 0,
            "average_water_l": round(mean(water_values[index]), 2) if water_values[index] else 0.0,
        }
        for index in range(7)
    ]


def build_mood_distribution(
    entries: Iterable[HealthEntry],
    *,
    limit: int = 6,
) -> list[tuple[str, int]]:
    """Return the most common normalized mood labels.

    Args:
        entries: Health records in any order.
        limit: Maximum labels to return.

    Returns:
        ``(mood, count)`` pairs ordered by frequency and name.

    Raises:
        ValueError: If ``limit`` is not positive.

    Example:
        >>> build_mood_distribution([HealthEntry.build('2026-07-15', 1, 1, mood='Calm')])
        [('Calm', 1)]
    """
    if limit <= 0:
        raise ValueError("Mood limit must be positive.")
    counts = Counter((item.mood or "Not recorded").strip() or "Not recorded" for item in entries)
    return sorted(counts.items(), key=lambda pair: (-pair[1], pair[0].lower()))[:limit]


def build_calendar_matrix(
    entries: Iterable[HealthEntry],
    settings: AppSettings,
    *,
    days: int = 84,
    end_date: date | None = None,
) -> CalendarMatrix:
    """Build a Monday-first goal-consistency calendar for heatmaps.

    Args:
        entries: Health records in any order.
        settings: Goals used to score each tracked day.
        days: Requested history; rounded up to complete Monday-first weeks.
        end_date: Optional final date for deterministic tests.

    Returns:
        A seven-row calendar matrix with zero-to-one routine scores.

    Raises:
        ValueError: If settings or day range is invalid.

    Example:
        >>> matrix = build_calendar_matrix([], AppSettings(), days=14, end_date=date(2026, 7, 15))
        >>> len(matrix.weekday_labels)
        7
    """
    settings.validate()
    if not 7 <= days <= 365:
        raise ValueError("Calendar days must be between 7 and 365.")
    rows = _sorted_unique(entries)
    latest = end_date or max((item.entry_date for item in rows), default=date.today())
    final_sunday = latest + timedelta(days=(6 - latest.weekday()))
    requested_start = latest - timedelta(days=days - 1)
    first_monday = requested_start - timedelta(days=requested_start.weekday())
    week_count = ((final_sunday - first_monday).days + 1) // 7
    by_date = {item.entry_date: item for item in rows}

    values: list[list[float | None]] = [[None for _ in range(week_count)] for _ in range(7)]
    dates: list[list[str | None]] = [[None for _ in range(week_count)] for _ in range(7)]
    week_labels: list[str] = []

    for week in range(week_count):
        monday = first_monday + timedelta(days=week * 7)
        week_labels.append(monday.strftime("%b %d"))
        for weekday in range(7):
            current = monday + timedelta(days=weekday)
            if current > latest:
                continue
            dates[weekday][week] = current.isoformat()
            entry = by_date.get(current)
            values[weekday][week] = None if entry is None else _routine_day_score(entry, settings)

    return CalendarMatrix(
        week_labels=tuple(week_labels),
        weekday_labels=WEEKDAY_LABELS,
        values=tuple(tuple(row) for row in values),
        dates=tuple(tuple(row) for row in dates),
    )


def build_insight_lines(stats: DashboardStats, settings: AppSettings) -> list[str]:
    """Create concise evidence-based observations for GUI and reports.

    Args:
        stats: Calculated dashboard snapshot.
        settings: Active goals used to contextualize the observations.

    Returns:
        Four short descriptive insights without medical interpretation.

    Raises:
        ValueError: If settings are invalid.

    Example:
        >>> len(build_insight_lines(DashboardStats.empty(), AppSettings()))
        4
    """
    settings.validate()
    if stats.entry_count == 0:
        return [
            "Add your first record to activate the analytics studio.",
            "JSON and CSV exports keep your local data portable.",
            "Weather requests never contain health entries or notes.",
            "The routine score is a transparent habit signal, not medical advice.",
        ]

    trend = (
        "A 14-record history unlocks recent-versus-previous trend comparison."
        if stats.recent_step_change_pct is None
        else f"Recent average steps changed {stats.recent_step_change_pct:+.1f}% versus the prior seven records."
    )
    rhythm = (
        f"Your strongest average movement day is {stats.best_weekday}."
        if stats.best_weekday
        else "More records are needed to identify a weekday rhythm."
    )
    return [
        f"Both primary goals were reached on {stats.perfect_goal_rate_pct:.0f}% of tracked days.",
        f"Tracking coverage is {stats.tracking_coverage_pct:.0f}% with a longest streak of {stats.longest_tracking_streak_days} day(s).",
        trend,
        f"{rhythm} Most recorded mood: {stats.dominant_mood or 'not available'}.",
    ]

def format_dashboard(stats: DashboardStats, settings: AppSettings) -> str:
    """Format dashboard values as a compact terminal report.

    Args:
        stats: Calculated dashboard values.
        settings: Goals used to contextualize progress.

    Returns:
        Human-readable multiline report.

    Raises:
        ValueError: If settings are invalid.

    Example:
        >>> 'Tracked days' in format_dashboard(DashboardStats.empty(), AppSettings())
        False
    """
    settings.validate()
    if stats.entry_count == 0:
        return "No health entries yet. Add a record or seed demo data to begin. 💙"

    change = (
        "Not enough history"
        if stats.recent_step_change_pct is None
        else f"{stats.recent_step_change_pct:+.1f}% vs previous 7 records"
    )
    calories = "N/A" if stats.average_calories is None else f"{stats.average_calories:,}"

    return "\n".join(
        [
            "NovaFit Ultimate 4.0 — Wellness Command Center",
            "=" * 56,
            f"Tracked days: {stats.entry_count} | coverage {stats.tracking_coverage_pct:.0f}%",
            f"Routine consistency score: {stats.consistency_score}/100",
            f"Total steps: {stats.total_steps:,}",
            f"Average steps: {stats.average_steps:,} / goal {settings.step_goal:,}",
            f"Average water: {stats.average_water_l:.2f} L / goal {settings.water_goal_l:.1f} L",
            f"Average calories: {calories}",
            f"Step goal success: {stats.step_goal_days}/{stats.entry_count} ({stats.step_goal_rate_pct:.0f}%)",
            f"Water goal success: {stats.water_goal_days}/{stats.entry_count} ({stats.water_goal_rate_pct:.0f}%)",
            f"Perfect goal days: {stats.perfect_goal_days}/{stats.entry_count} ({stats.perfect_goal_rate_pct:.0f}%)",
            f"Current tracking streak: {stats.current_streak_days} day(s)",
            f"Longest tracking streak: {stats.longest_tracking_streak_days} day(s)",
            f"Longest combined-goal streak: {stats.longest_goal_streak_days} day(s)",
            f"Best day: {stats.best_steps:,} steps on {stats.best_date}",
            f"Best weekday by average steps: {stats.best_weekday or 'Not available'}",
            f"Recent trend: {change}",
            f"Dominant mood: {stats.dominant_mood or 'Not recorded'}",
        ]
    )


def _sorted_unique(entries: Iterable[HealthEntry]) -> list[HealthEntry]:
    """Return chronologically sorted records with one entry per date."""
    by_date = {item.entry_date: item for item in entries}
    return [by_date[key] for key in sorted(by_date)]


def _meets_both_goals(entry: HealthEntry, settings: AppSettings) -> bool:
    """Return whether one record meets both primary goals."""
    return entry.steps >= settings.step_goal and entry.water_l >= settings.water_goal_l


def _routine_day_score(entry: HealthEntry, settings: AppSettings) -> float:
    """Score a tracked day using capped step and hydration goal ratios."""
    step_ratio = min(1.0, entry.steps / settings.step_goal)
    water_ratio = min(1.0, entry.water_l / settings.water_goal_l)
    return round((step_ratio + water_ratio) / 2, 3)


def _best_weekday(entries: Sequence[HealthEntry]) -> str | None:
    """Return the weekday with the highest average step count."""
    profile = build_weekday_profile(entries)
    populated = [row for row in profile if row["count"]]
    if not populated:
        return None
    return max(populated, key=lambda row: (row["average_steps"], -WEEKDAY_LABELS.index(row["weekday"])))[
        "weekday"
    ]
