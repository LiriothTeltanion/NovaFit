// Preferences per local profile (language, theme, goals, activity level, sport focus, personal why), like the
// desktop's profile table. Kept in localStorage; always optional. The browser-wide key only remembers the active
// profile; the pre-profile key (older 0.2 builds) is read once as profile 1's preferences.
import { DEFAULT_GOALS, type Goals } from './domain/analytics';
import type { ActivityLevel } from './domain/coach';
import { LANGUAGES, type Language } from './i18n';
import { DEFAULT_THEME, THEMES } from './theme';

export const SPORT_FOCUSES = ['walking', 'strength', 'mobility', 'running', 'cycling', 'mixed'] as const;
export type SportFocus = (typeof SPORT_FOCUSES)[number];

export interface Prefs {
  language: Language;
  theme: string;
  goals: Goals;
  activityLevel: ActivityLevel;
  sportFocus: SportFocus;
  why: string;
  profileId: number;
}

const KEY = 'novafit-web:prefs';
const profileKey = (id: number) => `${KEY}:p${id}`;
export const DEFAULT_PREFS: Prefs = { language: 'en', theme: DEFAULT_THEME, goals: DEFAULT_GOALS, activityLevel: 'balanced', sportFocus: 'mixed', why: '', profileId: 1 };

function load(key: string): Partial<Prefs> | null {
  try {
    const raw = localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as Partial<Prefs>) : null;
  } catch {
    return null;
  }
}

function clean(raw: Partial<Prefs>, profileId: number, fallback: Prefs): Prefs {
  const goals = { ...fallback.goals, ...(raw.goals ?? {}) };
  return {
    language: raw.language && raw.language in LANGUAGES ? raw.language : fallback.language,
    theme: raw.theme && raw.theme in THEMES ? raw.theme : fallback.theme,
    goals,
    activityLevel: raw.activityLevel && ['beginner', 'balanced', 'active'].includes(raw.activityLevel) ? raw.activityLevel : fallback.activityLevel,
    sportFocus: raw.sportFocus && (SPORT_FOCUSES as readonly string[]).includes(raw.sportFocus) ? raw.sportFocus : fallback.sportFocus,
    why: typeof raw.why === 'string' ? raw.why.slice(0, 160) : '',
    profileId,
  };
}

/** Preferences of one profile; a new profile starts from the defaults but keeps the current language and theme. */
export function readProfilePrefs(profileId: number, current: Prefs = DEFAULT_PREFS): Prefs {
  const stored = load(profileKey(profileId)) ?? (profileId === 1 ? load(KEY) : null);
  const base = { ...DEFAULT_PREFS, language: current.language, theme: current.theme };
  return clean(stored ?? {}, profileId, stored ? DEFAULT_PREFS : base);
}

export function readPrefs(): Prefs {
  const global = load(KEY) ?? {};
  const profileId = Number.isInteger(global.profileId) && (global.profileId as number) > 0 ? (global.profileId as number) : 1;
  const prefs = readProfilePrefs(profileId);
  const params = new URLSearchParams(window.location.search);
  const lang = params.get('lang');
  const theme = params.get('theme');
  return {
    ...prefs,
    language: lang && lang in LANGUAGES ? (lang as Language) : prefs.language,
    theme: theme && theme in THEMES ? theme : prefs.theme,
  };
}

export function savePrefs(prefs: Prefs): void {
  try {
    const { profileId, ...rest } = prefs;
    localStorage.setItem(profileKey(profileId), JSON.stringify(rest));
    localStorage.setItem(KEY, JSON.stringify({ profileId }));
  } catch {
    /* private mode: preferences simply are not remembered */
  }
}

export function forgetProfilePrefs(profileId: number): void {
  try {
    localStorage.removeItem(profileKey(profileId));
  } catch {
    /* nothing to forget */
  }
}
