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
from .i18n import normalize_language, tr
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


SPARK_KEYS = tuple(f"spark_{index}" for index in range(1, 9))


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
    language = normalize_language(settings.language)
    rows = list(entries)
    stats = calculate_dashboard(rows, settings)
    current_date = today or date.today()
    spark_index = (current_date.toordinal() + stats.entry_count + spark_offset) % len(SPARK_KEYS)
    spark = tr(language, SPARK_KEYS[spark_index])

    if stats.entry_count == 0:
        return MotivationSnapshot(
            headline=tr(language, "motivation_empty_headline"),
            message=tr(language, "motivation_empty_message"),
            daily_spark=spark,
            micro_action=tr(language, "motivation_empty_action"),
            weekly_challenge=tr(language, "motivation_empty_challenge"),
            next_milestone=tr(language, "motivation_first_milestone"),
            milestone_progress_pct=0,
            celebration_level=0,
            achievements=_achievements(stats, language),
        )

    headline = _headline(stats, language)
    message = _message(stats, language)
    micro_action = _micro_action(stats, settings, language)
    challenge = _weekly_challenge(stats, language)
    milestone, progress = _next_milestone(stats, language)
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
        achievements=_achievements(stats, language),
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
    language = normalize_language(settings.language)
    earned = sum(item.earned for item in snapshot.achievements)
    mission = settings.personal_why.strip() or tr(language, "motivation_define_why")
    focus = settings.weekly_focus.strip() or snapshot.weekly_challenge
    return "\n".join(
        (
            tr(language, "motivation_report_title"),
            "=" * 42,
            snapshot.headline,
            snapshot.message,
            "",
            f"{tr(language, 'daily_spark')}: {snapshot.daily_spark}",
            f"{tr(language, 'next_action')}: {snapshot.micro_action}",
            f"{tr(language, 'motivation_weekly_focus')}: {focus}",
            f"{tr(language, 'motivation_next_milestone')}: {snapshot.next_milestone} ({snapshot.milestone_progress_pct}%)",
            f"{tr(language, 'motivation_constellation')}: {earned}/{len(snapshot.achievements)}",
            f"{tr(language, 'personal_why')}: {mission}",
            "",
            tr(language, "motivation_scope"),
        )
    )


def _headline(stats: DashboardStats, language: str) -> str:
    if stats.current_streak_days >= 14:
        return tr(language, "motivation_headline_streak", days=stats.current_streak_days)
    if stats.consistency_score >= 80:
        return tr(language, "motivation_headline_dependable")
    if stats.recent_step_change_pct is not None and stats.recent_step_change_pct > 8:
        return tr(language, "motivation_headline_climbing")
    if stats.active_last_7_days >= 5:
        return tr(language, "motivation_headline_returning")
    return tr(language, "motivation_headline_next")


def _message(stats: DashboardStats, language: str) -> str:
    return tr(
        language,
        "motivation_message",
        entries=stats.entry_count,
        streak=stats.current_streak_days,
        score=stats.consistency_score,
        perfect=stats.perfect_goal_days,
    )


def _micro_action(stats: DashboardStats, settings: AppSettings, language: str) -> str:
    candidates = (
        (stats.tracking_coverage_pct, tr(language, "motivation_action_tracking")),
        (stats.step_goal_rate_pct, tr(language, "motivation_action_steps", goal=f"{settings.step_goal:,}")),
        (
            stats.water_goal_rate_pct,
            tr(language, "motivation_action_water", goal=f"{settings.water_goal_l:.1f}"),
        ),
    )
    return min(candidates, key=lambda item: item[0])[1]


def _weekly_challenge(stats: DashboardStats, language: str) -> str:
    weakest = min(
        (
            (stats.tracking_coverage_pct, "tracking"),
            (stats.step_goal_rate_pct, "steps"),
            (stats.water_goal_rate_pct, "water"),
        ),
        key=lambda item: item[0],
    )[1]
    if weakest == "tracking":
        return tr(language, "motivation_challenge_tracking")
    if weakest == "steps":
        return tr(language, "motivation_challenge_steps")
    return tr(language, "motivation_challenge_water")


def _next_milestone(stats: DashboardStats, language: str) -> tuple[str, int]:
    for target in (3, 7, 14, 30, 60, 90, 180, 365):
        if stats.entry_count < target:
            return tr(language, "motivation_milestone_days", target=target), min(
                99, round((stats.entry_count / target) * 100)
            )
    for target in (3, 7, 14, 30, 60):
        if stats.current_streak_days < target:
            return tr(language, "motivation_milestone_streak", target=target), min(
                99, round((stats.current_streak_days / target) * 100)
            )
    return tr(language, "motivation_archive_complete"), 100


def _achievements(stats: DashboardStats, language: str) -> tuple[Achievement, ...]:
    specifications = (
        ("achievement_first_title", "achievement_first_body", stats.entry_count, 1, "🌱"),
        ("achievement_week_title", "achievement_week_body", stats.entry_count, 7, "🧱"),
        ("achievement_month_title", "achievement_month_body", stats.entry_count, 30, "🗓️"),
        ("achievement_rhythm_title", "achievement_rhythm_body", stats.longest_tracking_streak_days, 7, "🔥"),
        ("achievement_goals_title", "achievement_goals_body", stats.perfect_goal_days, 7, "✨"),
        ("achievement_momentum_title", "achievement_momentum_body", stats.consistency_score, 75, "🚀"),
    )
    return tuple(
        Achievement(
            title=tr(language, title_key),
            description=tr(language, description_key),
            earned=value >= target,
            progress_pct=min(100, round((value / target) * 100)) if target else 100,
            icon=icon,
        )
        for title_key, description_key, value, target, icon in specifications
    )
