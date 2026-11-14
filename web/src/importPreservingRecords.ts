import type { NovaFitWebDb } from './db';
import type { HealthEntry } from './domain/entries';
import type { WorkoutSession } from './domain/workouts';
import { sessionKey } from './domain/bridge';

/** Additive import: existing days win, duplicate sessions are skipped, all writes are atomic. */
export async function importPreservingRecords(store: NovaFitWebDb, entries: HealthEntry[], sessions: WorkoutSession[]) {
  return store.transaction('rw', store.entries, store.workouts, async () => {
    const dates = new Set(await store.entries.toCollection().primaryKeys());
    const keys = new Set((await store.workouts.toArray()).map(sessionKey));
    const freshEntries = entries.filter((entry) => !dates.has(entry.date) && dates.add(entry.date));
    const freshSessions = sessions.filter((session) => !keys.has(sessionKey(session)) && keys.add(sessionKey(session)));
    if (freshEntries.length) await store.entries.bulkAdd(freshEntries);
    if (freshSessions.length) await store.workouts.bulkAdd(freshSessions);
    return { entries: freshEntries.length, sessions: freshSessions.length,
      retained: entries.length + sessions.length - freshEntries.length - freshSessions.length };
  });
}
