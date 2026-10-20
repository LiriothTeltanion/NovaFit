import { useCallback, useEffect, useMemo, useState } from 'react';
import { BookOpen, Dumbbell, HeartPulse, LayoutDashboard, Lock, Settings2, Sparkles, UserRound } from 'lucide-react';
import { CoachPage } from './components/CoachPage';
import { DashboardPage } from './components/DashboardPage';
import { MotivationPage } from './components/MotivationPage';
import { ProfilesPage } from './components/ProfilesPage';
import { deleteProfileData, readProfiles, saveProfiles, storeFor, validateName, type Profile } from './profiles';
import { RecordsPage } from './components/RecordsPage';
import { SettingsPage } from './components/SettingsPage';
import { TrainingPage } from './components/TrainingPage';
import { db, listEntries, listSessions, type NovaFitWebDb } from './db';
import { exportPayload, parseImport, sessionKey } from './domain/bridge';
import { csvToEntries, entriesToCsv } from './domain/csv';
import { demoEntries, demoSessions } from './domain/demo';
import type { HealthEntry } from './domain/entries';
import { localIsoToday, type WorkoutSession } from './domain/workouts';
import { buildHtmlReport } from './domain/report';
import { LANGUAGES, directionFor, tr, type Language } from './i18n';
import { forgetProfilePrefs, readPrefs, readProfilePrefs, savePrefs, type Prefs } from './settings';
import { THEMES, applyTheme } from './theme';

let demoRequested = false; // React StrictMode runs effects twice in development: seed once.

const PAGES = [
  { id: 'dashboard', key: 'nav_dashboard', icon: LayoutDashboard },
  { id: 'motivation', key: 'nav_motivation', icon: Sparkles },
  { id: 'records', key: 'nav_records', icon: BookOpen },
  { id: 'training', key: 'nav_training', icon: Dumbbell },
  { id: 'coach', key: 'nav_recommendations', icon: HeartPulse },
  { id: 'profiles', key: 'nav_profiles', icon: UserRound },
  { id: 'settings', key: 'nav_tools', icon: Settings2 },
] as const;
type PageId = (typeof PAGES)[number]['id'];

