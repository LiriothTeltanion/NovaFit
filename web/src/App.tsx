import { useCallback, useEffect, useState } from 'react';
import { Activity, BookOpen, Dumbbell, HeartPulse, LayoutDashboard, Lock, Sparkles, UserRound } from 'lucide-react';
import { TrainingPage } from './components/TrainingPage';
import { db, listSessions, type NovaFitWebDb } from './db';
import { demoSessions } from './domain/demo';
import { toIso, type WorkoutSession } from './domain/workouts';
import { LANGUAGES, directionFor, tr, type Language } from './i18n';
import { DEFAULT_THEME, THEMES, applyTheme } from './theme';

const PREFS_KEY = 'novafit-web:prefs';
let demoRequested = false; // React StrictMode runs effects twice in development: seed once.

function readPrefs(): { language: Language; theme: string } {
  try {
    const raw = JSON.parse(localStorage.getItem(PREFS_KEY) ?? '{}') as { language?: string; theme?: string };
    const language = raw.language && raw.language in LANGUAGES ? (raw.language as Language) : 'en';
    return { language, theme: raw.theme && raw.theme in THEMES ? raw.theme : DEFAULT_THEME };
  } catch {
    return { language: 'en', theme: DEFAULT_THEME };
  }
}

function initialPrefs(): { language: Language; theme: string } {
  const prefs = readPrefs();
  const params = new URLSearchParams(window.location.search);
  const lang = params.get('lang');
  const theme = params.get('theme');
  return {
    language: lang && lang in LANGUAGES ? (lang as Language) : prefs.language,
    theme: theme && theme in THEMES ? theme : prefs.theme,
  };
}

const NAV = [
  { key: 'nav_dashboard', icon: LayoutDashboard },
  { key: 'nav_motivation', icon: Sparkles },
  { key: 'nav_recommendations', icon: HeartPulse },
  { key: 'nav_add', icon: Activity },
  { key: 'nav_training', icon: Dumbbell, active: true },
  { key: 'nav_records', icon: BookOpen },
  { key: 'nav_profiles', icon: UserRound },
] as const;

export function App({ store = db, today = toIso(new Date()) }: { store?: NovaFitWebDb; today?: string }) {
  const [prefs, setPrefs] = useState(initialPrefs);
  const [sessions, setSessions] = useState<WorkoutSession[]>([]);
  const { language, theme } = prefs;
  const t = (key: string) => tr(language, key);

  useEffect(() => {
    applyTheme(theme);
    document.documentElement.lang = language;
    document.documentElement.dir = directionFor(language);
    document.title = `NovaFit · ${tr(language, 'training_title')}`;
    try {
      localStorage.setItem(PREFS_KEY, JSON.stringify(prefs));
    } catch {
      /* private mode: preferences simply are not remembered */
    }
  }, [prefs, language, theme]);

  const reload = useCallback(async () => setSessions(await listSessions(store)), [store]);
  useEffect(() => {
    void (async () => {
      // ?demo=1 fills an EMPTY local store with a labelled, deterministic demo history (never mixes with real data).
      if (!demoRequested && new URLSearchParams(window.location.search).get('demo') === '1' && (await store.workouts.count()) === 0) {
        demoRequested = true;
        await store.workouts.bulkAdd(demoSessions(today));
      }
      await reload();
    })();
  }, [reload, store, today]);

  return (
    <div className="shell">
      <header className="topbar">
        <div className="brand">
          <span className="brand__mark" aria-hidden>
            <HeartPulse size={22} />
          </span>
          <div>
            <p className="brand__name">
              NovaFit <span className="badge">{t('web_badge')}</span>
            </p>
            <p className="brand__tagline">{t('app_subtitle')}</p>
          </div>
        </div>
        <div className="selectors">
          <label>
            {t('language')}
            <select value={language} onChange={(e) => setPrefs({ ...prefs, language: e.target.value as Language })}>
              {Object.entries(LANGUAGES).map(([code, item]) => (
                <option key={code} value={code}>
                  {item.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            {t('theme')}
            <select value={theme} onChange={(e) => setPrefs({ ...prefs, theme: e.target.value })}>
              {Object.entries(THEMES).map(([id, item]) => (
                <option key={id} value={id}>
                  {item.label}
                </option>
              ))}
            </select>
          </label>
        </div>
      </header>

      <div className="workspace">
        <nav className="sidebar" aria-label="NovaFit">
          <p className="sidebar__title">NOVA / FIT</p>
          <ul>
            {NAV.map(({ key, icon: Icon, ...rest }) => {
              const active = 'active' in rest;
              return (
                <li key={key}>
                  <span
                    className={active ? 'nav nav--active' : 'nav nav--muted'}
                    aria-current={active ? 'page' : undefined}
                    title={active ? undefined : t('web_desktop_only')}
                  >
                    <Icon aria-hidden size={18} /> {t(key)}
                    {!active && <span className="visually-hidden"> — {t('web_desktop_only')}</span>}
                  </span>
                </li>
              );
            })}
          </ul>
          <div className="card privacy">
            <p className="card__title">
              <Lock aria-hidden size={14} /> {t('privacy_title')}
            </p>
            <p>{t('web_storage_note')}</p>
          </div>
        </nav>

        <main className="content">
          <TrainingPage
            language={language}
            sessions={sessions}
            today={today}
            onAdd={async (session) => {
              await store.workouts.add(session);
              await reload();
            }}
            onDelete={async (id) => {
              await store.workouts.delete(id);
              await reload();
            }}
          />
        </main>
      </div>
    </div>
  );
}
