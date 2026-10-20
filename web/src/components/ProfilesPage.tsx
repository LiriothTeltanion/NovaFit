import { useState, type FormEvent } from 'react';
import { Check, Trash2, UserPlus, UserRound } from 'lucide-react';
import { tr, type Language } from '../i18n';
import type { Profile } from '../profiles';

interface Props {
  language: Language;
  profiles: Profile[];
  activeId: number;
  counts: Record<number, number>;
  onCreate: (name: string) => Promise<string>;
  onActivate: (id: number) => void;
  onDelete: (profile: Profile) => Promise<string>;
}

export function ProfilesPage({ language, profiles, activeId, counts, onCreate, onActivate, onDelete }: Props) {
  const t = (key: string, values?: Record<string, string | number>) => tr(language, key, values);
  const [name, setName] = useState('');
  const [message, setMessage] = useState<{ tone: 'ok' | 'error'; text: string } | null>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    try {
      setMessage({ tone: 'ok', text: await onCreate(name) });
      setName('');
    } catch (error) {
      setMessage({ tone: 'error', text: `${t('create_profile_error')}: ${error instanceof Error ? error.message : String(error)}` });
    }
  }

  return (
    <section className="page" aria-labelledby="profiles-title">
      <header className="page__header">
        <h1 id="profiles-title">{t('profile_studio')}</h1>
        <p>{t('profile_subtitle')}</p>
      </header>
      <div className="settings">
        <form className="card form" onSubmit={submit}>
          <h2 className="card__value">{t('create_profile')}</h2>
          <label>
            {t('display_name')}
            <input value={name} maxLength={40} onChange={(e) => setName(e.target.value)} required />
          </label>
          <button className="button button--accent" type="submit"><UserPlus aria-hidden size={18} /> {t('create')}</button>
        </form>
        <ul className="profile-list" aria-label={t('nav_profiles')}>
          {profiles.map((p) => (
            <li key={p.id} className={p.id === activeId ? 'card profile profile--active' : 'card profile'}>
              <span className="profile__avatar" aria-hidden><UserRound size={22} /></span>
              <div className="profile__body">
                <p className="profile__name">{p.name}</p>
                <p className="card__detail">{t('profile_records')}: {counts[p.id] ?? '—'}</p>
              </div>
              {p.id === activeId ? (
                <span className="pill pill--low"><Check aria-hidden size={12} /> {t('active')}</span>
              ) : (
                <button className="button button--quiet" type="button" onClick={() => onActivate(p.id)}>{t('activate')}</button>
              )}
              {p.id !== 1 && (
                <button
                  className="icon-button"
                  type="button"
                  aria-label={`${t('delete_profile')} ${p.name}`}
                  onClick={async () => {
                    if (!window.confirm(t('delete_profile_confirm', { name: p.name }))) return;
                    try {
                      setMessage({ tone: 'ok', text: await onDelete(p) });
                    } catch (error) {
                      setMessage({ tone: 'error', text: `${t('delete_profile_error')}: ${error instanceof Error ? error.message : String(error)}` });
                    }
                  }}
                >
                  <Trash2 aria-hidden size={16} />
                </button>
              )}
            </li>
          ))}
        </ul>
      </div>
      {message && <p className={`form__message form__message--${message.tone}`} role={message.tone === 'error' ? 'alert' : 'status'}>{message.text}</p>}
    </section>
  );
}
