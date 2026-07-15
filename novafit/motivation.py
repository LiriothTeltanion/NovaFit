"""
Module: motivation engine
Purpose: Translate transparent NovaFit metrics into encouraging, non-medical
    progress messages, milestones, achievements, and small weekly challenges.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Deterministic, offline, and grounded only in stored user records.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable

from .analytics import DashboardStats, calculate_dashboard
from .config import AppSettings
from .models import HealthEntry


@dataclass(frozen=True, slots=True)
class Achievement:
    """Represent one earned or upcoming motivation badge.

    Args:
        title: Short badge title.
        description: Evidence-based explanation.
        earned: Whether the condition is currently satisfied.
        progress_pct: Progress toward the badge from zero to one hundred.
        icon: Small decorative symbol.

    Example:
        >>> Achievement("First Step", "Track one day.", True, 100, "🌱").earned
        True
    """

    title: str
    description: str
    earned: bool
    progress_pct: int
    icon: str


@dataclass(frozen=True, slots=True)
class MotivationSnapshot:
    """Store all copy and progress signals needed by the Motivation Center.

    Args:
        headline: Primary encouraging statement.
        message: Grounded explanation.
        daily_spark: Deterministic original motivation line.
        micro_action: Small next action.
        weekly_challenge: Seven-day challenge based on the weakest tracked signal.
        next_milestone: Closest measurable milestone.
        milestone_progress_pct: Progress toward the next milestone.
        celebration_level: Visual celebration intensity from zero to three.
        achievements: Earned and upcoming badges.

    Example:
        >>> build_motivation_snapshot([], AppSettings()).celebration_level
        0
    """

    headline: str
    message: str
    daily_spark: str
    micro_action: str
    weekly_challenge: str
    next_milestone: str
    milestone_progress_pct: int
    celebration_level: int
    achievements: tuple[Achievement, ...]


SPARKS = (
    "Small records become strong evidence when you keep showing up.",
    "A calm system beats a perfect day. Build the next repeatable step.",
    "Progress is easier to trust when you can see it clearly.",
    "Consistency is not intensity every day; it is returning with intention.",
    "Your data is a mirror, not a judge. Use it to choose the next useful action.",
    "One honest entry today protects the story your future self will need.",
    "Momentum grows when the next action is small enough to begin now.",
    "Build steadily, recover deliberately, and let the evidence accumulate.",
)


def build_motivation_snapshot(
    entries: Iterable[HealthEntry],
    settings: AppSettings,
    *,
    today: date | None = None,
    spark_offset: int = 0,
) -> MotivationSnapshot:
    """Build a deterministic motivation snapshot from local records.

    Args:
        entries: Health records in any order.
        settings: Goals and personal motivation preferences.
        today: Optional date override for repeatable tests.
        spark_offset: Manual rotation offset used by the GUI's ``New spark`` button.

    Returns:
        Grounded motivation snapshot.

    Raises:
        ValueError: If settings are invalid.

    Example:
        >>> build_motivation_snapshot([], AppSettings()).headline
        'Begin with one honest record.'
    """
    settings.validate()
    rows = list(entries)
    stats = calculate_dashboard(rows, settings)
    current_date = today or date.today()
    spark_index = (current_date.toordinal() + stats.entry_count + spark_offset) % len(SPARKS)
    spark = SPARKS[spark_index]

    if stats.entry_count == 0:
        return MotivationSnapshot(
            headline="Begin with one honest record.",
            message="NovaFit has no history yet. One entry is enough to unlock your first dashboard and badge.",
            daily_spark=spark,
            micro_action="Record today's steps, water, mood, and one private note.",
            weekly_challenge="Track three days this week. Accuracy matters more than perfection.",
            next_milestone="First tracked day",
            milestone_progress_pct=0,
            celebration_level=0,
            achievements=_achievements(stats),
        )

    headline = _headline(stats)
    message = _message(stats)
    micro_action = _micro_action(stats, settings)
    challenge = _weekly_challenge(stats)
    milestone, progress = _next_milestone(stats)
    celebration = 3 if stats.consistency_score >= 85 else 2 if stats.consistency_score >= 65 else 1
    return MotivationSnapshot(
        headline=headline,
        message=message,
        daily_spark=spark,
        micro_action=micro_action,
        weekly_challenge=challenge,
        next_milestone=milestone,
        milestone_progress_pct=progress,
        celebration_level=celebration,
        achievements=_achievements(stats),
    )


def format_motivation(snapshot: MotivationSnapshot, settings: AppSettings) -> str:
    """Format a motivation snapshot for terminal output.

    Args:
        snapshot: Snapshot produced by ``build_motivation_snapshot``.
        settings: Personal mission and weekly focus settings.

    Returns:
        Multi-line terminal summary.

    Example:
        >>> "MOTIVATION CENTER" in format_motivation(build_motivation_snapshot([], AppSettings()), AppSettings())
        True
    """
    earned = sum(item.earned for item in snapshot.achievements)
    mission = settings.personal_why.strip() or "Define your personal why in the desktop Motivation Center."
    focus = settings.weekly_focus.strip() or snapshot.weekly_challenge
    return "\n".join(
        (
            "NOVA MOTIVATION CENTER & RECOVERY LAB",
            "=" * 42,
            snapshot.headline,
            snapshot.message,
            "",
            f"Daily spark: {snapshot.daily_spark}",
            f"Next action: {snapshot.micro_action}",
            f"Weekly focus: {focus}",
            f"Next milestone: {snapshot.next_milestone} ({snapshot.milestone_progress_pct}%)",
            f"Achievements: {earned}/{len(snapshot.achievements)}",
            f"Personal why: {mission}",
            "",
            "This is encouragement from your own tracking data, not medical advice.",
        )
    )


def _headline(stats: DashboardStats) -> str:
    if stats.current_streak_days >= 14:
        return f"A {stats.current_streak_days}-day rhythm is real momentum."
    if stats.consistency_score >= 80:
        return "Your system is becoming dependable."
    if stats.recent_step_change_pct is not None and stats.recent_step_change_pct > 8:
        return "Your recent movement trend is climbing."
    if stats.active_last_7_days >= 5:
        return "You kept returning this week."
    return "The next useful day can change the pattern."


def _message(stats: DashboardStats) -> str:
    return (
        f"You have {stats.entry_count} tracked day(s), {stats.current_streak_days} in the current streak, "
        f"and a transparent routine score of {stats.consistency_score}/100. "
        f"Both configured goals were met on {stats.perfect_goal_days} tracked day(s)."
    )


def _micro_action(stats: DashboardStats, settings: AppSettings) -> str:
    candidates = (
        (stats.tracking_coverage_pct, "Protect the record: add today's entry before the day ends."),
        (stats.step_goal_rate_pct, f"Choose one realistic movement block toward {settings.step_goal:,} steps."),
        (stats.water_goal_rate_pct, f"Make the next glass visible and work toward {settings.water_goal_l:.1f} L."),
    )
    return min(candidates, key=lambda item: item[0])[1]


def _weekly_challenge(stats: DashboardStats) -> str:
    weakest = min(
        (
            (stats.tracking_coverage_pct, "tracking"),
            (stats.step_goal_rate_pct, "steps"),
            (stats.water_goal_rate_pct, "water"),
        ),
        key=lambda item: item[0],
    )[1]
    if weakest == "tracking":
        return "Complete five short check-ins across the next seven days."
    if weakest == "steps":
        return "Add one intentional walk or movement break on four days this week."
    return "Use a visible hydration cue and record the result on five days this week."


def _next_milestone(stats: DashboardStats) -> tuple[str, int]:
    for target in (3, 7, 14, 30, 60, 90, 180, 365):
        if stats.entry_count < target:
            return f"{target} tracked days", min(99, round((stats.entry_count / target) * 100))
    for target in (3, 7, 14, 30, 60):
        if stats.current_streak_days < target:
            return f"{target}-day tracking streak", min(99, round((stats.current_streak_days / target) * 100))
    return "365-day archive complete", 100


def _achievements(stats: DashboardStats) -> tuple[Achievement, ...]:
    specifications = (
        ("First Signal", "Track the first day.", stats.entry_count, 1, "🌱"),
        ("Week Builder", "Collect seven tracked days.", stats.entry_count, 7, "🧱"),
        ("Month of Evidence", "Collect thirty tracked days.", stats.entry_count, 30, "🗓️"),
        ("Rhythm Keeper", "Reach a seven-day tracking streak.", stats.longest_tracking_streak_days, 7, "🔥"),
        ("Goal Fusion", "Meet both goals on seven dates.", stats.perfect_goal_days, 7, "✨"),
        ("Momentum 75", "Reach a routine score of 75.", stats.consistency_score, 75, "🚀"),
    )
    return tuple(
        Achievement(
            title=title,
            description=description,
            earned=value >= target,
            progress_pct=min(100, round((value / target) * 100)) if target else 100,
            icon=icon,
        )
        for title, description, value, target, icon in specifications
    )
