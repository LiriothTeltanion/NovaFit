// Self-contained offline HTML report (the web counterpart of novafit/reporting.py): inline CSS and SVG only,
// no scripts, no remote assets, every user string escaped. Opens anywhere, prints cleanly.
import { tr, directionFor, type Language } from '../i18n';
import { calculateDashboard, dailySeries, type Goals } from './analytics';
import { moodLabel, type HealthEntry } from './entries';
import { trainingSnapshot, type WorkoutSession } from './workouts';

const esc = (value: unknown) =>
  String(value ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c] as string);

function stepsSvg(entries: HealthEntry[], goal: number, today: string): string {
  const points = dailySeries(entries, 30, today);
  const W = 720, H = 200, P = 26;
  const peak = Math.max(goal, ...points.map((p) => p.steps)) || 1;
  const y = (v: number) => H - P - ((H - P * 2) * v) / peak;
  const slot = (W - P * 2) / points.length;
  const bars = points
    .map((p, i) => (p.tracked ? `<rect x="${(P + slot * i + slot * 0.15).toFixed(1)}" y="${y(p.steps).toFixed(1)}" width="${(slot * 0.7).toFixed(1)}" height="${(H - P - y(p.steps)).toFixed(1)}" rx="3" fill="${p.steps >= goal ? '#0f766e' : '#5eada4'}"/>` : ''))
    .join('');
  // The timeline always runs oldest → newest left to right, also inside a right-to-left page.
  return `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="steps" direction="ltr"><line x1="${P}" x2="${W - P}" y1="${y(goal).toFixed(1)}" y2="${y(goal).toFixed(1)}" stroke="#b45309" stroke-dasharray="6 5" stroke-width="2"/>${bars}<text x="${P}" y="${H - 6}" font-size="11" fill="#475569">${esc(points[0].date)}</text><text x="${W - P}" y="${H - 6}" font-size="11" fill="#475569" text-anchor="end">${esc(points[points.length - 1].date)}</text></svg>`;
}

export function buildHtmlReport(args: { entries: HealthEntry[]; sessions: WorkoutSession[]; goals: Goals; language: Language; today: string; profileName: string }): string {
  const { entries, sessions, goals, language, today, profileName } = args;
  const t = (key: string, values?: Record<string, string | number>) => tr(language, key, values);
  const s = calculateDashboard(entries, goals, today);
  const training = trainingSnapshot(sessions, today);
  const nf = new Intl.NumberFormat(language === 'he' ? 'he-IL' : language);
  const metrics: Array<[string, string]> = [
    [t('metric_tracked_days'), nf.format(s.entryCount)],
    [t('metric_average_steps'), nf.format(s.averageSteps)],
    [t('metric_average_water'), `${s.averageWaterL} L`],
    [t('metric_current_longest'), `${s.currentStreakDays} / ${s.longestTrackingStreakDays}`],
    [t('metric_both_goals'), nf.format(s.perfectGoalDays)],
    [t('metric_consistency'), `${s.consistencyScore}/100`],
    [t('training_this_week'), t('training_minutes_value', { minutes: training.thisWeek.minutes })],
  ];
  const rows = [...entries].sort((a, b) => (a.date < b.date ? 1 : -1)).slice(0, 30)
    .map((e) => `<tr><td>${esc(e.date)}</td><td>${nf.format(e.steps)}</td><td>${esc(e.waterL)}</td><td>${e.calories == null ? '—' : nf.format(e.calories)}</td><td>${esc(moodLabel(e.mood, language))}</td><td>${esc(e.note ?? '')}</td></tr>`)
    .join('');
  return `<!doctype html>
<html lang="${language}" dir="${directionFor(language)}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data:">
<title>NovaFit · ${esc(profileName)} · ${esc(today)}</title>
<style>
body{font-family:'Segoe UI',system-ui,sans-serif;margin:0;background:#f8fafc;color:#0f172a}
main{max-width:860px;margin:auto;padding:32px 20px}
h1{margin:0 0 4px;font-size:1.8rem}h2{font-size:1.1rem;margin:28px 0 10px}
.muted{color:#475569}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px}
.card{background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:14px}
.card b{display:block;font-size:1.35rem;color:#0f766e;margin-top:4px}
table{width:100%;border-collapse:collapse;font-size:.9rem;background:#fff}
th,td{padding:7px 9px;border-bottom:1px solid #e2e8f0;text-align:start}th{color:#475569;font-size:.78rem;text-transform:uppercase}
svg{width:100%;height:auto;background:#fff;border:1px solid #e2e8f0;border-radius:12px}
footer{margin-top:28px;font-size:.8rem;color:#64748b}
@media print{body{background:#fff}.card,svg,table{break-inside:avoid}}
</style>
</head>
<body><main>
<h1>NovaFit · ${esc(profileName)}</h1>
<p class="muted">${esc(t('app_subtitle'))} · ${esc(today)}</p>
<h2>${esc(t('nav_dashboard'))}</h2>
<div class="grid">${metrics.map(([k, v]) => `<div class="card">${esc(k)}<b><bdi>${esc(v)}</bdi></b></div>`).join('')}</div>
<h2>${esc(t('steps'))} · 30</h2>
${stepsSvg(entries, goals.stepGoal, today)}
<h2>${esc(t('tab_records'))}</h2>
<table><thead><tr><th>${esc(t('date'))}</th><th>${esc(t('steps'))}</th><th>${esc(t('water'))}</th><th>${esc(t('calories'))}</th><th>${esc(t('mood'))}</th><th>${esc(t('note'))}</th></tr></thead><tbody>${rows || `<tr><td colspan="6">${esc(t('no_records'))}</td></tr>`}</tbody></table>
<footer>${esc(t('recommendation_disclaimer'))} · ${esc(t('web_storage_note'))}</footer>
</main></body></html>
`;
}
