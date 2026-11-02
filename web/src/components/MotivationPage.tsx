import { useMemo, useState } from 'react';
import { Compass, Flag, RefreshCw, Sparkles, Target } from 'lucide-react';
import type { Goals } from '../domain/analytics';
import type { HealthEntry } from '../domain/entries';
import { buildMotivation } from '../domain/motivation';
import { tr, type Language } from '../i18n';

interface Props {
  language: Language;
  entries: HealthEntry[];
  goals: Goals;
  today: string;
  why: string;
}

export function MotivationPage({ language, entries, goals, today, why }: Props) {
  const t = (key: string) => tr(language, key);
  const [offset, setOffset] = useState(0);
  const m = useMemo(() => buildMotivation(entries, goals, language, today, offset), [entries, goals, language, today, offset]);
  const earned = m.achievements.filter((a) => a.earned).length;
  return (
    <section className="page" aria-labelledby="motivation-title">
      <header className={`hero card hero--level-${m.celebrationLevel}`}>
        <div>
          <p className="card__title"><Sparkles aria-hidden size={16} /> {t('nav_motivation')}</p>
          <h1 id="motivation-title" className="hero__title">{m.headline}</h1>
          <p className="hero__why">{m.message}</p>
        </div>
      </header>

      <div className="metrics">
        <article className="card stat">
          <h2 className="card__title"><Sparkles aria-hidden size={16} /> {t('daily_spark')}</h2>
          <p className="spark">{m.dailySpark}</p>
          <button className="button button--quiet" type="button" onClick={() => setOffset((v) => v + 1)}>
            <RefreshCw aria-hidden size={16} /> {t('motivation_new_spark')}
          </button>
        </article>
        <article className="card stat">
          <h2 className="card__title"><Target aria-hidden size={16} /> {t('next_action')}</h2>
          <p className="spark">{m.microAction}</p>
        </article>
        <article className="card stat">
          <h2 className="card__title"><Compass aria-hidden size={16} /> {t('motivation_week_challenge')}</h2>
          <p className="spark">{m.weeklyChallenge}</p>
        </article>
        <article className="card stat">
          <h2 className="card__title"><Flag aria-hidden size={16} /> {t('motivation_next_milestone')}</h2>
          <p className="spark">{m.nextMilestone}</p>
          <div className="meter" role="meter" aria-valuemin={0} aria-valuemax={100} aria-valuenow={m.milestoneProgressPct} aria-label={t('motivation_next_milestone')}>
            <span style={{ inlineSize: `${m.milestoneProgressPct}%` }} />
          </div>
        </article>
      </div>

      <article className="card">
        <h2 className="card__title">{t('motivation_constellation')} · {earned}/{m.achievements.length}</h2>
        <ul className="badges">
          {m.achievements.map((a) => (
            <li key={a.title} className={a.earned ? 'badge-card badge-card--earned' : 'badge-card'}>
              <span className="badge-card__icon" aria-hidden>{a.icon}</span>
              <div>
                <p className="badge-card__title">{a.title} {a.earned && <span className="visually-hidden">✓</span>}</p>
                <p className="card__detail">{a.description}</p>
                <div className="meter" role="meter" aria-valuemin={0} aria-valuemax={100} aria-valuenow={a.progressPct} aria-label={a.title}>
                  <span style={{ inlineSize: `${a.progressPct}%` }} />
                </div>
              </div>
            </li>
          ))}
        </ul>
      </article>

      <article className="card">
        <h2 className="card__title">{t('motivation_personal_why')}</h2>
        <p className="spark">{why || t('web_why_placeholder')}</p>
      </article>
      <p className="scope">{t('motivation_scope')}</p>
    </section>
  );
}
