// Port of novafit/analytics.py calculate_dashboard + build_daily_series. Same formulas, same rounding.
import type { HealthEntry } from './entries';
import { parseIsoDate, toIso } from './workouts';

export interface Goals {
  stepGoal: number;
  waterGoalL: number;
  calorieGoal: number;
}

export const DEFAULT_GOALS: Goals = { stepGoal: 10_000, waterGoalL: 2, calorieGoal: 2_000 };

export interface DashboardStats {
  entryCount: number;
  totalSteps: number;
  averageSteps: number;
  averageWaterL: number;
  averageCalories: number | null;
  stepGoalDays: number;
  waterGoalDays: number;
  perfectGoalDays: number;
  currentStreakDays: number;
  longestTrackingStreakDays: number;
  longestGoalStreakDays: number;
  bestSteps: number;
  bestDate: string | null;
  recentStepChangePct: number | null;
  dominantMood: string | null;
  trackingCoveragePct: number;
  consistencyScore: number;
  bestWeekday: number | null; // 0 = Monday
  activeLast7Days: number;
  latestDate: string | null;
  daysSinceLatest: number | null;
  isStale: boolean;
}

const DAY = 86_400_000;
const days = (a: string, b: string) => Math.round((parseIsoDate(b).getTime() - parseIsoDate(a).getTime()) / DAY);
const mean = (values: number[]) => values.reduce((s, v) => s + v, 0) / values.length;
const meetsBoth = (e: HealthEntry, g: Goals) => e.steps >= g.stepGoal && e.waterL >= g.waterGoalL;
// Python's round() is banker's rounding; mirror it so both apps print the same averages.
function pyRound(value: number, digits = 0): number {
  const f = 10 ** digits, x = value * f, r = Math.round(x);
  return (Math.abs(x % 1) === 0.5 ? (r % 2 === 0 ? r : r - 1) : r) / f;
}

export function sortedUnique(entries: HealthEntry[]): HealthEntry[] {
  const byDate = new Map(entries.map((e) => [e.date, e]));
  return [...byDate.values()].sort((a, b) => (a.date < b.date ? -1 : 1));
}

export function trackingStreak(entries: HealthEntry[], today: string): number {
  const dates = [...new Set(entries.map((e) => e.date).filter((d) => d <= today))].sort().reverse();
  if (!dates.length || days(dates[0], today) > 1) return 0;
  let streak = 1;
  for (let i = 1; i < dates.length && days(dates[i], dates[i - 1]) === 1; i += 1) streak += 1;
  return streak;
}

function longestStreak(dates: string[]): number {
  if (!dates.length) return 0;
  let longest = 1, current = 1;
  for (let i = 1; i < dates.length; i += 1) {
    current = days(dates[i - 1], dates[i]) === 1 ? current + 1 : 1;
    longest = Math.max(longest, current);
  }
  return longest;
}

export function calculateDashboard(entries: HealthEntry[], goals: Goals, today: string): DashboardStats {
  const rows = sortedUnique(entries);
  if (!rows.length) {
    return { entryCount: 0, totalSteps: 0, averageSteps: 0, averageWaterL: 0, averageCalories: null, stepGoalDays: 0, waterGoalDays: 0,
      perfectGoalDays: 0, currentStreakDays: 0, longestTrackingStreakDays: 0, longestGoalStreakDays: 0, bestSteps: 0, bestDate: null,
      recentStepChangePct: null, dominantMood: null, trackingCoveragePct: 0, consistencyScore: 0, bestWeekday: null, activeLast7Days: 0,
      latestDate: null, daysSinceLatest: null, isStale: false };
  }
  const calories = rows.flatMap((e) => (e.calories == null ? [] : [e.calories]));
  const best = rows.reduce((b, e) => (e.steps > b.steps || (e.steps === b.steps && e.date > b.date) ? e : b));
  const moodCounts = new Map<string, number>();
  for (const e of rows) if (e.mood) moodCounts.set(e.mood, (moodCounts.get(e.mood) ?? 0) + 1);
  const latest = rows[rows.length - 1].date;
  const daysSinceLatest = Math.max(0, days(latest, today));
  const coverage = Math.min(100, (rows.length / Math.max(1, days(rows[0].date, latest) + 1)) * 100);
  const stepGoalDays = rows.filter((e) => e.steps >= goals.stepGoal).length;
  const waterGoalDays = rows.filter((e) => e.waterL >= goals.waterGoalL).length;
  const activeLast7 = rows.filter((e) => e.date <= today && days(e.date, today) <= 6).length;
  const score = pyRound(coverage * 0.3 + (stepGoalDays / rows.length) * 100 * 0.25 + (waterGoalDays / rows.length) * 100 * 0.25 + (activeLast7 / 7) * 100 * 0.2);
  let goalStreak = 0, current = 0, previous: string | null = null;
  for (const e of rows) {
    const consecutive = previous != null && days(previous, e.date) === 1;
    current = meetsBoth(e, goals) ? (consecutive ? current + 1 : 1) : 0;
    goalStreak = Math.max(goalStreak, current);
    previous = e.date;
  }
  let recent: number | null = null;
  if (rows.length >= 14) {
    const now = mean(rows.slice(-7).map((e) => e.steps)), before = mean(rows.slice(-14, -7).map((e) => e.steps));
    recent = before === 0 ? (now > 0 ? 100 : 0) : pyRound(((now - before) / before) * 100, 1);
  }
  const weekdays = new Map<number, number[]>();
  for (const e of rows) {
    const wd = (parseIsoDate(e.date).getUTCDay() + 6) % 7;
    weekdays.set(wd, [...(weekdays.get(wd) ?? []), e.steps]);
  }
  const bestWeekday = weekdays.size ? [...weekdays.entries()].sort((a, b) => mean(b[1]) - mean(a[1]) || a[0] - b[0])[0][0] : null;
  return {
    entryCount: rows.length,
    totalSteps: rows.reduce((s, e) => s + e.steps, 0),
    averageSteps: pyRound(mean(rows.map((e) => e.steps))),
    averageWaterL: pyRound(mean(rows.map((e) => e.waterL)), 2),
    averageCalories: calories.length ? pyRound(mean(calories)) : null,
    stepGoalDays,
    waterGoalDays,
    perfectGoalDays: rows.filter((e) => meetsBoth(e, goals)).length,
    currentStreakDays: trackingStreak(rows, today),
    longestTrackingStreakDays: longestStreak(rows.map((e) => e.date)),
    longestGoalStreakDays: goalStreak,
    bestSteps: best.steps,
    bestDate: best.date,
    recentStepChangePct: recent,
    dominantMood: [...moodCounts.entries()].sort((a, b) => b[1] - a[1])[0]?.[0] ?? null,
    trackingCoveragePct: pyRound(coverage, 1),
    consistencyScore: Math.max(0, Math.min(100, score)),
    bestWeekday,
    activeLast7Days: activeLast7,
    latestDate: latest,
    daysSinceLatest,
    isStale: daysSinceLatest > 7,
  };
}

