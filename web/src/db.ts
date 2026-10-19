// Browser-local storage (IndexedDB through Dexie). Nothing leaves the device.
import Dexie, { type EntityTable } from 'dexie';
import type { WorkoutSession } from './domain/workouts';

export class NovaFitWebDb extends Dexie {
  workouts!: EntityTable<WorkoutSession, 'id'>;

  constructor(name = 'novafit-web') {
    super(name);
    this.version(1).stores({ workouts: '++id, date, kind' });
  }
}

export const db = new NovaFitWebDb();

export async function listSessions(store: NovaFitWebDb = db): Promise<WorkoutSession[]> {
  const rows = await store.workouts.orderBy('date').reverse().toArray();
  return rows.sort((a, b) => (a.date === b.date ? (b.id ?? 0) - (a.id ?? 0) : a.date < b.date ? 1 : -1));
}
