import { useEffect, useMemo, useState } from 'react';
import { ChartLine, Droplets, Footprints, Gauge, Smile, CalendarDays } from 'lucide-react';
import { dailySeries, moodDistribution, rollingAverage, routineScore, weekdayProfile, type DailyPoint, type Goals } from '../domain/analytics';
import { moodLabel, type HealthEntry } from '../domain/entries';
import { tr, type Language } from '../i18n';

// Web counterpart of the desktop Trend Lab (charts.py _create_trend_lab + analytics.py weekday and mood helpers).
const RANGES = [30, 60, 90] as const;
const WEEKDAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
const H = 220;
const PAD = 32;

interface Props {
  language: Language;
  entries: HealthEntry[];
  goals: Goals;
  today: string;
}

/** Contiguous runs of recorded days, so lines and fills stop at gaps instead of bridging them. */
const runs = (values: Array<number | null>): Array<Array<{ i: number; v: number }>> => {
  const out: Array<Array<{ i: number; v: number }>> = [];
  values.forEach((v, i) => {
    if (v == null) return;
    const last = out[out.length - 1];
    if (last && last[last.length - 1].i === i - 1) last.push({ i, v });
    else out.push([{ i, v }]);
  });
  return out;
};

const path = (values: Array<number | null>, x: (i: number) => number, y: (v: number) => number) =>
  runs(values).map((run) => run.map(({ i, v }, k) => `${k ? 'L' : 'M'}${x(i).toFixed(1)} ${y(v).toFixed(1)}`).join('')).join('');

const fill = (values: Array<number | null>, x: (i: number) => number, y: (v: number) => number, base: number) =>
  runs(values)
    .filter((run) => run.length > 1)
    .map((run) => `${run.map(({ i, v }, k) => `${k ? 'L' : 'M'}${x(i).toFixed(1)} ${y(v).toFixed(1)}`).join('')}L${x(run[run.length - 1].i).toFixed(1)} ${base}L${x(run[0].i).toFixed(1)} ${base}Z`)
    .join('');

/** One time series with an optional trailing average and a goal line; bars or a filled line. */
function TrendChart({ points, values, average, goal, goalText, kind, label, format, width = 640 }: {
  points: DailyPoint[];
  values: Array<number | null>;
  average?: Array<number | null>;
  goal: number;
  goalText: string;
  kind: 'line' | 'bars' | 'area';
  label: string;
  format: (v: number) => string;
  /** viewBox width: the full-width card uses a wider box so its text keeps the same size as the half cards. */
  width?: number;
}) {
  const W = width;
  const peak = Math.max(goal * 1.15, ...values.map((v) => v ?? 0)) || 1;
  const base = H - PAD;
  const slot = (W - PAD * 2) / Math.max(1, points.length);
  const x = (i: number) => PAD + slot * i + slot / 2;
  const y = (v: number) => base - ((H - PAD * 2) * v) / peak;
  const line = path(values, x, y);
  const area = kind !== 'bars' ? fill(values, x, y, base) : '';
  const step = Math.ceil(points.length / 6);
  return (
    <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`${label}: ${points.map((p, i) => `${p.date} ${values[i] == null ? '—' : format(values[i] as number)}`).join(', ')}`}>
      <line className="chart__goal" x1={PAD} x2={W - PAD} y1={y(goal)} y2={y(goal)} />
      <text className="chart__goal-label" x={W - PAD} y={y(goal) - 6} textAnchor="end">{goalText}</text>
      {kind === 'bars' && values.map((v, i) => (v == null ? (
        <rect key={points[i].date} className="chart__bar chart__bar--missing" x={x(i) - slot * 0.32} y={base - 3} width={slot * 0.64} height={3} rx={1.5} />
      ) : (
        <rect key={points[i].date} className={v >= goal ? 'chart__bar chart__bar--met' : 'chart__bar'} x={x(i) - slot * 0.32} y={y(v)} width={slot * 0.64} height={Math.max(2, base - y(v))} rx={3} />
      )))}
      {area && <path className="chart__area" d={area} />}
      {kind !== 'bars' && line && <path className="chart__line" d={line} />}
      {average && <path className="chart__average" d={path(average, x, y)} />}
      {points.map((p, i) => (i % step === 0 || i === points.length - 1) && (
        <text key={p.date} className="chart__axis" x={x(i)} y={base + 18} textAnchor="middle">{p.date.slice(8, 10)}/{p.date.slice(5, 7)}</text>
      ))}
    </svg>
  );
}

/** Horizontal bars with a text label per row (weekday rhythm, mood distribution). */
function RankBars({ rows, label }: { rows: Array<{ name: string; value: number; text: string; strong?: boolean }>; label: string }) {
  const peak = Math.max(1, ...rows.map((r) => r.value));
  return (
    <ul className="rank" aria-label={label}>
      {rows.map((row) => (
        <li key={row.name} className={row.strong ? 'rank__row rank__row--strong' : 'rank__row'}>
          <span className="rank__name">{row.name}</span>
          <span className="rank__track" aria-hidden><span style={{ inlineSize: `${Math.max(2, (row.value / peak) * 100)}%` }} /></span>
          <span className="rank__value">{row.text}</span>
        </li>
      ))}
    </ul>
  );
}