export interface DailyPoint {
  date: string;
  steps: number;
  waterL: number;
  calories: number | null;
  mood: string | null;
  tracked: boolean;
}

export function dailySeries(entries: HealthEntry[], count: number, end: string): DailyPoint[] {
  const byDate = new Map(entries.map((e) => [e.date, e]));
  const last = parseIsoDate(end).getTime();
  return Array.from({ length: count }, (_, i) => {
    const date = toIso(new Date(last - (count - 1 - i) * DAY));
    const e = byDate.get(date);
    return { date, steps: e?.steps ?? 0, waterL: e?.waterL ?? 0, calories: e?.calories ?? null, mood: e?.mood ?? null, tracked: !!e };
  });
}

/** Trailing rolling average, `null` until the window is full (analytics.py rolling_average). */
export function rollingAverage(values: number[], window = 7): Array<number | null> {
  if (window <= 0) throw new Error('Rolling-average window must be positive.');
  return values.map((_, i) => (i - window + 1 < 0 ? null : pyRound(mean(values.slice(i - window + 1, i + 1)), 2)));
}

export interface WeekdayAverage {
  weekday: number; // 0 = Monday
  count: number;
  averageSteps: number;
  averageWaterL: number;
}

/** Monday-first averages per weekday (analytics.py build_weekday_profile). */
export function weekdayProfile(entries: HealthEntry[]): WeekdayAverage[] {
  const steps: number[][] = Array.from({ length: 7 }, () => []);
  const water: number[][] = Array.from({ length: 7 }, () => []);
  for (const e of entries) {
    const wd = (parseIsoDate(e.date).getUTCDay() + 6) % 7;
    steps[wd].push(e.steps);
    water[wd].push(e.waterL);
  }
  return steps.map((list, weekday) => ({
    weekday,
    count: list.length,
    averageSteps: list.length ? pyRound(mean(list)) : 0,
    averageWaterL: list.length ? pyRound(mean(water[weekday]), 2) : 0,
  }));
}

/** Most frequent moods, ties by name (analytics.py build_mood_distribution); `null` = not recorded. */
export function moodDistribution(entries: HealthEntry[], limit = 6): Array<[string | null, number]> {
  if (limit <= 0) throw new Error('Mood limit must be positive.');
  const counts = new Map<string | null, number>();
  for (const e of entries) {
    const mood = e.mood?.trim() || null;
    counts.set(mood, (counts.get(mood) ?? 0) + 1);
  }
  const name = (m: string | null) => (m ?? 'Not recorded').toLowerCase();
  return [...counts.entries()].sort((a, b) => b[1] - a[1] || name(a[0]).localeCompare(name(b[0]))).slice(0, limit);
}

/** Daily routine score 0–100 used by the desktop Trend Lab: half steps, half water, capped at each goal. */
export function routineScore(point: DailyPoint, goals: Goals): number {
  if (!point.tracked) return 0;
  return Math.min(1, point.steps / goals.stepGoal) * 50 + Math.min(1, point.waterL / goals.waterGoalL) * 50;
}
