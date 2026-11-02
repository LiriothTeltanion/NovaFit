import { csvToEntries, entriesToCsv, parseCsv } from './csv';
import { buildEntry } from './entries';

describe('desktop-compatible CSV', () => {
  it('round-trips records, quotes commas and guards formulas', () => {
    const entries = [
      buildEntry({ date: '2026-10-18', steps: 8000, waterL: 2.1, calories: 1900, mood: 'Calm', note: 'park, then "tea"' }),
      buildEntry({ date: '2026-10-19', steps: 500, waterL: 1, note: '=HYPERLINK("x")' }),
    ];
    const csv = entriesToCsv(entries);
    expect(csv.startsWith('﻿Date,Steps,Water (L),Calories,Mood,Note\r\n')).toBe(true);
    expect(csv).toContain(`"'=HYPERLINK(""x"")"`);
    const back = csvToEntries(csv);
    expect(back.invalid).toBe(0);
    expect(back.entries).toEqual(entries);
  });

  it('accepts the desktop aliases and reports bad rows', () => {
    const text = 'date,steps,water_l,mood\n2026-10-18,5000,1.5,Happy\n2026-13-01,1,1,\n';
    const result = csvToEntries(text);
    expect(result.entries).toHaveLength(1);
    expect(result.invalid).toBe(1);
    expect(result.errors[0]).toMatch(/Row 3/);
    expect(parseCsv('a,"b\nc"\r\n1,2')).toEqual([['a', 'b\nc'], ['1', '2']]);
  });
});
