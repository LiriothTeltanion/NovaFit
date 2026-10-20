// Mirrors tests/test_analytics.py style cases so the web dashboard matches the desktop numbers.
import { calculateDashboard, dailySeries, DEFAULT_GOALS, moodDistribution, rollingAverage, routineScore, trackingStreak, weekdayProfile } from './analytics';
import { buildEntry, canonicalMood, EntryValidationError, moodLabel } from './entries';
import { tr } from '../i18n';

const e = (date: string, steps: number, waterL: number, mood = '') => buildEntry({ date, steps, waterL, mood });

describe('entries', () => {
  it('validates like the desktop and keeps canonical moods', () => {
    expect(buildEntry({ date: '2026-10-19', steps: '9000', waterL: '2,5', calories: '', mood: 'Concentrado', note: '  hi  ' })).toEqual({
      date: '2026-10-19', steps: 9000, waterL: 2.5, calories: null, mood: 'Focused', note: 'hi',
    });
    expect(() => e('2026-10-19', -1, 1)).toThrow(EntryValidationError);
    expect(() => e('2026-10-19', 200_001, 1)).toThrow(EntryValidationError);
    expect(() => e('2026-10-19', 10, 21)).toThrow(EntryValidationError);
    expect(canonicalMood('happy')).toBe('Happy');
    expect(moodLabel('Happy', 'es')).toBe(tr('es', 'mood_happy'));
  });
});

describe('dashboard', () => {
  it('computes goals, streaks and the routine score', () => {
    const rows = [e('2026-07-13', 10000, 2.5, 'Focused'), e('2026-07-14', 12000, 2.1, 'Focused'), e('2026-07-15', 3000, 1.0, 'Tired')];
    const stats = calculateDashboard(rows, DEFAULT_GOALS, '2026-07-16');
    expect(stats).toMatchObject({ entryCount: 3, totalSteps: 25000, averageSteps: 8333, stepGoalDays: 2, waterGoalDays: 2, perfectGoalDays: 2,
      currentStreakDays: 3, longestTrackingStreakDays: 3, longestGoalStreakDays: 2, bestSteps: 12000, bestDate: '2026-07-14', dominantMood: 'Focused',
      trackingCoveragePct: 100, bestWeekday: 1, isStale: false });
    // 100 × .3 + 66.67 × .25 + 66.67 × .25 + (3 / 7 × 100) × .2 = 71.9 → 72
    expect(stats.consistencyScore).toBe(72);
  });

  it('breaks the streak after a missed day and reports gaps in the series', () => {
    const rows = [e('2026-07-10', 1, 1), e('2026-07-11', 1, 1)];
    expect(trackingStreak(rows, '2026-07-12')).toBe(2);
    expect(trackingStreak(rows, '2026-07-13')).toBe(0);
    const series = dailySeries(rows, 4, '2026-07-12');
    expect(series.map((p) => p.tracked)).toEqual([false, true, true, false]);
  });
});

describe('trend lab helpers (analytics.py parity)', () => {
  it('rolls a trailing average like the doctest', () => {
    expect(rollingAverage([1, 2, 3], 2)).toEqual([null, 1.5, 2.5]);
    expect(() => rollingAverage([1], 0)).toThrow();
  });

  it('builds a Monday-first weekday profile', () => {
    const profile = weekdayProfile([e('2026-10-19', 8000, 2), e('2026-10-26', 10000, 2.5), e('2026-10-25', 4000, 1)]);
    expect(profile).toHaveLength(7);
    expect(profile[0]).toEqual({ weekday: 0, count: 2, averageSteps: 9000, averageWaterL: 2.25 });
    expect(profile[6]).toMatchObject({ count: 1, averageSteps: 4000 });
    expect(weekdayProfile([]).every((d) => d.count === 0)).toBe(true);
  });

  it('counts moods by frequency, then name, with unrecorded days', () => {
    const rows = [e('2026-10-17', 1, 1, 'Calm'), e('2026-10-18', 1, 1, 'Happy'), e('2026-10-19', 1, 1, 'Happy'), e('2026-10-20', 1, 1)];
    expect(moodDistribution(rows)).toEqual([['Happy', 2], ['Calm', 1], [null, 1]]);
    expect(moodDistribution(rows, 1)).toEqual([['Happy', 2]]);
  });

  it('scores a day out of 100 with both goals capped', () => {
    const [point] = dailySeries([e('2026-10-19', 15000, 1)], 1, '2026-10-19');
    expect(routineScore(point, DEFAULT_GOALS)).toBe(75);
  });
});

