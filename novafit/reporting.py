"""
Module: offline HTML reporting
Purpose: Export a self-contained visual NovaFit report without sending local records online.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Minimal deps; comments in ENGLISH; emojis sparingly.
"""

from __future__ import annotations

import base64
from html import escape
from io import BytesIO
from pathlib import Path
from typing import Iterable

from . import __version__
from .analytics import build_insight_lines, calculate_dashboard
from .charts import create_analytics_figure, resolve_chart_theme
from .config import AppSettings
from .models import HealthEntry
from .motivation import build_motivation_snapshot
from .themes import theme_label
from .time_utils import timestamp_label


def export_html_report(
    entries: Iterable[HealthEntry],
    settings: AppSettings,
    destination: Path,
    *,
    days: int | None = None,
    theme: str | None = None,
    view: str = "command_center",
) -> Path:
    """Create a portable, self-contained HTML analytics report.

    Args:
        entries: Health records in any order.
        settings: Active local goals and theme preference.
        destination: HTML output path.
        days: Optional analytics range override.
        theme: Optional dark/light override.
        view: Analytics view embedded in the report.

    Returns:
        Written HTML path.

    Raises:
        OSError: If the report cannot be written.
        ValueError: If settings, theme, or chart view is invalid.
        ImportError: If Matplotlib is unavailable.

    Example:
        >>> export_html_report([], AppSettings(), Path('data/report.html'), days=7).suffix
        '.html'
    """
    rows = sorted(list(entries), key=lambda item: item.entry_date, reverse=True)
    active_theme = theme or settings.theme
    palette = resolve_chart_theme(active_theme)
    selected_days = days or settings.chart_days
    stats = calculate_dashboard(rows, settings)
    insights = build_insight_lines(stats, settings)
    motivation = build_motivation_snapshot(rows, settings)

    figure = create_analytics_figure(
        rows,
        settings,
        view=view,
        days=selected_days,
        theme=active_theme,
    )
    image_buffer = BytesIO()
    figure.savefig(
        image_buffer,
        format="png",
        dpi=150,
        facecolor=figure.get_facecolor(),
        bbox_inches="tight",
        pad_inches=0.18,
    )
    encoded_chart = base64.b64encode(image_buffer.getvalue()).decode("ascii")

    kpis = [
        ("Tracked days", f"{stats.entry_count}"),
        ("Routine score", f"{stats.consistency_score}/100"),
        ("Tracking coverage", f"{stats.tracking_coverage_pct:.0f}%"),
        ("Average steps", f"{stats.average_steps:,}"),
        ("Average water", f"{stats.average_water_l:.2f} L"),
        ("Balanced goal days", f"{stats.perfect_goal_rate_pct:.0f}%"),
        ("Current streak", f"{stats.current_streak_days} day(s)"),
        ("Longest streak", f"{stats.longest_tracking_streak_days} day(s)"),
    ]
    table_rows = "\n".join(_entry_row(item) for item in rows[:120])
    if not table_rows:
        table_rows = '<tr><td colspan="6" class="empty">No health records were available.</td></tr>'

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>NovaFit Analytics Report</title>
  <style>
    :root {{
      --bg: {palette.background}; --panel: {palette.panel}; --panel-alt: {palette.panel_alt};
      --text: {palette.text}; --muted: {palette.muted}; --grid: {palette.grid};
      --cyan: {palette.cyan}; --purple: {palette.purple}; --green: {palette.green};
      --amber: {palette.amber}; --pink: {palette.pink}; --blue: {palette.blue};
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: var(--bg); color: var(--text); font-family: Inter, Segoe UI, Arial, sans-serif; }}
    main {{ max-width: 1380px; margin: 0 auto; padding: 36px 24px 64px; }}
    header {{ display: flex; gap: 24px; align-items: flex-start; justify-content: space-between; border-bottom: 1px solid var(--grid); padding-bottom: 24px; }}
    h1 {{ margin: 0; font-size: clamp(2rem, 5vw, 4rem); letter-spacing: -0.04em; }}
    h2 {{ margin-top: 42px; font-size: 1.25rem; letter-spacing: .06em; text-transform: uppercase; }}
    p {{ color: var(--muted); line-height: 1.65; }}
    .eyebrow {{ color: var(--cyan); font-weight: 800; letter-spacing: .16em; text-transform: uppercase; font-size: .78rem; }}
    .badge {{ border: 1px solid var(--grid); background: var(--panel); border-radius: 999px; padding: 10px 14px; color: var(--muted); white-space: nowrap; }}
    .kpis {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 12px; margin: 28px 0; }}
    .card {{ background: linear-gradient(145deg, var(--panel-alt), var(--panel)); border: 1px solid var(--grid); border-radius: 18px; padding: 18px; box-shadow: 0 18px 45px rgba(0,0,0,.12); }}
    .card small {{ display: block; color: var(--muted); font-weight: 700; letter-spacing: .08em; text-transform: uppercase; }}
    .card strong {{ display: block; margin-top: 8px; font-size: 1.55rem; color: var(--cyan); }}
    .chart {{ background: var(--panel); border: 1px solid var(--grid); border-radius: 24px; padding: 14px; overflow: hidden; }}
    .chart img {{ display: block; width: 100%; height: auto; border-radius: 16px; }}
    .insights {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 12px; }}
    .insight {{ border-left: 3px solid var(--purple); }}
    .motivation {{ margin-top: 28px; background: radial-gradient(circle at 82% 25%, var(--purple), transparent 18%), linear-gradient(135deg, var(--panel-alt), var(--panel)); }}
    .motivation h3 {{ margin: 0 0 8px; color: var(--cyan); font-size: 1.7rem; }}
    .motivation strong {{ color: var(--text); }}
    table {{ width: 100%; border-collapse: collapse; overflow: hidden; border-radius: 16px; border: 1px solid var(--grid); background: var(--panel); }}
    th, td {{ padding: 12px 14px; border-bottom: 1px solid var(--grid); text-align: left; }}
    th {{ color: var(--cyan); font-size: .78rem; text-transform: uppercase; letter-spacing: .08em; }}
    td {{ color: var(--muted); }}
    tr:last-child td {{ border-bottom: 0; }}
    .empty {{ text-align: center; padding: 30px; }}
    footer {{ margin-top: 40px; padding-top: 22px; border-top: 1px solid var(--grid); color: var(--muted); font-size: .85rem; }}
    @media print {{ body {{ background: white; }} main {{ max-width: none; padding: 0; }} .card, .chart, table {{ box-shadow: none; break-inside: avoid; }} }}
  </style>
