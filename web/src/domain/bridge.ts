// JSON bridge with the desktop app: reads and writes `novafit-health-export-v2` (health_data + training_sessions).
import { buildEntry, type HealthEntry } from './entries';
import { buildSession, type WorkoutSession } from './workouts';

export interface ImportOutcome {
  entries: HealthEntry[];
  sessions: WorkoutSession[];
  invalid: number;
  errors: string[];
}

const MAX_ROWS = 100_000;

export function exportPayload(entries: HealthEntry[], sessions: WorkoutSession[], exportedAt = new Date()): object {
  return {
    metadata: {
      exported_at: exportedAt.toISOString().slice(0, 19),
      application: 'NovaFit web',
      version: '0.2.0',
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      total_entries: entries.length,
      schema: 'novafit-health-export-v2',
      total_sessions: sessions.length,
    },
    health_data: entries.map((e) => ({ date: e.date, steps: e.steps, water_l: e.waterL, calories: e.calories, mood: e.mood, note: e.note })),
    training_sessions: sessions.map((s) => ({ date: s.date, kind: s.kind, duration_min: s.durationMin, rpe: s.rpe, distance_km: s.distanceKm, note: s.note })),
  };
}

/** Validate every row independently; a bad row is reported, never fatal. Accepts the desktop export or a bare list. */
export function parseImport(text: string): ImportOutcome {
  const payload: unknown = JSON.parse(text);
  const out: ImportOutcome = { entries: [], sessions: [], invalid: 0, errors: [] };
  const fail = (label: string, error: unknown) => {
    out.invalid += 1;
    if (out.errors.length < 20) out.errors.push(`${label}: ${error instanceof Error ? error.message : String(error)}`);
  };
  const record = (value: unknown): Record<string, unknown> | null => (value && typeof value === 'object' && !Array.isArray(value) ? (value as Record<string, unknown>) : null);
  const root = record(payload);
  const health = Array.isArray(payload) ? payload : Array.isArray(root?.health_data) ? (root?.health_data as unknown[]) : root ? [root] : null;
  if (!health) throw new Error('JSON root must be an object or a list of objects.');
  health.slice(0, MAX_ROWS).forEach((raw, index) => {
    const row = record(raw);
    try {
      if (!row) throw new Error('row must be an object');
      out.entries.push(buildEntry({ date: String(row.date ?? row.entry_date ?? ''), steps: row.steps ?? row.Steps, waterL: row.water_l ?? row.water ?? row['Water (L)'], calories: row.calories, mood: row.mood, note: row.note }));
    } catch (error) {
      fail(`Row ${index + 1}`, error);
    }
  });
  const sessions = Array.isArray(root?.training_sessions) ? (root?.training_sessions as unknown[]) : [];
  sessions.slice(0, MAX_ROWS).forEach((raw, index) => {
    const row = record(raw);
    try {
      if (!row) throw new Error('session must be an object');
      out.sessions.push(buildSession({ date: String(row.date ?? ''), kind: String(row.kind ?? ''), durationMin: row.duration_min, rpe: row.rpe, distanceKm: row.distance_km, note: row.note }));
    } catch (error) {
      fail(`Session ${index + 1}`, error);
    }
  });
  return out;
}

export const sessionKey = (s: WorkoutSession) => [s.date, s.kind, s.durationMin, s.rpe, s.distanceKm, s.note].join('|');
