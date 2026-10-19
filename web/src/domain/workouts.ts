// Port of novafit/workouts.py (desktop) for the web shell. Same bounds, same Monday-based
// weeks, same streak rule, same session load (minutes × RPE): the two apps must agree.
import domain from '../generated/domain.json';

export const WORKOUT_KINDS = domain.workoutKinds as readonly string[];
export const REFERENCE_WEEKLY_MINUTES: number = domain.referenceWeeklyMinutes;
export const MAX_DURATION_MIN = 600;
export const MAX_DISTANCE_KM = 500;
export const MAX_NOTE_LENGTH = 500;

export interface WorkoutSession {
  id?: number;
  date: string; // ISO YYYY-MM-DD
  kind: string;
  durationMin: number;
  rpe: number | null;
  distanceKm: number | null;
  note: string | null;
}

export interface TrainingWeek {
  weekStart: string;
  sessions: number;
  minutes: number;
  activeDays: number;
  load: number;
}

export interface TrainingSnapshot {
  thisWeek: TrainingWeek;
  lastWeek: TrainingWeek;
  weeks: TrainingWeek[];
  streakWeeks: number;
  referencePercent: number;
  minutesChange: number;
}

export class WorkoutValidationError extends Error {}

const ISO = /^\d{4}-\d{2}-\d{2}$/;

/** Parse a real calendar date (UTC midnight, so week maths never shifts with the timezone). */
export function parseIsoDate(value: string): Date {
  const text = value.trim();
  if (!ISO.test(text)) throw new WorkoutValidationError('Date must use YYYY-MM-DD.');
  const parsed = new Date(`${text}T00:00:00Z`);
  if (Number.isNaN(parsed.getTime()) || parsed.toISOString().slice(0, 10) !== text) {
    throw new WorkoutValidationError('Date must be a real calendar date.');
  }
  return parsed;
}

export const toIso = (day: Date): string => day.toISOString().slice(0, 10);

function wholeNumber(raw: unknown, field: string, min: number, max: number): number {
  const text = String(raw ?? '').trim();
  if (!/^-?\d+$/.test(text)) throw new WorkoutValidationError(`${field} must be a whole number.`);
  const value = Number(text);
  if (value < min || value > max) throw new WorkoutValidationError(`${field} must be between ${min} and ${max}.`);
  return value;
}

export function buildSession(input: {
  date: string;
  kind: string;
  durationMin: unknown;
  rpe?: unknown;
  distanceKm?: unknown;
  note?: unknown;
}): WorkoutSession {
  const date = toIso(parseIsoDate(input.date));
  if (!WORKOUT_KINDS.includes(input.kind)) throw new WorkoutValidationError(`Unknown workout type: ${input.kind}.`);
  const durationMin = wholeNumber(input.durationMin, 'Duration', 1, MAX_DURATION_MIN);
  const rpeText = String(input.rpe ?? '').trim();
  const rpe = rpeText === '' ? null : wholeNumber(rpeText, 'Effort (RPE)', 1, 10);
  const distText = String(input.distanceKm ?? '').trim().replace(',', '.');
  let distanceKm: number | null = null;
  if (distText !== '') {
    const value = Number(distText);
    if (!Number.isFinite(value) || value < 0 || value > MAX_DISTANCE_KM) {
      throw new WorkoutValidationError(`Distance must be between 0 and ${MAX_DISTANCE_KM}.`);
    }
    distanceKm = Math.round(value * 100) / 100;
  }
  const noteText = String(input.note ?? '').split(/\s+/).filter(Boolean).join(' ');
  if (noteText.length > MAX_NOTE_LENGTH) throw new WorkoutValidationError(`Note cannot exceed ${MAX_NOTE_LENGTH} characters.`);
  return { date, kind: input.kind, durationMin, rpe, distanceKm, note: noteText || null };
}

export const sessionLoad = (s: WorkoutSession): number | null => (s.rpe == null ? null : s.durationMin * s.rpe);

/** Monday of the ISO week, as an ISO date. */
export function weekStart(iso: string): string {
  const day = parseIsoDate(iso);
  const offset = (day.getUTCDay() + 6) % 7;
  return toIso(new Date(day.getTime() - offset * 86_400_000));
}

const addWeeks = (iso: string, weeks: number): string => toIso(new Date(parseIsoDate(iso).getTime() + weeks * 7 * 86_400_000));

export function weeklySummary(sessions: WorkoutSession[], today: string, weeks = 8): TrainingWeek[] {
  if (weeks < 1 || weeks > 52) throw new WorkoutValidationError('Weeks must be between 1 and 52.');
  const current = weekStart(today);
  const starts = Array.from({ length: weeks }, (_, index) => addWeeks(current, index - (weeks - 1)));
  const buckets = new Map<string, WorkoutSession[]>(starts.map((start) => [start, []]));
  for (const session of sessions) buckets.get(weekStart(session.date))?.push(session);
  return starts.map((start) => {
    const items = buckets.get(start) ?? [];
    return {
      weekStart: start,
      sessions: items.length,
      minutes: items.reduce((sum, s) => sum + s.durationMin, 0),
      activeDays: new Set(items.map((s) => s.date)).size,
      load: items.reduce((sum, s) => sum + (sessionLoad(s) ?? 0), 0),
    };
  });
}

/** The desktop's snapshot: the streak survives an empty current week (a Monday does not break it). */
export function trainingSnapshot(sessions: WorkoutSession[], today: string, weeks = 8): TrainingSnapshot {
  const summary = weeklySummary(sessions, today, Math.max(2, weeks));
  const history = weeklySummary(sessions, today, 52).reverse();
  const ordered = history[0]?.sessions === 0 ? history.slice(1) : history;
  let streakWeeks = 0;
  for (const week of ordered) {
    if (week.sessions === 0) break;
    streakWeeks += 1;
  }
  const thisWeek = summary[summary.length - 1];
  const lastWeek = summary[summary.length - 2];
  return {
    thisWeek,
    lastWeek,
    weeks: summary.slice(-weeks),
    streakWeeks,
    referencePercent: Math.min(100, Math.round((thisWeek.minutes * 100) / REFERENCE_WEEKLY_MINUTES)),
    minutesChange: thisWeek.minutes - lastWeek.minutes,
  };
}