</head>
<body>
<main>
  <header>
    <div>
      <div class="eyebrow">NovaFit // local-first wellness analytics</div>
      <h1>Personal progress, clearly visualized.</h1>
      <p>This report summarizes locally stored habit data. It is descriptive, private, and not medical advice.</p>
    </div>
    <div class="badge">v{__version__} · {escape(timestamp_label())} · {selected_days}-day view · {escape(theme_label(active_theme))}</div>
  </header>

  <section class="kpis">
    {"".join(f'<article class="card"><small>{escape(label)}</small><strong>{escape(value)}</strong></article>' for label, value in kpis)}
  </section>

  <section class="card motivation">
    <div class="eyebrow">Motivation Center</div>
    <h3>{escape(motivation.headline)}</h3>
    <p>{escape(motivation.message)}</p>
    <p><strong>Daily spark:</strong> {escape(motivation.daily_spark)}</p>
    <p><strong>Next useful action:</strong> {escape(motivation.micro_action)}</p>
    <p><strong>Next milestone:</strong> {escape(motivation.next_milestone)} ({motivation.milestone_progress_pct}%)</p>
    <p><strong>Personal why:</strong> {escape(settings.personal_why or "Not configured")}</p>
  </section>

  <section class="chart">
    <img src="data:image/png;base64,{encoded_chart}" alt="NovaFit analytics dashboard">
  </section>

  <h2>Evidence-based observations</h2>
  <section class="insights">
    {"".join(f'<article class="card insight"><p>{escape(line)}</p></article>' for line in insights)}
  </section>

  <h2>Recent records</h2>
  <table>
    <thead><tr><th>Date</th><th>Steps</th><th>Water</th><th>Calories</th><th>Mood</th><th>Note</th></tr></thead>
    <tbody>{table_rows}</tbody>
  </table>

  <footer>
    NovaFit keeps its SQLite records on the current device. Weather requests contain city coordinates only; health entries are never included.
  </footer>
</main>
</body>
</html>
"""
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.write_text(html, encoding="utf-8")
    temporary.replace(destination)
    return destination


def _entry_row(entry: HealthEntry) -> str:
    """Render one escaped HTML table row.

    Args:
        entry: Validated health record.

    Returns:
        Safe HTML table row.

    Raises:
        None.

    Example:
        >>> '&lt;' in _entry_row(HealthEntry.build('2026-07-15', 1, 1, note='<x>'))
        True
    """
    calories = "—" if entry.calories is None else f"{entry.calories:,}"
    return (
        "<tr>"
        f"<td>{escape(entry.entry_date.isoformat())}</td>"
        f"<td>{entry.steps:,}</td>"
        f"<td>{entry.water_l:.2f} L</td>"
        f"<td>{escape(calories)}</td>"
        f"<td>{escape(entry.mood or '—')}</td>"
        f"<td>{escape(entry.note or '')}</td>"
        "</tr>"
    )
