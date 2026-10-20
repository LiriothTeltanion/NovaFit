import { useMemo } from 'react';
import { CalendarCheck, Droplets, Flame, Footprints, Sparkles, Target, TrendingUp, Trophy } from 'lucide-react';
import { calculateDashboard, dailySeries, type Goals } from '../domain/analytics';
import { moodLabel, type HealthEntry } from '../domain/entries';
import { parseIsoDate } from '../domain/workouts';
import { tr, type Language } from '../i18n';
import { ConsistencyMap, DailyBars, WaterArea } from './Charts';

const WEEKDAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];

interface Props {
  language: Language;
  entries: HealthEntry[];
  goals: Goals;
  today: string;
  why: string;
  onAddRecord: () => void;
}

export function DashboardPage({ language, entries, goals, today, why, onAddRecord }: Props) {
  const t = (key: string, values?: Record<string, string | number>) => tr(language, key, values);
  const stats = useMemo(() => calculateDashboard(entries, goals, today), [entries, goals, today]);
  const last14 = useMemo(() => dailySeries(entries, 14, today), [entries, today]);
  const last49 = useMemo(() => dailySeries(entries, 49, today), [entries, today]);
  const nf = new Intl.NumberFormat(language === 'he' ? 'he-IL' : language);
  const dayIndex = Math.floor(parseIsoDate(today).getTime() / 86_400_000);
  const spark = t(`spark_${(dayIndex % 8) + 1}`);
  const weekdayLabels = WEEKDAYS.map((d) => t(`weekday_${d}`));

  const cards = [
    { icon: Footprints, title: t('metric_average_steps'), value: nf.format(stats.averageSteps), detail: `${t('step_goal')}: ${nf.format(goals.stepGoal)}` },
    { icon: Droplets, title: t('metric_average_water'), value: `${stats.averageWaterL} L`, detail: `${t('water_goal')}: ${goals.waterGoalL} L` },
    { icon: Flame, title: t('metric_current_longest'), value: `${stats.currentStreakDays} / ${stats.longestTrackingStreakDays}`, detail: t('motivation_current_streak') },
    { icon: Target, title: t('metric_both_goals'), value: nf.format(stats.perfectGoalDays), detail: `${t('metric_tracked_days')}: ${stats.entryCount}` },
    { icon: CalendarCheck, title: t('metric_consistency'), value: `${stats.consistencyScore}/100`, detail: `${t('metric_coverage_30')}: ${stats.trackingCoveragePct}%`, meter: stats.consistencyScore },
    { icon: TrendingUp, title: t('metric_recent_trend'), value: stats.recentStepChangePct == null ? '—' : `${stats.recentStepChangePct > 0 ? '+' : ''}${stats.recentStepChangePct}%`, detail: stats.recentStepChangePct == null ? t('need_14_records') : t('metric_average_steps') },
    { icon: Trophy, title: t('metric_best_day'), value: stats.bestDate ? nf.format(stats.bestSteps) : '—', detail: stats.bestDate ?? t('no_records') },
  ];

  return (
    <section className="page" aria-labelledby="dashboard-title">
      <header className="hero card">
        <div>
          <p className="card__title"><Sparkles aria-hidden size={16} /> {t('daily_spark')}</p>
          <h1 id="dashboard-title" className="hero__title">{spark}</h1>
          <p className="hero__why">
            <strong>{t('motivation_personal_why')}:</strong> {why || t('web_why_placeholder')}
          </p>
        </div>
        <button className="button button--accent" type="button" onClick={onAddRecord}>
          {t('nav_add')}
        </button>
      </header>

      {stats.entryCount === 0 ? (
        <p className="card empty">{t('no_records')}</p>
      ) : (
        <>
          <div className="metrics">
            {cards.map(({ icon: Icon, title, value, detail, meter }) => (
              <article className="card stat" key={title}>
                <h2 className="card__title"><Icon aria-hidden size={16} /> {title}</h2>
                <p className="card__value">{value}</p>
                <p className="card__detail">{detail}</p>
                {meter != null && (
                  <div className="meter" role="meter" aria-valuemin={0} aria-valuemax={100} aria-valuenow={meter} aria-label={title}>
                    <span style={{ inlineSize: `${meter}%` }} />
                  </div>
                )}
              </article>
            ))}
          </div>

          <div className="chart-grid">
            <article className="card">
              <h2 className="card__title">{t('web_chart_steps')}</h2>
              <DailyBars points={last14} value={(p) => p.steps} goal={goals.stepGoal} label={t('web_chart_steps')} format={(v) => nf.format(v)} />
            </article>
            <article className="card">
              <h2 className="card__title">{t('web_chart_water')}</h2>
              <WaterArea points={last14} goal={goals.waterGoalL} label={t('web_chart_water')} />
            </article>
          </div>

          <article className="card">
            <h2 className="card__title">{t('web_chart_map')}</h2>
            <ConsistencyMap points={last49} stepGoal={goals.stepGoal} waterGoal={goals.waterGoalL} label={t('web_chart_map')} weekdays={weekdayLabels} />
            <p className="legend">
              <span className="legend__swatch map__cell--both" /> <span className="legend__swatch map__cell--one" /> <span className="legend__swatch map__cell--tracked" />{' '}
              <span className="legend__swatch map__cell--none" /> {t('web_map_legend')}
            </p>
          </article>

          <article className="card insights">
            {stats.bestWeekday != null && <p>💡 {t('insight_best_weekday', { weekday: weekdayLabels[stats.bestWeekday] })}</p>}
            {stats.dominantMood && <p>🙂 {t('dominant_mood', { value: moodLabel(stats.dominantMood, language) })}</p>}
            {stats.latestDate && (
              <p>🗓️ {t('latest_record', { date: stats.latestDate, steps: nf.format(entries.find((e) => e.date === stats.latestDate)?.steps ?? 0), water: entries.find((e) => e.date === stats.latestDate)?.waterL ?? 0 })}</p>
            )}
          </article>
        </>
      )}
    </section>
  );
}
