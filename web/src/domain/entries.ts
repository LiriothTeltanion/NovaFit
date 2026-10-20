// Port of novafit/models.py HealthEntry + validation.py bounds. Moods are stored as the desktop's canonical
// English labels ("Focused") so JSON files move between the two apps unchanged.
import { parseIsoDate, toIso } from './workouts';
import { tr, type Language } from '../i18n';

export const MOOD_KEYS = ['focused', 'calm', 'energetic', 'happy', 'motivated', 'tired', 'stressed'] as const;
export const MAX_STEPS = 200_000;
export const MAX_WATER_L = 20;
export const MAX_CALORIES = 20_000;
export const MAX_MOOD_LENGTH = 32;
export const MAX_NOTE_LENGTH = 500;

export interface HealthEntry {
  date: string;
  steps: number;
  waterL: number;
  calories: number | null;
  mood: string | null;
  note: string | null;
}

export class EntryValidationError extends Error {}

function wholeNumber(raw: unknown, field: string, max: number): number {
  const text = String(raw ?? '').trim();
  if (!/^\d+$/.test(text)) throw new EntryValidationError(`${field} must be a whole number of 0 or more.`);
  const value = Number(text);
  if (value > max) throw new EntryValidationError(`${field} cannot exceed ${max.toLocaleString('en')}.`);
  return value;
}

function cleanText(raw: unknown, field: string, max: number): string | null {
  const text = String(raw ?? '').split(/\s+/).filter(Boolean).join(' ');
  if (text.length > max) throw new EntryValidationError(`${field} cannot exceed ${max} characters.`);
  return text || null;
}

export function canonicalMood(value: unknown): string | null {
  const text = String(value ?? '').trim();
  if (!text) return null;
  const folded = text.toLocaleLowerCase();
  for (const key of MOOD_KEYS) {
    if (folded === key) return key[0].toUpperCase() + key.slice(1);
    for (const language of ['en', 'es', 'he'] as Language[]) {
      if (folded === tr(language, `mood_${key}`).toLocaleLowerCase()) return key[0].toUpperCase() + key.slice(1);
    }
  }
  return text;
}

export function moodLabel(mood: string | null, language: Language): string {
  if (!mood) return '';
  const key = mood.toLowerCase();
  return (MOOD_KEYS as readonly string[]).includes(key) ? tr(language, `mood_${key}`) : mood;
}

export function buildEntry(input: { date: string; steps: unknown; waterL: unknown; calories?: unknown; mood?: unknown; note?: unknown }): HealthEntry {
  const date = toIso(parseIsoDate(input.date));
  const steps = wholeNumber(input.steps, 'Steps', MAX_STEPS);
  const waterText = String(input.waterL ?? '').trim().replace(',', '.');
  const waterL = Number(waterText);
  if (waterText === '' || !Number.isFinite(waterL) || waterL < 0 || waterL > MAX_WATER_L) {
    throw new EntryValidationError(`Water must be a number between 0 and ${MAX_WATER_L}.`);
  }
  const calText = String(input.calories ?? '').trim();
  const calories = calText === '' ? null : wholeNumber(calText, 'Calories', MAX_CALORIES);
  const mood = canonicalMood(cleanText(input.mood, 'Mood', MAX_MOOD_LENGTH));
  return { date, steps, waterL: Math.round(waterL * 100) / 100, calories, mood, note: cleanText(input.note, 'Note', MAX_NOTE_LENGTH) };
}
