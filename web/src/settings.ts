// Per-browser preferences (language, theme, goals, activity level). Kept in localStorage; always optional.
import { DEFAULT_GOALS, type Goals } from './domain/analytics';
import type { ActivityLevel } from './domain/coach';
import { LANGUAGES, type Language } from './i18n';
import { DEFAULT_THEME, THEMES } from './theme';

export interface Prefs {
  language: Language;
  theme: string;
  goals: Goals;
  activityLevel: ActivityLevel;
  why: string;
  profileId: number;
}

const KEY = 'novafit-web:prefs';
export const DEFAULT_PREFS: Prefs = { language: 'en', theme: DEFAULT_THEME, goals: DEFAULT_GOALS, activityLevel: 'balanced', why: '', profileId: 1 };

export function readPrefs(): Prefs {
  let raw: Partial<Prefs> = {};
  try {
    raw = JSON.parse(localStorage.getItem(KEY) ?? '{}') as Partial<Prefs>;
  } catch {
    raw = {};
  }
  const params = new URLSearchParams(window.location.search);
  const lang = params.get('lang') ?? raw.language;
  const theme = params.get('theme') ?? raw.theme;
  const goals = { ...DEFAULT_GOALS, ...(raw.goals ?? {}) };
  return {
    language: lang && lang in LANGUAGES ? (lang as Language) : DEFAULT_PREFS.language,
    theme: theme && theme in THEMES ? theme : DEFAULT_PREFS.theme,
    goals,
    activityLevel: raw.activityLevel && ['beginner', 'balanced', 'active'].includes(raw.activityLevel) ? raw.activityLevel : 'balanced',
    why: typeof raw.why === 'string' ? raw.why.slice(0, 160) : '',
    profileId: Number.isInteger(raw.profileId) && (raw.profileId as number) > 0 ? (raw.profileId as number) : 1,
  };
}

export function savePrefs(prefs: Prefs): void {
  try {
    localStorage.setItem(KEY, JSON.stringify(prefs));
  } catch {
    /* private mode: preferences simply are not remembered */
  }
}
