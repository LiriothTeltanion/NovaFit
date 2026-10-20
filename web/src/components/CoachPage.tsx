import { useMemo } from 'react';
import { HeartPulse } from 'lucide-react';
import type { Goals } from '../domain/analytics';
import { buildPlan, type ActivityLevel } from '../domain/coach';
import type { HealthEntry } from '../domain/entries';
import type { WorkoutSession } from '../domain/workouts';
import { tr, type Language } from '../i18n';
import type { SportFocus } from '../settings';

interface Props {
  language: Language;
  entries: HealthEntry[];
  sessions: WorkoutSession[];
  goals: Goals;
  level: ActivityLevel;
  focus: SportFocus;
  today: string;
}

export function CoachPage({ language, entries, sessions, goals, level, focus, today }: Props) {
  const t = (key: string) => tr(language, key);
  const plan = useMemo(
    () => buildPlan(entries, goals, level, language, today, sessions, (k) => tr(language, `workout_kind_${k}`), tr(language, `sport_${focus}`)),
    [entries, goals, level, language, today, sessions, focus],
  );
  return (
    <section className="page" aria-labelledby="coach-title">
      <header className="page__header">
        <h1 id="coach-title">{t('recommendation_title')}</h1>
        <p>{plan.summary}</p>
      </header>
      <div className="stats">
        <article className="card stat">
          <h2 className="card__title"><HeartPulse aria-hidden size={16} /> {t('data_confidence')}</h2>
          <p className="card__value">{plan.confidencePct}%</p>
          <div className="meter" role="meter" aria-valuemin={0} aria-valuemax={100} aria-valuenow={plan.confidencePct} aria-label={t('data_confidence')}>
            <span style={{ inlineSize: `${plan.confidencePct}%` }} />
          </div>
        </article>
        <article className="card stat stat--wide">
          <h2 className="card__title">{t('suggested_weekly_rhythm')}</h2>
          <ul className="rhythm">
            {plan.weekly.map((line) => <li key={line}>{line}</li>)}
          </ul>
        </article>
      </div>
      <ol className="recommendations" aria-label={t('recommendations_heading')}>
        {plan.items.map((item, index) => (
          <li key={item.title} className={`card recommendation recommendation--${item.priority}`}>
            <div className="recommendation__head">
              <h2>
                <span className="recommendation__index">{String(index + 1).padStart(2, '0')}</span> {item.title}
              </h2>
              <span className={`pill pill--${item.priority}`}>{t(`priority_${item.priority}`)}</span>
            </div>
            <p><strong>{t('action')}:</strong> {item.action}</p>
            <p className="card__detail"><strong>{t('why')}:</strong> {item.reason}</p>
          </li>
        ))}
      </ol>
      <p className="scope">{plan.disclaimer}</p>
    </section>
  );
}
