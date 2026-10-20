// Deterministic demo history for screenshots and first-time visitors (?demo=1, only into an empty store).
import { buildEntry, MOOD_KEYS, type HealthEntry } from './entries';
import { buildSession, parseIsoDate, toIso, type WorkoutSession } from './workouts';

const PLANS: Array<[kind: string, minutes: [number, number], rpe: [number, number], km: [number, number] | null]> = [
  ['walking', [25, 60], [3, 5], [2, 5.5]],
  ['running', [20, 45], [5, 8], [3, 8]],
  ['strength', [30, 55], [6, 8], null],
  ['mobility', [15, 30], [2, 4], null],
  ['cycling', [30, 75], [4, 7], [8, 25]],
];

function generator(seed: number) {
  let state = seed >>> 0;
  const next = () => ((state = (Math.imul(state, 1664525) + 1013904223) >>> 0) / 4294967296);
  return { next, between: ([lo, hi]: [number, number]) => lo + Math.floor(next() * (hi - lo + 1)) };
}

export function demoSessions(today: string, weeks = 8, seed = 20261019): WorkoutSession[] {
  const { next, between } = generator(seed);
  const last = parseIsoDate(today).getTime();
  const sessions: WorkoutSession[] = [];
  for (let day = weeks * 7 - 1; day >= 0; day -= 1) {
    if (next() >= 0.52) continue;
    const [kind, minutes, rpe, km] = PLANS[Math.floor(next() * PLANS.length)];
    sessions.push(buildSession({ date: toIso(new Date(last - day * 86_400_000)), kind, durationMin: between(minutes), rpe: between(rpe), distanceKm: km ? (km[0] + next() * (km[1] - km[0])).toFixed(1) : '' }));
  }
  return sessions;
}

/** About 7 weeks of daily records with a few skipped days, so streaks, coverage and charts all have something to show. */
export function demoEntries(today: string, days = 49, seed = 20261020): HealthEntry[] {
  const { next, between } = generator(seed);
  const last = parseIsoDate(today).getTime();
  const entries: HealthEntry[] = [];
  for (let day = days - 1; day >= 0; day -= 1) {
    if (day > 2 && next() < 0.12) continue;
    const weekend = [0, 6].includes(new Date(last - day * 86_400_000).getUTCDay());
    const steps = between(weekend ? [9000, 16000] : [4500, 12500]);
    entries.push(
      buildEntry({
        date: toIso(new Date(last - day * 86_400_000)),
        steps,
        waterL: (1.2 + next() * 1.6).toFixed(2),
        calories: next() < 0.7 ? between([1700, 2600]) : '',
        mood: next() < 0.8 ? MOOD_KEYS[Math.floor(next() * MOOD_KEYS.length)] : '',
      }),
    );
  }
  return entries;
}
