import { NovaFitWebDb } from './db';
import { importPreservingRecords } from './importPreservingRecords';
import { buildEntry } from './domain/entries';
import { buildSession } from './domain/workouts';

let n = 0;
describe('preserve-first imports', () => {
  it('retains existing days, skips duplicate input and makes repeat imports idempotent', async () => {
    const db = new NovaFitWebDb(`preserve-test-${++n}`);
    const original = buildEntry({ date: '2026-10-18', steps: 42, waterL: 1, note: 'keep me' });
    const replacement = { ...original, steps: 999, note: 'do not overwrite' };
    const fresh = { ...original, date: '2026-10-19' };
    const session = buildSession({ date: '2026-10-19', kind: 'walking', durationMin: 30 });
    await db.entries.add(original);
    expect(await importPreservingRecords(db, [replacement, fresh, fresh], [session, session])).toEqual({ entries: 1, sessions: 1, retained: 3 });
    expect(await db.entries.get(original.date)).toEqual(original);
    expect(await importPreservingRecords(db, [replacement, fresh], [session])).toEqual({ entries: 0, sessions: 0, retained: 3 });
    expect(await db.entries.count()).toBe(2);
    expect(await db.workouts.count()).toBe(1);
    await db.delete();
  });

  it('rolls back every write when a later insertion fails', async () => {
    const db = new NovaFitWebDb(`preserve-test-${++n}`);
    const entry = buildEntry({ date: '2026-10-19', steps: 42, waterL: 1 });
    const session = buildSession({ date: '2026-10-19', kind: 'walking', durationMin: 30 });
    await db.workouts.add({ ...session, id: 1 });
    await expect(importPreservingRecords(db, [entry], [{ ...session, durationMin: 40, id: 1 }])).rejects.toThrow();
    expect(await db.entries.count()).toBe(0);
    expect(await db.workouts.count()).toBe(1);
    await db.delete();
  });
});