/** True on wide layouts, where the full-width steps card gets a wider viewBox (false in tests without matchMedia). */
function useWide(query = '(min-width: 900px)'): boolean {
  const media = () => (typeof window !== 'undefined' && window.matchMedia ? window.matchMedia(query) : null);
  const [wide, setWide] = useState(() => media()?.matches ?? false);
  useEffect(() => {
    const list = media();
    if (!list) return;
    const update = () => setWide(list.matches);
    list.addEventListener('change', update);
    return () => list.removeEventListener('change', update);
  }, [query]);
  return wide;
}

export function TrendsPage({ language, entries, goals, today }: Props) {
  const wide = useWide();
  const t = (key: string, values?: Record<string, string | number>) => tr(language, key, values);
  const [days, setDays] = useState<(typeof RANGES)[number]>(30);
  const nf = new Intl.NumberFormat(language === 'he' ? 'he-IL' : language);
  const points = useMemo(() => dailySeries(entries, days, today), [entries, days, today]);
  const span = Math.min(7, points.length);
  const steps = points.map((p) => (p.tracked ? p.steps : null));
  const water = points.map((p) => (p.tracked ? p.waterL : null));
  // The desktop averages over the calendar series (untracked days count as 0); keep that, but only draw it on tracked days.
  const stepAverage = rollingAverage(points.map((p) => p.steps), span).map((v, i) => (points[i].tracked ? v : null));
  const waterAverage = rollingAverage(points.map((p) => p.waterL), span).map((v, i) => (points[i].tracked ? v : null));
  const score = points.map((p) => (p.tracked ? Math.round(routineScore(p, goals)) : null));
  const inRange = useMemo(() => entries.filter((e) => e.date >= points[0].date && e.date <= today), [entries, points, today]);
  const weekdays = weekdayProfile(inRange);
  const bestWeekday = weekdays.reduce((best, d) => (d.count && d.averageSteps > best.averageSteps ? d : best), weekdays[0]);
  const moods = moodDistribution(inRange);

  return (
    <section className="page" aria-labelledby="trends-title">
      <header className="page__header page__header--split">
        <div>
          <h1 id="trends-title"><ChartLine aria-hidden size={22} /> {t('chart_view_trend_lab')}</h1>
          <p className="card__detail">{t('web_trend_subtitle', { days })}</p>
        </div>
        <label>
          {t('web_trend_range')}
          <select value={days} onChange={(e) => setDays(Number(e.target.value) as (typeof RANGES)[number])}>
            {RANGES.map((d) => <option key={d} value={d}>{d}</option>)}
          </select>
        </label>
      </header>

      {inRange.length === 0 ? (
        <p className="card empty">{t('no_records')}</p>
      ) : (
        <>
          <article className="card">
            <h2 className="card__title"><Footprints aria-hidden size={16} /> {t('web_trend_steps')}</h2>
            <TrendChart points={points} values={steps} average={stepAverage} goal={goals.stepGoal} goalText={nf.format(goals.stepGoal)} kind="area" label={t('web_trend_steps')} format={(v) => nf.format(v)} width={wide ? 1180 : 640} />
            <p className="legend">
              <span className="legend__line legend__line--main" /> {t('steps')}
              <span className="legend__line legend__line--average" /> {t('web_trend_average')}
              <span className="legend__line legend__line--goal" /> {t('step_goal')}
            </p>
          </article>

          <div className="chart-grid">
            <article className="card">
              <h2 className="card__title"><Droplets aria-hidden size={16} /> {t('web_trend_water')}</h2>
              <TrendChart points={points} values={water} average={waterAverage} goal={goals.waterGoalL} goalText={`${goals.waterGoalL} L`} kind="bars" label={t('web_trend_water')} format={(v) => `${v} L`} />
              <p className="legend"><span className="legend__line legend__line--average" /> {t('web_trend_average')}</p>
            </article>
            <article className="card">
              <h2 className="card__title"><Gauge aria-hidden size={16} /> {t('web_trend_score')}</h2>
              <TrendChart points={points} values={score} goal={100} goalText="100" kind="area" label={t('web_trend_score')} format={(v) => String(v)} />
              <p className="card__detail">{t('insight_score_scope')}</p>
            </article>
          </div>

          <div className="chart-grid">
            <article className="card">
              <h2 className="card__title"><CalendarDays aria-hidden size={16} /> {t('web_trend_weekday')}</h2>
              <RankBars
                label={t('web_trend_weekday')}
                rows={weekdays.map((d) => ({
                  name: t(`weekday_${WEEKDAYS[d.weekday]}`),
                  value: d.averageSteps,
                  text: d.count ? nf.format(d.averageSteps) : '—',
                  strong: d.count > 0 && d === bestWeekday,
                }))}
              />
              {bestWeekday.count > 0 && <p className="card__detail">💡 {t('insight_best_weekday', { weekday: t(`weekday_${WEEKDAYS[bestWeekday.weekday]}`) })}</p>}
            </article>
            <article className="card">
              <h2 className="card__title"><Smile aria-hidden size={16} /> {t('web_trend_moods')}</h2>
              <RankBars
                label={t('web_trend_moods')}
                rows={moods.map(([mood, count], i) => ({
                  name: mood ? moodLabel(mood, language) : t('not_recorded'),
                  value: count,
                  text: nf.format(count),
                  strong: i === 0 && mood != null,
                }))}
              />
            </article>
          </div>
        </>
      )}
    </section>
  );
}