const pageFromHash = (): PageId => {
  const id = window.location.hash.replace(/^#\/?/, '');
  return (PAGES.some((p) => p.id === id) ? id : 'dashboard') as PageId;
};

export function App({ store: base = db, today = localIsoToday() }: { store?: NovaFitWebDb; today?: string }) {
  const [prefs, setPrefs] = useState<Prefs>(readPrefs);
  const [profiles, setProfiles] = useState<Profile[]>(readProfiles);
  const [counts, setCounts] = useState<Record<number, number>>({});
  const profileId = profiles.some((p) => p.id === prefs.profileId) ? prefs.profileId : 1;
  const store = useMemo(() => storeFor(base, profileId), [base, profileId]);
  const [page, setPage] = useState<PageId>(pageFromHash);
  const [entries, setEntries] = useState<HealthEntry[]>([]);
  const [sessions, setSessions] = useState<WorkoutSession[]>([]);
  const { language, theme } = prefs;
  const t = (key: string, values?: Record<string, string | number>) => tr(language, key, values);
  const updatePrefs = (next: Prefs) => {
    setPrefs(next);
    savePrefs(next);
  };
  // Each profile keeps its own goals, language, theme, level, sport focus and personal why.
  const switchProfile = (id: number) => updatePrefs(readProfilePrefs(id, prefs));

  useEffect(() => {
    applyTheme(theme);
    document.documentElement.lang = language;
    document.documentElement.dir = directionFor(language);
  }, [language, theme]);

  useEffect(() => {
    const label = tr(language, PAGES.find((p) => p.id === page)?.key ?? 'nav_dashboard');
    document.title = `NovaFit · ${label}`;
  }, [page, language]);

  useEffect(() => {
    const onHash = () => setPage(pageFromHash());
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
  }, []);

  const reload = useCallback(async () => {
    const [nextEntries, nextSessions] = await Promise.all([listEntries(store), listSessions(store)]);
    setEntries(nextEntries);
    setSessions(nextSessions);
  }, [store]);

  useEffect(() => {
    void (async () => {
      // ?demo=1 fills an EMPTY local store with a labelled, deterministic demo history (never mixes with real data).
      if (!demoRequested && new URLSearchParams(window.location.search).get('demo') === '1' && (await store.entries.count()) === 0 && (await store.workouts.count()) === 0) {
        demoRequested = true;
        await store.entries.bulkPut(demoEntries(today));
        await store.workouts.bulkAdd(demoSessions(today));
      }
      await reload();
    })();
  }, [reload, store, today]);

  const go = (id: PageId) => {
    window.location.hash = `/${id}`;
    setPage(id);
  };

  function download(content: string, type: string, name: string) {
    const url = URL.createObjectURL(new Blob([content], { type }));
    const link = Object.assign(document.createElement('a'), { href: url, download: name });
    link.click();
    URL.revokeObjectURL(url);
  }

  async function exportJson() {
    download(JSON.stringify(exportPayload([...entries].reverse(), [...sessions].reverse()), null, 2) + '\n', 'application/json', `novafit-web-export-${today}.json`);
  }

  async function exportReport() {
    const profileName = profiles.find((p) => p.id === profileId)?.name ?? '';
    const html = buildHtmlReport({ entries, sessions, goals: prefs.goals, language, today, profileName });
    download(html, 'text/html', `novafit-web-report-${today}.html`);
  }

  async function exportCsv() {
    download(entriesToCsv([...entries].reverse()), 'text/csv', `novafit-web-records-${today}.csv`);
  }

  async function importCsv(text: string): Promise<string> {
    const outcome = csvToEntries(text);
    await store.entries.bulkPut(outcome.entries);
    await reload();
    return t('imported_records', { imported: outcome.entries.length, invalid: outcome.invalid });
  }

  useEffect(() => {
    if (page !== 'profiles') return;
    void Promise.all(profiles.map(async (p) => [p.id, await storeFor(base, p.id).entries.count()] as const)).then((rows) => setCounts(Object.fromEntries(rows)));
  }, [page, profiles, base, entries]);

  async function createProfile(name: string): Promise<string> {
    const clean = validateName(name, profiles);
    const next = [...profiles, { id: Math.max(...profiles.map((p) => p.id)) + 1, name: clean }];
    setProfiles(next);
    saveProfiles(next);
    return t('profile_created', { name: clean });
  }

  async function removeProfile(profile: Profile): Promise<string> {
    await deleteProfileData(base, profile.id);
    const next = profiles.filter((p) => p.id !== profile.id);
    setProfiles(next);
    saveProfiles(next);
    forgetProfilePrefs(profile.id);
    if (profileId === profile.id) switchProfile(1);
    return t('profile_deleted', { name: profile.name });
  }

  async function importJson(text: string): Promise<string> {
    const outcome = parseImport(text);
    const known = new Set(sessions.map(sessionKey));
    const fresh = outcome.sessions.filter((s) => !known.has(sessionKey(s)) && known.add(sessionKey(s)));
    await store.transaction('rw', store.entries, store.workouts, async () => {
      await store.entries.bulkPut(outcome.entries);
      if (fresh.length) await store.workouts.bulkAdd(fresh);
    });
    await reload();
    return t('web_import_done', { entries: outcome.entries.length, sessions: fresh.length, invalid: outcome.invalid });
  }

  return (
    <div className="shell">
      <a
        className="skip-link"
        href="#main"
        onClick={(event) => {
          // The hash router would read #main as a page; focus the content without changing the route.
          event.preventDefault();
          document.getElementById('main')?.focus();
        }}
      >{t('nav_dashboard')} ↓</a>
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
            {t('user')}
            <select value={profileId} onChange={(e) => switchProfile(Number(e.target.value))}>
              {profiles.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </label>
          <label>
            {t('language')}
            <select value={language} onChange={(e) => updatePrefs({ ...prefs, language: e.target.value as Language })}>
              {Object.entries(LANGUAGES).map(([code, item]) => (
                <option key={code} value={code}>{item.label}</option>
              ))}
            </select>
          </label>
          <label>
            {t('theme')}
            <select value={theme} onChange={(e) => updatePrefs({ ...prefs, theme: e.target.value })}>
              {Object.entries(THEMES).map(([id, item]) => (
                <option key={id} value={id}>{item.label}</option>
              ))}
            </select>
          </label>
        </div>
      </header>

      <div className="workspace">
        <nav className="sidebar" aria-label="NovaFit">
          <p className="sidebar__title">NOVA / FIT</p>
          <ul>
            {PAGES.map(({ id, key, icon: Icon }) => (
              <li key={id}>
                <a href={`#/${id}`} className={page === id ? 'nav nav--active' : 'nav'} aria-current={page === id ? 'page' : undefined} onClick={(e) => { e.preventDefault(); go(id); }}>
                  <Icon aria-hidden size={18} /> {t(key)}
                </a>
              </li>
            ))}
          </ul>
          <div className="card privacy">
            <p className="card__title"><Lock aria-hidden size={14} /> {t('privacy_title')}</p>
            <p>{t('web_storage_note')}</p>
          </div>
        </nav>

        <main className="content" id="main" tabIndex={-1}>
          {page === 'dashboard' && <DashboardPage language={language} entries={entries} goals={prefs.goals} today={today} why={prefs.why} onAddRecord={() => go('records')} />}
          {page === 'records' && (
            <RecordsPage
              key={prefs.profileId}
              language={language}
              entries={entries}
              today={today}
              onSave={async (entry) => { await store.entries.put(entry); await reload(); }}
              onDelete={async (date) => { await store.entries.delete(date); await reload(); }}
            />
          )}
          {page === 'training' && (
            <TrainingPage
              key={prefs.profileId}
              language={language}
              sessions={sessions}
              today={today}
              onAdd={async (session) => { await store.workouts.add(session); await reload(); }}
              onDelete={async (id) => { await store.workouts.delete(id); await reload(); }}
            />
          )}
          {page === 'motivation' && <MotivationPage language={language} entries={entries} goals={prefs.goals} today={today} why={prefs.why} />}
          {page === 'coach' && <CoachPage language={language} entries={entries} sessions={sessions} goals={prefs.goals} level={prefs.activityLevel} focus={prefs.sportFocus} today={today} />}
          {page === 'profiles' && (
            <ProfilesPage language={language} profiles={profiles} activeId={profileId} counts={counts} onCreate={createProfile} onActivate={switchProfile} onDelete={removeProfile} />
          )}
          {page === 'settings' && <SettingsPage key={prefs.profileId} language={language} prefs={prefs} onSave={updatePrefs} onExport={exportJson} onImport={importJson} onExportCsv={exportCsv} onExportReport={exportReport} onImportCsv={importCsv} />}
        </main>
      </div>
    </div>
  );
}
