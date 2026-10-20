// Mirrors tests/test_workouts.py so the web port and the desktop agree on the numbers.
import { buildSession, localIsoToday, sessionLoad, trainingSnapshot, weekStart, weeklySummary, WorkoutValidationError } from './workouts';

const MONDAY = '2026-10-19';
const s = (date: string, kind: string, durationMin: number, rpe?: number) => buildSession({ date, kind, durationMin, rpe });

describe('buildSession', () => {
  it('validates bounds and normalises optional fields', () => {
    const session = buildSession({ date: MONDAY, kind: 'running', durationMin: '30', rpe: '6', distanceKm: '', note: '  easy  ' });
    expect(session).toMatchObject({ durationMin: 30, rpe: 6, distanceKm: null, note: 'easy' });
    expect(sessionLoad(session)).toBe(180);
    for (const bad of [0, 601, -5, 'abc', 12.5]) expect(() => s(MONDAY, 'walking', bad as number)).toThrow(WorkoutValidationError);
    for (const rpe of [0, 11]) expect(() => s(MONDAY, 'walking', 20, rpe)).toThrow(WorkoutValidationError);
    expect(() => s('2026-02-30', 'walking', 20)).toThrow(WorkoutValidationError);
    expect(() => s(MONDAY, 'teleporting', 20)).toThrow(WorkoutValidationError);
  });
});

describe('weekly summary', () => {
  it('uses Monday-based weeks, oldest first', () => {
    const sessions = [s('2026-10-19', 'running', 30, 6), s('2026-10-25', 'walking', 20), s('2026-10-18', 'strength', 40, 5), s('2026-01-01', 'walking', 99)];
    const weeks = weeklySummary(sessions, '2026-10-22', 3);
    expect(weeks.map((w) => w.weekStart)).toEqual(['2026-10-05', '2026-10-12', MONDAY]);
    expect(weeks[2]).toMatchObject({ minutes: 50, sessions: 2, load: 180 });
    expect(weeks[1].minutes).toBe(40);
    expect(weekStart('2026-10-25')).toBe(MONDAY);
  });

  it('keeps the streak alive through an empty current week', () => {
    const iso = (offsetDays: number) => new Date(Date.parse(`${MONDAY}T00:00:00Z`) - offsetDays * 86_400_000).toISOString().slice(0, 10);
    const sessions = [0, 1, 2].map((weeks) => s(iso(weeks * 7 + 2), 'walking', 30));
    expect(trainingSnapshot(sessions, MONDAY).streakWeeks).toBe(3);
    const withToday = [...sessions, s(MONDAY, 'running', 200)];
    const snapshot = trainingSnapshot(withToday, MONDAY);
    expect(snapshot.streakWeeks).toBe(4);
    expect(snapshot.referencePercent).toBe(100);
    expect(snapshot.minutesChange).toBe(170);
  });
});

describe('local calendar day', () => {
  it('uses the local date, not UTC, right after midnight', () => {
    expect(localIsoToday(new Date(2026, 9, 20, 0, 30))).toBe('2026-10-20');
    expect(localIsoToday(new Date(2026, 0, 5, 23, 59))).toBe('2026-01-05');
  });
});
