import { useMemo, useState, type FormEvent } from 'react';
import { Dumbbell, Flame, Gauge, Trash2 } from 'lucide-react';
import {
  REFERENCE_WEEKLY_MINUTES,
  WORKOUT_KINDS,
  WorkoutValidationError,
  buildSession,
  sessionLoad,
  trainingSnapshot,
  type WorkoutSession,
} from '../domain/workouts';
import { tr, type Language } from '../i18n';
import { WeeklyBars } from './WeeklyBars';

interface Props {
  language: Language;
  sessions: WorkoutSession[];
  today: string;
  onAdd: (session: WorkoutSession) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
}

export function TrainingPage({ language, sessions, today, onAdd, onDelete }: Props) {
  const t = (key: string, values?: Record<string, string | number>) => tr(language, key, values);
  const snapshot = useMemo(() => trainingSnapshot(sessions, today), [sessions, today]);
  const [form, setForm] = useState({ date: today, kind: WORKOUT_KINDS[0], durationMin: '', rpe: '5', distanceKm: '', note: '' });
  const [message, setMessage] = useState<{ tone: 'ok' | 'error'; text: string } | null>(null);
  const [showAll, setShowAll] = useState(false);
  const visible = showAll ? sessions.slice(0, 500) : sessions.slice(0, 12);
  const field = (name: keyof typeof form) => (event: { target: { value: string } }) => setForm({ ...form, [name]: event.target.value });

  async function submit(event: FormEvent) {
    event.preventDefault();
    try {
      const session = buildSession(form);
      await onAdd(session);
      setForm({ ...form, durationMin: '', distanceKm: '', note: '' });
      setMessage({ tone: 'ok', text: t('workout_saved', { kind: t(`workout_kind_${session.kind}`), minutes: session.durationMin, profile: 'NovaFit web' }) });
    } catch (error) {
      const text = error instanceof WorkoutValidationError ? error.message : String(error);
      setMessage({ tone: 'error', text: `${t('workout_save_error')}: ${text}` });
    }
  }

  return (
    <section className="page" aria-labelledby="training-title">
      <header className="page__header">
        <h1 id="training-title">{t('training_title')}</h1>
        <p>{t('training_subtitle')}</p>
      </header>

      <div className="training">
        <form className="card form" onSubmit={submit} aria-label={t('new_session')}>
          <h2 className="card__value">{t('new_session')}</h2>
          <label>
            {t('date')}
            <input type="date" value={form.date} onChange={field('date')} required />
          </label>
          <label>
            {t('workout_kind')}
            <select value={form.kind} onChange={field('kind')}>
              {WORKOUT_KINDS.map((kind) => (
                <option key={kind} value={kind}>
                  {t(`workout_kind_${kind}`)}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t('workout_minutes')}
            <input inputMode="numeric" value={form.durationMin} onChange={field('durationMin')} required />
          </label>
          <label>
            {t('workout_rpe')}
            <input type="range" min={1} max={10} value={form.rpe} onChange={field('rpe')} aria-valuetext={`RPE ${form.rpe}`} />
            <span className="form__hint">
              <strong>{form.rpe}</strong> · {t('workout_rpe_hint')}
            </span>
          </label>
          <label>
            {t('workout_distance')}
            <input inputMode="decimal" value={form.distanceKm} onChange={field('distanceKm')} />
          </label>
          <label>
            {t('note')}
            <input value={form.note} onChange={field('note')} maxLength={500} />
          </label>
          <button className="button button--accent" type="submit">
            <Dumbbell aria-hidden size={18} /> {t('save_workout')}
          </button>
          {message && (
            <p className={`form__message form__message--${message.tone}`} role={message.tone === 'error' ? 'alert' : 'status'}>
              {message.text}
            </p>
          )}
        </form>

        <div className="training__main">
          <div className="stats">
            <article className="card stat">
              <h2 className="card__title"><Flame aria-hidden size={16} /> {t('training_this_week')}</h2>
              <p className="card__value">{t('training_minutes_value', { minutes: snapshot.thisWeek.minutes })}</p>
              <p className="card__detail">{t('training_sessions_value', { sessions: snapshot.thisWeek.sessions, days: snapshot.thisWeek.activeDays })}</p>
            </article>
            <article className="card stat">
              <h2 className="card__title"><Gauge aria-hidden size={16} /> {t('training_streak')}</h2>
              <p className="card__value">{t('training_streak_value', { weeks: snapshot.streakWeeks })}</p>
              <p className="card__detail">{t('training_vs_last_week', { change: snapshot.minutesChange })}</p>
            </article>
            <article className="card stat">
              <h2 className="card__title">{t('training_reference')}</h2>
              <p className="card__value">{t('training_reference_value', { percent: snapshot.referencePercent, reference: REFERENCE_WEEKLY_MINUTES })}</p>
              <div className="meter" role="meter" aria-valuemin={0} aria-valuemax={100} aria-valuenow={snapshot.referencePercent} aria-label={t('training_reference')}>
                <span style={{ inlineSize: `${snapshot.referencePercent}%` }} />
              </div>
            </article>
          </div>

          <article className="card">
            <h2 className="card__title">{t('training_weekly_minutes')}</h2>
            <WeeklyBars weeks={snapshot.weeks} language={language} />
          </article>

          <article className="card">
            <h2 className="card__title">{t('training_recent')}</h2>
            {sessions.length === 0 ? (
              <p className="empty">{t('training_empty')}</p>
            ) : (
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th scope="col">{t('date')}</th>
                      <th scope="col">{t('workout_kind')}</th>
                      <th scope="col">{t('workout_minutes')}</th>
                      <th scope="col">RPE</th>
                      <th scope="col">km</th>
                      <th scope="col">{t('training_load')}</th>
                      <th scope="col"><span className="visually-hidden">{t('delete_workout')}</span></th>
                    </tr>
                  </thead>
                  <tbody>
                    {visible.map((session) => (
                      <tr key={session.id}>
                        <td>{session.date}</td>
                        <td>{t(`workout_kind_${session.kind}`)}</td>
                        <td>{session.durationMin}</td>
                        <td>{session.rpe ?? '—'}</td>
                        <td>{session.distanceKm ?? '—'}</td>
                        <td>{sessionLoad(session) ?? '—'}</td>
                        <td>
                          <button className="icon-button" type="button" onClick={() => session.id != null && window.confirm(t('confirm_delete_workout')) && onDelete(session.id)} aria-label={`${t('delete_workout')} ${session.date}`}>
                            <Trash2 aria-hidden size={16} />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {sessions.length > visible.length && (
                  <button className="button button--quiet" type="button" onClick={() => setShowAll(true)}>
                    {t('show_all')} ({sessions.length})
                  </button>
                )}
              </div>
            )}
          </article>
          <p className="scope">{t('training_scope')}</p>
        </div>
      </div>
    </section>
  );
}
