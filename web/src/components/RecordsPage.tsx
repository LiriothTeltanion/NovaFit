import { useMemo, useState, type FormEvent } from 'react';
import { Pencil, Save, Trash2 } from 'lucide-react';
import { buildEntry, EntryValidationError, MOOD_KEYS, moodLabel, type HealthEntry } from '../domain/entries';
import { WorkoutValidationError } from '../domain/workouts';
import { tr, type Language } from '../i18n';

interface Props {
  language: Language;
  entries: HealthEntry[];
  today: string;
  onSave: (entry: HealthEntry) => Promise<void>;
  onDelete: (date: string) => Promise<void>;
}

const blank = (today: string) => ({ date: today, steps: '', waterL: '', calories: '', mood: '', note: '' });

export function RecordsPage({ language, entries, today, onSave, onDelete }: Props) {
  const t = (key: string, values?: Record<string, string | number>) => tr(language, key, values);
  const [form, setForm] = useState(blank(today));
  const [query, setQuery] = useState('');
  const [showAll, setShowAll] = useState(false);
  const [message, setMessage] = useState<{ tone: 'ok' | 'error'; text: string } | null>(null);
  const nf = new Intl.NumberFormat(language === 'he' ? 'he-IL' : language);
  const field = (name: keyof typeof form) => (event: { target: { value: string } }) => setForm({ ...form, [name]: event.target.value });
  const filtered = useMemo(() => {
    const q = query.trim().toLocaleLowerCase();
    return q ? entries.filter((e) => [e.date, e.note ?? '', moodLabel(e.mood, language)].some((v) => v.toLocaleLowerCase().includes(q))) : entries;
  }, [entries, query, language]);
  const visible = showAll ? filtered : filtered.slice(0, 14);

  async function submit(event: FormEvent) {
    event.preventDefault();
    try {
      const entry = buildEntry(form);
      await onSave(entry);
      setMessage({ tone: 'ok', text: `${t('success_saved')}: ${entry.date} ✅` });
      setForm(blank(today));
    } catch (error) {
      const text = error instanceof EntryValidationError || error instanceof WorkoutValidationError ? error.message : String(error);
      setMessage({ tone: 'error', text: `${t('save_record_error')}: ${text}` });
    }
  }

  const edit = (e: HealthEntry) => {
    setForm({ date: e.date, steps: String(e.steps), waterL: String(e.waterL), calories: e.calories == null ? '' : String(e.calories), mood: e.mood?.toLowerCase() ?? '', note: e.note ?? '' });
    setMessage(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <section className="page" aria-labelledby="records-title">
      <header className="page__header">
        <h1 id="records-title">{t('tab_records')}</h1>
        <p>{t('privacy_body')}</p>
      </header>
      <div className="training">
        <form className="card form" onSubmit={submit} aria-label={t('nav_add')}>
          <h2 className="card__value">{t('nav_add')}</h2>
          <label>{t('date')}<input type="date" value={form.date} onChange={field('date')} required /></label>
          <label>{t('steps')}<input inputMode="numeric" value={form.steps} onChange={field('steps')} required /></label>
          <label>{t('water')}<input inputMode="decimal" value={form.waterL} onChange={field('waterL')} required /></label>
          <label>{t('calories')}<input inputMode="numeric" value={form.calories} onChange={field('calories')} /></label>
          <fieldset className="moods">
            <legend>{t('mood')}</legend>
            {MOOD_KEYS.map((key) => (
              <label key={key} className={form.mood === key ? 'chip chip--on' : 'chip'}>
                <input type="radio" name="mood" value={key} checked={form.mood === key} onChange={field('mood')} />
                {t(`mood_${key}`)}
              </label>
            ))}
          </fieldset>
          <label>{t('note')}<input value={form.note} onChange={field('note')} maxLength={500} /></label>
          <div className="form__row">
            <button className="button button--accent" type="submit"><Save aria-hidden size={18} /> {t('save_record')}</button>
            <button className="button button--quiet" type="button" onClick={() => setForm(blank(today))}>{t('clear_form')}</button>
          </div>
          {message && <p className={`form__message form__message--${message.tone}`} role={message.tone === 'error' ? 'alert' : 'status'}>{message.text}</p>}
        </form>

        <article className="card">
          <div className="toolbar">
            <h2 className="card__title">{t('tab_records')} ({filtered.length})</h2>
            <label className="search">
              <span className="visually-hidden">{t('search')}</span>
              <input type="search" placeholder={t('search')} value={query} onChange={(e) => setQuery(e.target.value)} />
            </label>
          </div>
          {entries.length === 0 ? (
            <p className="empty">{t('no_records')}</p>
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th scope="col">{t('date')}</th>
                    <th scope="col">{t('steps')}</th>
                    <th scope="col">{t('water')}</th>
                    <th scope="col">{t('calories')}</th>
                    <th scope="col">{t('mood')}</th>
                    <th scope="col">{t('note')}</th>
                    <th scope="col"><span className="visually-hidden">{t('edit')}</span></th>
                  </tr>
                </thead>
                <tbody>
                  {visible.map((e) => (
                    <tr key={e.date}>
                      <td>{e.date}</td>
                      <td>{nf.format(e.steps)}</td>
                      <td>{e.waterL}</td>
                      <td>{e.calories == null ? '—' : nf.format(e.calories)}</td>
                      <td>{moodLabel(e.mood, language) || '—'}</td>
                      <td className="cell-note">{e.note ?? ''}</td>
                      <td className="cell-actions">
                        <button className="icon-button" type="button" onClick={() => edit(e)} aria-label={`${t('edit')} ${e.date}`}><Pencil aria-hidden size={16} /></button>
                        <button className="icon-button" type="button" onClick={() => window.confirm(t('delete_record_confirm', { date: e.date, profile: 'NovaFit web' })) && onDelete(e.date)} aria-label={`${t('delete_record')} ${e.date}`}><Trash2 aria-hidden size={16} /></button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {filtered.length > visible.length && (
                <button className="button button--quiet" type="button" onClick={() => setShowAll(true)}>{t('show_all')} ({filtered.length})</button>
              )}
            </div>
          )}
        </article>
      </div>
    </section>
  );
}
