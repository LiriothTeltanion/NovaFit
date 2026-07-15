"""
Module: analytics chart rendering
Purpose: Build ambitious, exportable Matplotlib dashboards without coupling storage to UI.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Matplotlib is the only visualization dependency; comments in ENGLISH.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from . import __version__
from .analytics import (
    build_calendar_matrix,
    build_daily_series,
    build_mood_distribution,
    build_weekday_profile,
    calculate_dashboard,
    rolling_average,
)
from .config import AppSettings
from .models import HealthEntry
from .themes import get_theme

CHART_VIEWS: Mapping[str, str] = {
    "command_center": "Command Center",
    "trend_lab": "Trend Lab",
    "consistency_map": "Consistency Map",
    "training_atlas": "Training Atlas",
}
USER_VIEWS: tuple[str, ...] = ("overview", "trends", "consistency", "atlas")
SUPPORTED_VIEWS: tuple[str, ...] = USER_VIEWS + tuple(CHART_VIEWS)


@dataclass(frozen=True, slots=True)
class ChartTheme:
    """Describe one complete chart palette.

    Attributes:
        background: Figure background.
        panel: Plot-panel background.
        panel_alt: Secondary panel surface.
        text: Primary text.
        muted: Secondary text.
        grid: Grid and separator color.
        cyan: Movement accent.
        blue: Secondary movement accent.
        purple: Identity and rolling-average accent.
        green: Success accent.
        amber: Reference and caution accent.
        pink: Mood and emphasis accent.
        red: Negative or below-goal accent.

    Example:
        >>> resolve_chart_theme('dark').cyan
        '#22d3ee'
    """

    background: str
    panel: str
    panel_alt: str
    text: str
    muted: str
    grid: str
    cyan: str
    blue: str
    purple: str
    green: str
    amber: str
    pink: str
    red: str


DARK_THEME = ChartTheme(**dict(get_theme("midnight").chart))

LIGHT_THEME = ChartTheme(**dict(get_theme("cloud").chart))


def resolve_chart_theme(theme: str | ChartTheme) -> ChartTheme:
    """Resolve any NovaFit theme name or return a supplied palette.

    Args:
        theme: Stable theme identifier, legacy ``dark``/``light`` alias, display
            label, or an explicit ``ChartTheme``.

    Returns:
        Chart palette ready for rendering.

    Raises:
        ValueError: If a string theme is unsupported.

    Example:
        >>> resolve_chart_theme('aurora').green
        '#4ade80'
    """
    if isinstance(theme, ChartTheme):
        return theme
    definition = get_theme(theme)
    return ChartTheme(**dict(definition.chart))


def normalize_chart_view(view: str) -> str:
    """Normalize a user-facing chart-view value to its stable identifier.

    Args:
        view: Identifier or display label.

    Returns:
        One key from ``CHART_VIEWS``.

    Raises:
        ValueError: If the view is unsupported.

    Example:
        >>> normalize_chart_view('Trend Lab')
        'trend_lab'
    """
    normalized = view.strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "overview": "command_center",
        "goals": "trend_lab",
        "calendar": "consistency_map",
        "patterns": "trend_lab",
        "trends": "trend_lab",
        "consistency": "consistency_map",
        "atlas": "training_atlas",
        "training": "training_atlas",
        "sport": "training_atlas",
    }
    normalized = aliases.get(normalized, normalized)
    for key, label in CHART_VIEWS.items():
        if normalized in {key, label.lower().replace(" ", "_")}:
            return key
    raise ValueError(f"Unsupported chart view: {view}")


def create_dashboard_figure(
    entries: Iterable[HealthEntry],
    settings: AppSettings,
    *,
    view: str = "command_center",
    theme: str | ChartTheme = "dark",
    days: int | None = None,
    figure_size: tuple[float, float] | None = None,
) -> Any:
    """Create one of NovaFit's definitive analytics dashboards.

    Args:
        entries: Health records in any order.
        settings: Goal lines and chart preferences.
        view: ``command_center``, ``trend_lab``, or ``consistency_map``.
        theme: Dark, light, or an explicit palette.
        days: Optional history-range override.
        figure_size: Optional Matplotlib size in inches for embedded canvases.

    Returns:
        A Matplotlib ``Figure`` object.

    Raises:
        ImportError: If Matplotlib is not installed.
        ValueError: If view, theme, settings, or day range is invalid.

    Example:
        >>> figure = create_dashboard_figure([], AppSettings(), days=14)
        >>> len(figure.axes) >= 4
        True
    """
    settings.validate()
    selected_days = days or settings.chart_days
    if not 7 <= selected_days <= 365:
        raise ValueError("Chart days must be between 7 and 365.")
    selected_view = normalize_chart_view(view)
    palette = resolve_chart_theme(theme)
    rows = list(entries)

    if selected_view == "command_center":
        return _create_command_center(rows, settings, palette, selected_days, figure_size)
    if selected_view == "trend_lab":
        return _create_trend_lab(rows, settings, palette, selected_days, figure_size)
    if selected_view == "consistency_map":
        return _create_consistency_map(rows, settings, palette, selected_days, figure_size)
    return _create_training_atlas(rows, settings, palette, selected_days, figure_size)


def create_progress_figure(
    entries: Iterable[HealthEntry],
    settings: AppSettings,
    *,
    days: int | None = None,
) -> Any:
    """Create the primary command-center figure for backward compatibility.

    Args:
        entries: Health records in any order.
        settings: Goal lines and chart preferences.
        days: Optional history-range override.

    Returns:
        NovaFit command-center ``Figure``.

    Raises:
        ImportError: If Matplotlib is not installed.
        ValueError: If settings or days are invalid.

    Example:
        >>> len(create_progress_figure([], AppSettings(), days=7).axes) >= 4
        True
    """
    return create_dashboard_figure(entries, settings, view="command_center", theme=settings.theme, days=days)


def save_dashboard_chart(
    entries: Iterable[HealthEntry],
    settings: AppSettings,
    destination: Path,
    *,
    view: str = "command_center",
    theme: str | ChartTheme | None = None,
    days: int | None = None,
    dpi: int = 180,
) -> Path:
    """Save a high-resolution dashboard PNG for sharing or documentation.

    Args:
        entries: Health records in any order.
        settings: Goal and chart preferences.
        destination: PNG output path.
        view: Dashboard view identifier or label.
        theme: Optional theme override; settings theme is used by default.
        days: Optional history-range override.
        dpi: Output resolution between 72 and 400.

    Returns:
        Written PNG path.

    Raises:
        ImportError: If Matplotlib is not installed.
        ValueError: If view, theme, days, or DPI is invalid.
        OSError: If the destination cannot be written.

    Example:
        >>> save_dashboard_chart([], AppSettings(), Path('data/chart.png'), days=7).suffix
        '.png'
    """
    if not 72 <= dpi <= 400:
        raise ValueError("Chart DPI must be between 72 and 400.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure = create_dashboard_figure(
        entries,
        settings,
        view=view,
        theme=theme or settings.theme,
        days=days,
    )
    figure.savefig(
        destination,
        format="png",
        dpi=dpi,
        bbox_inches="tight",
        facecolor=figure.get_facecolor(),
    )
    return destination


def save_progress_chart(
    entries: Iterable[HealthEntry],
    settings: AppSettings,
    destination: Path,
    *,
    days: int | None = None,
) -> Path:
    """Save the primary command-center PNG using the historical API name.

    Args:
        entries: Health records in any order.
        settings: Goal and chart preferences.
        destination: PNG output path.
        days: Optional history-range override.

    Returns:
        Written PNG path.

    Raises:
        ImportError: If Matplotlib is not installed.
        OSError: If the destination cannot be written.

    Example:
        >>> save_progress_chart([], AppSettings(), Path('data/chart.png'), days=7).name
        'chart.png'
    """
    return save_dashboard_chart(entries, settings, destination, days=days)


def create_analytics_figure(
    entries: Iterable[HealthEntry],
    settings: AppSettings,
    *,
    view: str = "command_center",
    theme: str | ChartTheme | None = None,
    days: int | None = None,
) -> Any:
    """Create a definitive analytics figure using the public studio API.

    Args:
        entries: Health records in any order.
        settings: Goal and chart preferences.
        view: Dashboard view identifier or supported alias.
        theme: Optional dark/light palette override.
        days: Optional history-range override.

    Returns:
        A Matplotlib ``Figure`` object.

    Raises:
        ValueError: If view, theme, settings, or range is invalid.
        ImportError: If Matplotlib is unavailable.

    Example:
        >>> len(create_analytics_figure([], AppSettings(), days=7).axes) >= 4
        True
    """
    return create_dashboard_figure(
        entries,
        settings,
        view=view,
        theme=theme or settings.theme,
        days=days,
    )


def save_analytics_chart(
    entries: Iterable[HealthEntry],
    settings: AppSettings,
    destination: Path,
    *,
    view: str = "command_center",
    theme: str | ChartTheme | None = None,
    days: int | None = None,
    dpi: int = 180,
) -> Path:
    """Save a definitive analytics view using the public studio API.

    Args:
        entries: Health records in any order.
        settings: Goal and chart preferences.
        destination: PNG output path.
        view: Dashboard view identifier or supported alias.
        theme: Optional theme override.
        days: Optional history-range override.
        dpi: Output resolution.

    Returns:
        Written PNG path.

    Raises:
        ValueError: If view, theme, days, or DPI is invalid.
        OSError: If the destination cannot be written.

    Example:
        >>> save_analytics_chart([], AppSettings(), Path('data/chart.png'), days=7).suffix
        '.png'
    """
    return save_dashboard_chart(
        entries,
        settings,
        destination,
        view=view,
        theme=theme,
        days=days,
        dpi=dpi,
    )


def _create_command_center(
    entries: Sequence[HealthEntry],
    settings: AppSettings,
    palette: ChartTheme,
    days: int,
    figure_size: tuple[float, float] | None = None,
) -> Any:
    """Render the multi-panel executive health command center."""
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.figure import Figure
    from matplotlib.gridspec import GridSpec
    from matplotlib.patches import Wedge
    from matplotlib.ticker import FuncFormatter

    series = build_daily_series(entries, days)
    stats = calculate_dashboard(entries, settings)
    labels = [row["date"][5:] for row in series]
    positions = list(range(len(series)))
    steps = [row["steps"] for row in series]
    water = [row["water_l"] for row in series]
    tracked = [bool(row["tracked"]) for row in series]
    step_average = rolling_average(steps, min(7, len(steps)))
    water_average = rolling_average(water, min(7, len(water)))

    figure = Figure(figsize=figure_size or (14.8, 8.5), dpi=100, facecolor=palette.background)
    compact = figure.get_figwidth() < 10.0 or figure.get_figheight() < 6.0
    grid = GridSpec(
        9,
        12,
        figure=figure,
        left=0.085 if compact else 0.045,
        right=0.975 if compact else 0.985,
        top=0.78 if compact else 0.815,
        bottom=0.115 if compact else 0.085,
        wspace=0.72 if compact else 0.62,
        hspace=1.8 if compact else 0.95,
    )
    movement_axis = figure.add_subplot(grid[0:3, 0:8])
    goal_axis = figure.add_subplot(grid[0:3, 8:12])
    hydration_axis = figure.add_subplot(grid[3:6, 0:8])
    rhythm_axis: Any = figure.add_subplot(grid[3:6, 8:12], projection="polar")
    mood_axis = figure.add_subplot(grid[6:9, 0:4])
    heat_axis = figure.add_subplot(grid[6:9, 4:12])

    _figure_header(
        figure,
        palette,
        "Wellness Command Center",
        (
            f"{days}-day local view · {stats.entry_count} tracked records · "
            f"routine consistency {stats.consistency_score}/100"
        ),
        right_label="LOCAL-FIRST · DESCRIPTIVE ONLY",
    )

    _style_axis(movement_axis, palette, "Movement signal", "Steps")
    movement_axis.plot(positions, steps, color=palette.cyan, linewidth=2.25, zorder=3)
    movement_axis.fill_between(positions, steps, color=palette.cyan, alpha=0.13, zorder=1)
    valid_average = [(index, value) for index, value in enumerate(step_average) if value is not None]
    if valid_average:
        movement_axis.plot(
            [item[0] for item in valid_average],
            [item[1] for item in valid_average],
            color=palette.purple,
            linewidth=1.8,
            linestyle="-",
            label="7-day average",
            zorder=4,
        )
    movement_axis.axhline(
        settings.step_goal,
        color=palette.amber,
        linestyle=(0, (4, 4)),
        linewidth=1.35,
        label=f"Goal {settings.step_goal:,}",
        zorder=2,
    )
    marker_colors = [
        palette.green
        if tracked[index] and value >= settings.step_goal
        else palette.red
        if tracked[index]
        else palette.grid
        for index, value in enumerate(steps)
    ]
    movement_axis.scatter(
        positions,
        steps,
        c=marker_colors,
        s=28,
        edgecolors=palette.panel,
        linewidths=0.8,
        zorder=5,
    )
    movement_axis.yaxis.set_major_formatter(FuncFormatter(lambda value, _position: _format_steps(value)))
    _set_date_ticks(movement_axis, labels)
    if compact:
        movement_axis.tick_params(axis="x", labelbottom=False)
    _annotate_peak(movement_axis, positions, steps, labels, palette, suffix=" steps")
    _style_legend(movement_axis, palette)

    goal_axis.set_facecolor(palette.panel)
    goal_axis.set_aspect("equal")
    goal_axis.set_xlim(-1.30, 2.00)
    goal_axis.set_ylim(-1.2, 1.2)
    goal_axis.axis("off")
    scale = _figure_scale(figure)
    goal_axis.set_title(
        "Goal constellation",
        loc="left",
        color=palette.text,
        fontsize=11 * scale,
        fontweight="bold",
        pad=6,
    )
    ring_specs = (
        (1.00, stats.step_goal_rate_pct, palette.cyan, "STEP", stats.step_goal_days),
        (0.73, stats.water_goal_rate_pct, palette.blue, "WATER", stats.water_goal_days),
        (0.46, stats.perfect_goal_rate_pct, palette.green, "BOTH", stats.perfect_goal_days),
    )
    for radius, percentage, color, label, count in ring_specs:
        goal_axis.add_patch(
            Wedge((0, 0), radius, 0, 360, width=0.13, facecolor=palette.panel_alt, edgecolor="none")
        )
        goal_axis.add_patch(
            Wedge(
                (0, 0),
                radius,
                90,
                90 + (360 * min(100, max(0, percentage)) / 100),
                width=0.13,
                facecolor=color,
                edgecolor="none",
                alpha=0.95,
            )
        )
        goal_axis.text(
            1.10,
            radius - 0.22,
            f"{label}  {percentage:>3.0f}%  ·  {count}d",
            color=color,
            fontsize=8.5 * scale,
            fontweight="bold",
            ha="left",
            va="center",
        )
    goal_axis.text(
        0,
        0.08,
        str(stats.consistency_score),
        color=palette.text,
        fontsize=23 * scale,
        fontweight="bold",
        ha="center",
    )
    goal_axis.text(
        0,
        -0.13,
        "ROUTINE\nSCORE",
        color=palette.muted,
        fontsize=7.5 * scale,
        fontweight="bold",
        ha="center",
        va="center",
    )
    goal_axis.text(
        1.10,
        -0.72,
        f"Best dual streak · {stats.longest_goal_streak_days}d",
        color=palette.muted,
        fontsize=8.2 * scale,
        ha="left",
        va="top",
    )

    _style_axis(hydration_axis, palette, "Hydration current", "Liters")
    hydration_colors = [
        palette.green
        if tracked[index] and value >= settings.water_goal_l
        else palette.blue
        if tracked[index]
        else palette.grid
        for index, value in enumerate(water)
    ]
    hydration_axis.bar(positions, water, color=hydration_colors, alpha=0.86, width=0.72, zorder=2)
    valid_water_average = [(index, value) for index, value in enumerate(water_average) if value is not None]
    if valid_water_average:
        hydration_axis.plot(
            [item[0] for item in valid_water_average],
            [item[1] for item in valid_water_average],
            color=palette.purple,
            linewidth=1.65,
            marker="o",
            markersize=2.8,
            label="7-day average",
            zorder=4,
        )
    hydration_axis.axhline(
        settings.water_goal_l,
        color=palette.amber,
        linestyle=(0, (4, 4)),
        linewidth=1.25,
        label=f"Goal {settings.water_goal_l:.1f} L",
    )
    _set_date_ticks(hydration_axis, labels)
    if compact:
        hydration_axis.tick_params(axis="x", labelbottom=False)
    _style_legend(hydration_axis, palette)

    weekday = build_weekday_profile(entries)
    angles = [index * (6.283185307179586 / 7) for index in range(7)]
    averages = [row["average_steps"] for row in weekday]
    max_average = max(averages, default=0) or 1
    normalized = [value / max_average for value in averages]
    rhythm_axis.set_facecolor(palette.panel)
    rhythm_axis.set_theta_offset(1.5707963267948966)
    rhythm_axis.set_theta_direction(-1)
    rhythm_axis.bar(
        angles,
        normalized,
        width=0.67,
        color=[
            palette.cyan,
            palette.blue,
            palette.purple,
            palette.green,
            palette.amber,
            palette.pink,
            palette.cyan,
        ],
        alpha=0.82,
        edgecolor=palette.panel,
        linewidth=0.8,
    )
    rhythm_axis.set_xticks(angles)
    rhythm_axis.set_xticklabels(
        [row["weekday"] for row in weekday],
        color=palette.muted,
        fontsize=7.5 * scale,
    )
    rhythm_axis.set_yticklabels([])
    rhythm_axis.grid(color=palette.grid, alpha=0.35)
    rhythm_axis.spines["polar"].set_color(palette.grid)
    rhythm_axis.set_title(
        "Weekday rhythm",
        color=palette.text,
        fontsize=11 * scale,
        fontweight="bold",
        pad=8,
    )
    rhythm_axis.text(
        0,
        0,
        stats.best_weekday or "—",
        color=palette.text,
        fontsize=10 * scale,
        fontweight="bold",
        ha="center",
        va="center",
    )

    _style_axis(mood_axis, palette, "Mood check-ins", "Count")
    mood_pairs = build_mood_distribution(entries)
    if mood_pairs:
        mood_labels = [item[0] for item in mood_pairs][::-1]
        mood_counts = [item[1] for item in mood_pairs][::-1]
        mood_colors = [
            palette.purple,
            palette.cyan,
            palette.blue,
            palette.green,
            palette.amber,
            palette.pink,
        ][-len(mood_pairs) :]
        mood_axis.barh(mood_labels, mood_counts, color=mood_colors, alpha=0.85)
        mood_axis.set_xlabel("Recorded days", color=palette.muted, fontsize=8)
        mood_axis.tick_params(axis="y", labelsize=7.5)
    else:
        _draw_empty_state(mood_axis, palette, "No mood check-ins yet")

    _style_axis(heat_axis, palette, "Consistency field", "")
    matrix = build_calendar_matrix(entries, settings, days=max(42, min(days, 112)))
    numeric = [[float("nan") if value is None else value for value in row] for row in matrix.values]
    heatmap = LinearSegmentedColormap.from_list(
        "novafit_consistency",
        [palette.panel_alt, palette.blue, palette.cyan, palette.green],
    ).with_extremes(bad=palette.panel)
    heat_axis.imshow(numeric, aspect="auto", interpolation="nearest", vmin=0, vmax=1, cmap=heatmap)
    heat_axis.set_yticks(range(7))
    heat_axis.set_yticklabels(matrix.weekday_labels, fontsize=7.5)
    label_step = max(1, len(matrix.week_labels) // 7)
    week_positions = list(range(0, len(matrix.week_labels), label_step))
    heat_axis.set_xticks(week_positions)
    heat_axis.set_xticklabels(
        [matrix.week_labels[index] for index in week_positions],
        fontsize=7.2 * scale,
        rotation=0,
    )
    heat_axis.set_xlabel(
        "Brighter = stronger combined goal progress"
        if compact
        else "Brighter cells represent stronger combined step and hydration goal progress",
        color=palette.muted,
        fontsize=7.5 * scale,
    )
    heat_axis.grid(False)

    figure.text(
        0.985,
        0.018,
        (
            "Routine score = tracking coverage + capped step/hydration goal completion. "
            "Personal tracking only; not medical advice."
        ),
        color=palette.muted,
        fontsize=7.4 * scale,
        ha="right",
    )
    return figure


def _create_trend_lab(
    entries: Sequence[HealthEntry],
    settings: AppSettings,
    palette: ChartTheme,
    days: int,
    figure_size: tuple[float, float] | None = None,
) -> Any:
    """Render a four-panel long-form trend laboratory."""
    from matplotlib.figure import Figure
    from matplotlib.gridspec import GridSpec
    from matplotlib.ticker import FuncFormatter

    series = build_daily_series(entries, days)
    labels = [row["date"][5:] for row in series]
    positions = list(range(len(series)))
    steps = [row["steps"] for row in series]
    water = [row["water_l"] for row in series]
    calories = [float("nan") if row["calories"] is None else row["calories"] for row in series]
    daily_score = [
        min(1.0, row["steps"] / settings.step_goal) * 50
        + min(1.0, row["water_l"] / settings.water_goal_l) * 50
        if row["tracked"]
        else 0
        for row in series
    ]

    figure = Figure(figsize=figure_size or (14.8, 8.5), dpi=100, facecolor=palette.background)
    compact = figure.get_figwidth() < 10.0 or figure.get_figheight() < 6.0
    grid = GridSpec(
        6,
        12,
        figure=figure,
        left=0.075 if compact else 0.055,
        right=0.97 if compact else 0.98,
        top=0.79 if compact else 0.84,
        bottom=0.12 if compact else 0.09,
        hspace=1.65 if compact else 0.9,
        wspace=0.92 if compact else 0.6,
    )
    step_axis = figure.add_subplot(grid[0:3, 0:8])
    water_axis = figure.add_subplot(grid[0:3, 8:12])
    calorie_axis = figure.add_subplot(grid[3:6, 0:6])
    score_axis = figure.add_subplot(grid[3:6, 6:12])

    _figure_header(
        figure,
        palette,
        "Trend Lab",
        f"Rolling signals and goal context across {days} calendar days",
    )

    _style_axis(step_axis, palette, "Movement trajectory", "Steps")
    step_axis.plot(positions, steps, color=palette.cyan, linewidth=2.1, marker="o", markersize=3.2)
    step_axis.fill_between(positions, steps, color=palette.cyan, alpha=0.12)
    average = rolling_average(steps, min(7, len(steps)))
    _plot_optional_series(step_axis, average, palette.purple, "7-day average")
    step_axis.axhline(
        settings.step_goal,
        color=palette.amber,
        linestyle="--",
        linewidth=1.2,
        label="Daily goal",
    )
    step_axis.yaxis.set_major_formatter(FuncFormatter(lambda value, _position: _format_steps(value)))
    _set_date_ticks(step_axis, labels)
    if compact:
        step_axis.tick_params(axis="x", labelbottom=False)
    _style_legend(step_axis, palette)

    _style_axis(water_axis, palette, "Hydration stability", "Liters")
    water_axis.bar(positions, water, color=palette.blue, alpha=0.78, width=0.72)
    water_average = rolling_average(water, min(7, len(water)))
    _plot_optional_series(water_axis, water_average, palette.green, "7-day average")
    water_axis.axhline(
        settings.water_goal_l,
        color=palette.amber,
        linestyle="--",
        linewidth=1.2,
        label="Daily goal",
    )
    _set_date_ticks(water_axis, labels)
    if compact:
        water_axis.tick_params(axis="x", labelbottom=False)
    _style_legend(water_axis, palette)

    _style_axis(calorie_axis, palette, "Calorie reference (optional)", "Calories")
    calorie_axis.plot(positions, calories, color=palette.pink, linewidth=1.8, marker="o", markersize=3)
    calorie_axis.axhline(
        settings.calorie_goal,
        color=palette.amber,
        linestyle="--",
        linewidth=1.2,
        label="Reference",
    )
    calorie_axis.fill_between(positions, calories, settings.calorie_goal, color=palette.pink, alpha=0.08)
    _set_date_ticks(calorie_axis, labels)
    _style_legend(calorie_axis, palette)

    _style_axis(score_axis, palette, "Daily routine score", "Score")
    score_axis.plot(positions, daily_score, color=palette.green, linewidth=2.0)
    score_axis.fill_between(positions, daily_score, color=palette.green, alpha=0.16)
    score_axis.axhline(100, color=palette.cyan, linestyle=(0, (3, 4)), linewidth=1.0, label="Both goals met")
    score_axis.set_ylim(0, 112)
    _set_date_ticks(score_axis, labels)
    _style_legend(score_axis, palette)
    score_axis.text(
        0.99,
        0.04,
        "50% steps + 50% hydration",
        transform=score_axis.transAxes,
        color=palette.muted,
        fontsize=7.5 * _figure_scale(figure),
        ha="right",
    )
    return figure


def _create_consistency_map(
    entries: Sequence[HealthEntry],
    settings: AppSettings,
    palette: ChartTheme,
    days: int,
    figure_size: tuple[float, float] | None = None,
) -> Any:
    """Render a calendar-first consistency and rhythm view."""
    from matplotlib.colors import LinearSegmentedColormap
    from matplotlib.figure import Figure
    from matplotlib.gridspec import GridSpec

    stats = calculate_dashboard(entries, settings)
    matrix = build_calendar_matrix(entries, settings, days=max(42, min(days, 182)))
    weekday = build_weekday_profile(entries)
    moods = build_mood_distribution(entries, limit=7)

    figure = Figure(figsize=figure_size or (14.8, 8.5), dpi=100, facecolor=palette.background)
    compact = figure.get_figwidth() < 10.0 or figure.get_figheight() < 6.0
    if compact:
        grid = GridSpec(
            10,
            12,
            figure=figure,
            left=0.095,
            right=0.93,
            top=0.78,
            bottom=0.13,
            hspace=2.05,
            wspace=0.75,
        )
        heat_axis = figure.add_subplot(grid[0:4, 0:12])
        weekday_axis = figure.add_subplot(grid[4:7, 0:6])
        water_axis = figure.add_subplot(grid[4:7, 6:12])
        mood_axis = figure.add_subplot(grid[7:10, 0:12])
    else:
        grid = GridSpec(
            7,
            12,
            figure=figure,
            left=0.06,
            right=0.98,
            top=0.84,
            bottom=0.1,
            hspace=1.0,
            wspace=0.72,
        )
        heat_axis = figure.add_subplot(grid[0:4, 0:12])
        weekday_axis = figure.add_subplot(grid[4:7, 0:5])
        water_axis = figure.add_subplot(grid[4:7, 5:8])
        mood_axis = figure.add_subplot(grid[4:7, 8:12])

    _figure_header(
        figure,
        palette,
        "Consistency Map",
        (
            f"Coverage {stats.tracking_coverage_pct:.0f}% · "
            f"current streak {stats.current_streak_days}d · "
            f"longest streak {stats.longest_tracking_streak_days}d"
        ),
    )

    _style_axis(heat_axis, palette, "Calendar routine field", "")
    numeric = [[float("nan") if value is None else value for value in row] for row in matrix.values]
    colormap = LinearSegmentedColormap.from_list(
        "novafit_map",
        [palette.panel_alt, palette.purple, palette.cyan, palette.green],
    ).with_extremes(bad=palette.panel)
    image = heat_axis.imshow(numeric, aspect="auto", interpolation="nearest", vmin=0, vmax=1, cmap=colormap)
    heat_axis.set_yticks(range(7))
    heat_axis.set_yticklabels(matrix.weekday_labels)
    label_step = max(1, len(matrix.week_labels) // 10)
    positions = list(range(0, len(matrix.week_labels), label_step))
    heat_axis.set_xticks(positions)
    heat_axis.set_xticklabels([matrix.week_labels[index] for index in positions])
    if compact:
        heat_axis.tick_params(axis="x", labelbottom=False)
    scale = _figure_scale(figure)
    heat_axis.set_xlabel("")
    colorbar = figure.colorbar(image, ax=heat_axis, fraction=0.015, pad=0.012)
    colorbar.ax.tick_params(colors=palette.muted, labelsize=7 * scale)
    colorbar_outline: Any = colorbar.outline
    colorbar_outline.set_edgecolor(palette.grid)
    colorbar.set_ticks([0, 0.5, 1])
    colorbar.set_ticklabels(["Low", "Mid", "Goal"] if compact else ["Started", "Balanced", "Goals"])

    _style_axis(weekday_axis, palette, "Weekday movement rhythm", "Average steps")
    weekday_labels = [row["weekday"] for row in weekday]
    weekday_steps = [row["average_steps"] for row in weekday]
    bars = weekday_axis.bar(weekday_labels, weekday_steps, color=palette.cyan, alpha=0.82)
    if weekday_steps:
        best_index = max(range(len(weekday_steps)), key=weekday_steps.__getitem__)
        bars[best_index].set_color(palette.green)
    weekday_axis.tick_params(axis="x", labelrotation=0)
    if compact:
        weekday_axis.tick_params(axis="x", pad=-13, labelcolor=palette.text)

    _style_axis(water_axis, palette, "Hydration by weekday", "Liters")
    water_axis.bar(
        weekday_labels,
        [row["average_water_l"] for row in weekday],
        color=palette.blue,
        alpha=0.82,
    )
    water_axis.axhline(settings.water_goal_l, color=palette.amber, linestyle="--", linewidth=1.1)
    water_axis.tick_params(
        axis="x",
        labelrotation=0 if compact else 65,
        labelsize=7,
        pad=-13 if compact else 2,
        labelcolor=palette.text if compact else palette.muted,
    )

    _style_axis(mood_axis, palette, "Mood distribution", "")
    if moods:
        labels = [item[0] for item in moods][::-1]
        counts = [item[1] for item in moods][::-1]
        colors = [
            palette.purple,
            palette.cyan,
            palette.blue,
            palette.green,
            palette.amber,
            palette.pink,
            palette.red,
        ]
        mood_axis.barh(labels, counts, color=colors[-len(moods) :], alpha=0.84)
    else:
        _draw_empty_state(mood_axis, palette, "No mood check-ins yet")

    figure.text(
        0.98,
        0.025,
        (
            f"Missing = empty · perfect goal days: {stats.perfect_goal_days} · longest combined-goal streak: "
            f"{stats.longest_goal_streak_days}d · best weekday: {stats.best_weekday or '—'}"
        ),
        color=palette.muted,
        fontsize=8 * scale,
        ha="right",
    )
    return figure


def _create_training_atlas(
    entries: Sequence[HealthEntry],
    settings: AppSettings,
    palette: ChartTheme,
    days: int,
    figure_size: tuple[float, float] | None = None,
) -> Any:
    """Create a visual training and routine atlas from descriptive signals."""
    import numpy as np
    from matplotlib.figure import Figure

    rows = list(entries)
    stats = calculate_dashboard(rows, settings)
    series = build_daily_series(rows, days)
    weekday = build_weekday_profile(rows)
    labels = [row["date"][5:] for row in series]
    steps = [float(row["steps"]) for row in series]
    water = [float(row["water_l"]) for row in series]

    figure = Figure(figsize=figure_size or (16.4, 10.1), dpi=100, facecolor=palette.background)
    compact = figure.get_figwidth() < 10.0 or figure.get_figheight() < 6.0
    if compact:
        grid = figure.add_gridspec(
            3,
            2,
            left=0.08,
            right=0.96,
            top=0.70,
            bottom=0.14,
            wspace=0.42,
            hspace=0.88,
            height_ratios=(0.85, 0.85, 1.35),
        )
        radar = figure.add_subplot(grid[0:2, 0], polar=True)
        movement_axis = figure.add_subplot(grid[0, 1])
        hydration_axis = figure.add_subplot(grid[1, 1])
        rhythm_axis = figure.add_subplot(grid[2, 0])
        coach_axis = figure.add_subplot(grid[2, 1])
    else:
        grid = figure.add_gridspec(
            2,
            3,
            left=0.055,
            right=0.97,
            top=0.86,
            bottom=0.085,
            wspace=0.3,
            hspace=0.38,
            width_ratios=(1.05, 1.35, 1.0),
        )
        radar = figure.add_subplot(grid[:, 0], polar=True)
        movement_axis = figure.add_subplot(grid[0, 1])
        hydration_axis = figure.add_subplot(grid[1, 1])
        rhythm_axis = figure.add_subplot(grid[0, 2])
        coach_axis = figure.add_subplot(grid[1, 2])
    _figure_header(
        figure,
        palette,
        "Training Atlas",
        (
            f"{days}-day descriptive map · goals, rhythm, and coverage"
            if compact
            else f"{days}-day descriptive map · goals, rhythm, coverage, and conservative next actions"
        ),
    )

    dimensions = ("Movement", "Hydration", "Coverage", "Consistency", "Recent rhythm")
    values = (
        min(100.0, stats.step_goal_rate_pct),
        min(100.0, stats.water_goal_rate_pct),
        min(100.0, stats.tracking_coverage_pct),
        float(stats.consistency_score),
        min(100.0, (stats.active_last_7_days / 7) * 100),
    )
    angles = np.linspace(0, 2 * math.pi, len(dimensions), endpoint=False).tolist()
    radar_values = list(values) + [values[0]]
    radar_angles = angles + [angles[0]]
    radar.set_facecolor(palette.panel)
    radar.plot(radar_angles, radar_values, color=palette.cyan, linewidth=2.4)
    radar.fill(radar_angles, radar_values, color=palette.purple, alpha=0.22)
    radar.scatter(angles, values, color=palette.amber, s=42, zorder=4)
    radar.set_xticks(angles)
    scale = _figure_scale(figure)
    radar.set_xticklabels(dimensions, color=palette.text, fontsize=8.5 * scale)
    radar.set_ylim(0, 100)
    radar.set_yticks((25, 50, 75, 100))
    radar.set_yticklabels(("25", "50", "75", "100"), color=palette.muted, fontsize=7 * scale)
    radar.grid(color=palette.grid, alpha=0.38)
    radar.spines["polar"].set_color(palette.grid)
    radar.set_title(
        "Routine capability map",
        color=palette.text,
        fontsize=12 * scale,
        fontweight="bold",
        pad=4 if compact else 24,
    )

    _style_axis(movement_axis, palette, "Movement trajectory", "steps")
    movement_axis.plot(
        range(len(steps)),
        steps,
        color=palette.cyan,
        linewidth=2.0,
        marker="o",
        markersize=2.8,
    )
    movement_axis.axhline(
        settings.step_goal,
        color=palette.amber,
        linestyle="--",
        linewidth=1.15,
        label="goal",
    )
    movement_axis.fill_between(range(len(steps)), steps, color=palette.cyan, alpha=0.12)
    _set_date_ticks(movement_axis, labels)
    _style_legend(movement_axis, palette)

    _style_axis(hydration_axis, palette, "Hydration signal", "liters")
    colors = [palette.green if item >= settings.water_goal_l else palette.blue for item in water]
    hydration_axis.bar(range(len(water)), water, color=colors, alpha=0.78)
    hydration_axis.axhline(settings.water_goal_l, color=palette.amber, linestyle="--", linewidth=1.15)
    _set_date_ticks(hydration_axis, labels)

    _style_axis(rhythm_axis, palette, "Weekday rhythm", "average steps")
    week_labels = [row["weekday"] for row in weekday]
    week_values = [row["average_steps"] for row in weekday]
    rhythm_axis.bar(
        week_labels,
        week_values,
        color=[
            palette.purple,
            palette.cyan,
            palette.blue,
            palette.green,
            palette.amber,
            palette.pink,
            palette.red,
        ],
        alpha=0.82,
    )
    rhythm_axis.tick_params(axis="x", labelrotation=30 if compact else 38)

    coach_axis.set_facecolor(palette.panel)
    coach_axis.set_xticks([])
    coach_axis.set_yticks([])
    for spine in coach_axis.spines.values():
        spine.set_color(palette.grid)
    coach_axis.set_title("Coach lens", loc="left", color=palette.text, fontsize=11, fontweight="bold", pad=10)
    suggestions: list[str] = []
    if stats.entry_count < 7:
        suggestions.append("• Build at least 7 tracked days before treating a trend as stable.")
    if stats.average_steps < settings.step_goal * 0.5 and stats.entry_count:
        suggestions.append("• Prefer short comfortable movement blocks over one abrupt jump.")
    else:
        suggestions.append("• Progress gradually; increase only one variable at a time.")
    if stats.average_water_l < settings.water_goal_l and stats.entry_count:
        suggestions.append("• Strengthen hydration logging at two fixed moments each day.")
    suggestions.append("• Keep at least one easy or recovery day in the weekly rhythm.")
    suggestions.append("• These are general educational signals, not medical advice.")
    coach_axis.text(
        0.055,
        0.9,
        ("\n" if compact else "\n\n").join(suggestions),
        transform=coach_axis.transAxes,
        color=palette.text,
        fontsize=8 * scale if compact else 9 * scale,
        va="top",
        wrap=True,
        linespacing=1.35,
    )
    figure.text(
        0.97,
        0.03,
        (
            f"Confidence grows with coverage · score {stats.consistency_score}/100"
            if compact
            else (
                "Profile-independent atlas · data confidence grows with coverage · "
                f"score {stats.consistency_score}/100"
            )
        ),
        color=palette.muted,
        fontsize=8 * scale,
        ha="right",
    )
    return figure


def _figure_scale(figure: Any) -> float:
    """Return a conservative typography scale for export and embedded figures."""
    width_ratio = figure.get_figwidth() / 14.8
    height_ratio = figure.get_figheight() / 8.5
    return max(0.78, min(1.08, math.sqrt(width_ratio * height_ratio)))


def _figure_header(
    figure: Any,
    palette: ChartTheme,
    title: str,
    subtitle: str,
    *,
    right_label: str = "LOCAL ANALYTICS",
) -> None:
    """Add a responsive title, subtitle, and privacy boundary to a figure."""
    scale = _figure_scale(figure)
    compact = figure.get_figwidth() < 10.0 or figure.get_figheight() < 6.0
    left = 0.07 if compact else 0.055
    figure.text(
        left,
        0.955,
        f"NovaFit · {title}" if compact else f"NovaFit Ultimate {__version__} · {title}",
        color=palette.text,
        fontsize=max(13.0, 19 * scale),
        fontweight="bold",
        ha="left",
        va="top",
        clip_on=False,
        zorder=20,
    )
    figure.text(
        left,
        0.89 if compact else 0.914,
        subtitle,
        color=palette.muted,
        fontsize=max(7.2, 9.5 * scale),
        ha="left",
        va="top",
    )
    if not compact:
        figure.text(
            0.98,
            0.95,
            right_label,
            color=palette.cyan,
            fontsize=8.5 * scale,
            fontweight="bold",
            ha="right",
            va="top",
        )


def _style_axis(axis: Any, palette: ChartTheme, title: str, ylabel: str) -> None:
    """Apply NovaFit panel styling to a Matplotlib axis."""
    scale = _figure_scale(axis.figure)
    axis.set_facecolor(palette.panel)
    axis.set_title(
        title,
        loc="left",
        color=palette.text,
        fontsize=max(8.5, 10.5 * scale),
        fontweight="bold",
        pad=6,
        wrap=True,
    )
    if ylabel:
        axis.set_ylabel(ylabel, color=palette.muted, fontsize=max(6.8, 8 * scale), labelpad=3)
    axis.tick_params(colors=palette.muted, labelsize=max(6.8, 7.6 * scale), pad=2)
    axis.grid(axis="y", color=palette.grid, alpha=0.27, linewidth=0.8)
    axis.set_axisbelow(True)
    for spine in axis.spines.values():
        spine.set_color(palette.grid)
        spine.set_alpha(0.58)


def _style_legend(axis: Any, palette: ChartTheme) -> None:
    """Style an axis legend only when labeled artists exist."""
    handles, labels = axis.get_legend_handles_labels()
    if not handles:
        return
    scale = _figure_scale(axis.figure)
    compact = axis.figure.get_figwidth() < 10.0
    legend = axis.legend(
        handles,
        labels,
        loc="upper left",
        fontsize=max(6.4, 7.2 * scale),
        ncol=1 if compact else min(3, len(labels)),
        borderaxespad=0.45,
        handlelength=1.6,
        handletextpad=0.45,
    )
    legend.get_frame().set_facecolor(palette.panel_alt)
    legend.get_frame().set_edgecolor(palette.grid)
    legend.get_frame().set_alpha(0.88)
    for text in legend.get_texts():
        text.set_color(palette.text)


def _set_date_ticks(axis: Any, labels: Sequence[str]) -> None:
    """Use readable, evenly spaced date ticks for short or long ranges."""
    if not labels:
        return
    max_ticks = max(3, min(9, round(axis.figure.get_figwidth() * 0.55)))
    step = max(1, math.ceil(len(labels) / max_ticks))
    positions = list(range(0, len(labels), step))
    final_position = len(labels) - 1
    if positions[-1] != final_position:
        if final_position - positions[-1] < max(2, step // 2):
            positions[-1] = final_position
        else:
            positions.append(final_position)
    axis.set_xticks(positions)
    axis.set_xticklabels(
        [labels[index] for index in positions],
        rotation=0,
        ha="center",
        fontsize=max(6.6, 7.3 * _figure_scale(axis.figure)),
    )


def _format_steps(value: float) -> str:
    """Format step-axis values without turning sub-thousand values into ``0k``."""
    absolute = abs(value)
    if absolute < 1_000:
        return f"{int(value):,}"
    if absolute < 10_000:
        return f"{value / 1_000:.1f}k"
    return f"{value / 1_000:.0f}k"


def _plot_optional_series(axis: Any, values: Sequence[float | None], color: str, label: str) -> None:
    """Plot non-null rolling values while preserving their original positions."""
    points = [(index, value) for index, value in enumerate(values) if value is not None]
    if not points:
        return
    axis.plot(
        [point[0] for point in points],
        [point[1] for point in points],
        color=color,
        linewidth=1.8,
        label=label,
    )


def _annotate_peak(
    axis: Any,
    positions: Sequence[int],
    values: Sequence[float | int],
    labels: Sequence[str],
    palette: ChartTheme,
    *,
    suffix: str = "",
) -> None:
    """Annotate the largest non-zero value without covering the data line."""
    if not values or max(values, default=0) <= 0 or axis.figure.get_figwidth() < 9.0:
        return
    index = max(range(len(values)), key=values.__getitem__)
    axis.annotate(
        f"Peak {int(values[index]):,}{suffix}\n{labels[index]}",
        xy=(positions[index], values[index]),
        xytext=(9, 9),
        textcoords="offset points",
        color=palette.text,
        fontsize=7.2 * _figure_scale(axis.figure),
        fontweight="bold",
        arrowprops={"arrowstyle": "-", "color": palette.purple, "alpha": 0.8},
        bbox={
            "boxstyle": "round,pad=0.35",
            "facecolor": palette.panel_alt,
            "edgecolor": palette.grid,
            "alpha": 0.9,
        },
    )


def _draw_empty_state(axis: Any, palette: ChartTheme, message: str) -> None:
    """Render an accessible empty state inside an existing axis."""
    axis.text(
        0.5,
        0.5,
        message,
        transform=axis.transAxes,
        color=palette.muted,
        fontsize=9 * _figure_scale(axis.figure),
        ha="center",
        va="center",
        wrap=True,
    )
    axis.set_xticks([])
    axis.set_yticks([])


palette_for = resolve_chart_theme
