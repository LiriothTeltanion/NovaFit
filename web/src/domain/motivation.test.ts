import { buildMotivation, ordinal, sparkKey } from './motivation';
import { DEFAULT_GOALS } from './analytics';
import { buildEntry } from './entries';

describe('motivation port', () => {
  it('matches Python date.toordinal and the spark rotation', () => {
    expect(ordinal('1970-01-01')).toBe(719163);
    expect(ordinal('2026-10-20')).toBe(739909);
    expect(sparkKey('2026-10-20', 0)).toBe('spark_6'); // (739909 + 0) % 8 = 5 → spark_6
  });

  it('starts empty and then earns badges from real records', () => {
    expect(buildMotivation([], DEFAULT_GOALS, 'en', '2026-10-20').headline).toBe('Begin with one honest record.');
    const rows = Array.from({ length: 8 }, (_, i) => buildEntry({ date: `2026-10-${String(13 + i).padStart(2, '0')}`, steps: 11000, waterL: 2.5 }));
    const m = buildMotivation(rows, DEFAULT_GOALS, 'es', '2026-10-20');
    expect(m.achievements.filter((a) => a.earned).map((a) => a.icon)).toEqual(['🌱', '🧱', '🔥', '✨', '🚀']);
    expect(m.milestoneProgressPct).toBe(57); // 8 of 14 days
    expect(m.celebrationLevel).toBe(3);
  });
});
