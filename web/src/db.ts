// Browser-local storage (IndexedDB through Dexie). Nothing leaves the device.
import Dexie, { type EntityTable } from 'dexie';
import type { HealthEntry } from './domain/entries';
import type { WorkoutSession } from './domain/workouts';

export class NovaFitWebDb extends Dexie {
  workouts!: EntityTable<WorkoutSession, 'id'>;
  entries!: EntityTable<HealthEntry, 'date'>;

  constructor(name = 'novafit-web') {
    super(name);
    this.version(1).stores({ workouts: '++id, date, kind' });
    // v2 adds the daily records (one per date, like the desktop's UNIQUE(user_id, date)); v1 data is kept.
    this.version(2).stores({ workouts: '++id, date, kind', entries: '&date' });
  }
}

export const db = new NovaFitWebDb();

export async function listSessions(store: NovaFitWebDb = db): Promise<WorkoutSession[]> {
  const rows = await store.workouts.toArray();
  return rows.sort((a, b) => (a.date === b.date ? (b.id ?? 0) - (a.id ?? 0) : a.date < b.date ? 1 : -1));
}

export async function listEntries(store: NovaFitWebDb = db): Promise<HealthEntry[]> {
  return (await store.entries.toArray()).sort((a, b) => (a.date < b.date ? 1 : -1));
}
