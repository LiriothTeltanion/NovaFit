import { exportPayload, parseImport } from './bridge';
import { buildPlan, trainingSignals } from './coach';
import { DEFAULT_GOALS } from './analytics';
import { buildEntry } from './entries';
import { buildSession } from './workouts';

describe('JSON bridge with the desktop app', () => {
  it('round-trips records and sessions in the desktop schema', () => {
    const entries = [buildEntry({ date: '2026-10-18', steps: 8000, waterL: 2, calories: 1900, mood: 'Calm', note: 'park' })];
    const sessions = [buildSession({ date: '2026-10-19', kind: 'running', durationMin: 30, rpe: 6, distanceKm: '5.2' })];
    const payload = exportPayload(entries, sessions, new Date('2026-10-19T06:00:00Z')) as Record<string, unknown>;
    expect((payload.metadata as Record<string, unknown>).schema).toBe('novafit-health-export-v2');
    expect(payload.health_data).toEqual([{ date: '2026-10-18', steps: 8000, water_l: 2, calories: 1900, mood: 'Calm', note: 'park' }]);
    const back = parseImport(JSON.stringify(payload));
    expect(back.entries).toEqual(entries);
    expect(back.sessions).toEqual(sessions);
    expect(back.invalid).toBe(0);
  });

  it('accepts a desktop file with a bad row and reports it instead of failing', () => {
    const desktop = {
      metadata: { schema: 'novafit-health-export-v2' },
      health_data: [{ date: '2026-10-18', steps: 5000, water_l: 1.5 }, { date: '2026-02-30', steps: 1, water_l: 1 }],
      training_sessions: [{ date: '2026-10-18', kind: 'yoga-ish', duration_min: 20 }],
    };
    const outcome = parseImport(JSON.stringify(desktop));
    expect(outcome.entries).toHaveLength(1);
    expect(outcome.invalid).toBe(2);
    expect(outcome.errors[0]).toMatch(/Row 2/);
  });
});

describe('coach port', () => {
  it('flags a sharp training-load jump with the desktop wording', () => {
    const iso = (offset: number) => new Date(Date.parse('2026-10-19T00:00:00Z') - offset * 86_400_000).toISOString().slice(0, 10);
    const week = (offset: number, minutes: number, rpe: number, count = 3) => Array.from({ length: count }, (_, i) => buildSession({ date: iso(offset + 2 * i), kind: 'running', durationMin: minutes, rpe }));
    const sessions = [...week(0, 60, 8, 2), ...week(7, 30, 5), ...week(14, 30, 5), ...week(21, 30, 5)];
    expect(trainingSignals(sessions, '2026-10-19').loadRatio).toBeCloseTo(2.13, 2);
    const plan = buildPlan([], DEFAULT_GOALS, 'balanced', 'es', '2026-10-19', sessions, (k) => k);
    const training = plan.items.filter((i) => i.category === 'training');
    expect(training[0]).toMatchObject({ priority: 'high', title: 'Suaviza las próximas sesiones' });
    expect(training[0].reason).toContain('113%');
    expect(plan.weekly).toHaveLength(3);
  });
});
