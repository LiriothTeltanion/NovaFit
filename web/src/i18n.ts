// The desktop catalogue, exported by scripts/export_from_python.py: one source for every label.
import catalogue from './generated/i18n.json';

export type Language = 'en' | 'es' | 'he';
export const LANGUAGES = catalogue.languages as Record<Language, { label: string; direction: 'ltr' | 'rtl'; locale: string }>;
const MESSAGES = catalogue.messages as Record<Language, Record<string, string>>;

/** Translate with English fallback and Python-style {name} / {name:+d} placeholders. */
export function tr(language: Language, key: string, values: Record<string, string | number> = {}): string {
  const template = MESSAGES[language]?.[key] ?? MESSAGES.en[key];
  if (template == null) throw new Error(`Missing translation key: ${key}`);
  return template.replace(/\{(\w+)(?::\+d)?\}/g, (match, name: string) => {
    if (!(name in values)) return match;
    const value = values[name];
    return match.includes(':+d') && typeof value === 'number' ? (value >= 0 ? `+${value}` : String(value)) : String(value);
  });
}

export const directionFor = (language: Language): 'ltr' | 'rtl' => LANGUAGES[language].direction;
export const languageKeys = (language: Language): string[] => Object.keys(MESSAGES[language]);
