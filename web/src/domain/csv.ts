// Desktop-compatible CSV (novafit/io_utils.py): header "Date,Steps,Water (L),Calories,Mood,Note", UTF-8 with BOM,
// spreadsheet formula guard on text cells, tolerant column aliases on import.
import { buildEntry, type HealthEntry } from './entries';

const HEADER = ['Date', 'Steps', 'Water (L)', 'Calories', 'Mood', 'Note'];
const safe = (value: string) => (value && '=+-@'.includes(value[0]) ? `'${value}` : value);
const quote = (value: string) => (/[",\r\n]/.test(value) ? `"${value.replace(/"/g, '""')}"` : value);

export function entriesToCsv(entries: HealthEntry[]): string {
  const rows = entries.map((e) => [e.date, String(e.steps), String(e.waterL), e.calories == null ? '' : String(e.calories), safe(e.mood ?? ''), safe(e.note ?? '')]);
  return '﻿' + [HEADER, ...rows].map((row) => row.map(quote).join(',')).join('\r\n') + '\r\n';
}

/** RFC 4180 parser: quoted fields, doubled quotes, CRLF or LF, optional BOM. */
export function parseCsv(text: string): string[][] {
  const rows: string[][] = [];
  let row: string[] = [], field = '', quoted = false;
  const input = text.replace(/^﻿/, '');
  for (let i = 0; i < input.length; i += 1) {
    const c = input[i];
    if (quoted) {
      if (c === '"' && input[i + 1] === '"') { field += '"'; i += 1; }
      else if (c === '"') quoted = false;
      else field += c;
    } else if (c === '"') quoted = true;
    else if (c === ',') { row.push(field); field = ''; }
    else if (c === '\n' || c === '\r') {
      if (c === '\r' && input[i + 1] === '\n') i += 1;
      row.push(field); rows.push(row); row = []; field = '';
    } else field += c;
  }
  if (field || row.length) { row.push(field); rows.push(row); }
  return rows.filter((r) => r.some((cell) => cell.trim() !== ''));
}

export function csvToEntries(text: string): { entries: HealthEntry[]; invalid: number; errors: string[] } {
  const [header = [], ...rows] = parseCsv(text);
  const index = (...names: string[]) => header.findIndex((h) => names.includes(h.trim().toLowerCase()));
  const col = { date: index('date', 'entry_date'), steps: index('steps'), water: index('water (l)', 'water_l', 'water'), calories: index('calories'), mood: index('mood'), note: index('note') };
  const out = { entries: [] as HealthEntry[], invalid: 0, errors: [] as string[] };
  const unguard = (v: string) => (v.startsWith("'") && '=+-@'.includes(v[1] ?? '') ? v.slice(1) : v);
  rows.slice(0, 100_000).forEach((r, i) => {
    const cell = (k: keyof typeof col) => (col[k] >= 0 ? (r[col[k]] ?? '') : '');
    try {
      out.entries.push(buildEntry({ date: cell('date'), steps: cell('steps'), waterL: cell('water'), calories: cell('calories'), mood: unguard(cell('mood')), note: unguard(cell('note')) }));
    } catch (error) {
      out.invalid += 1;
      if (out.errors.length < 20) out.errors.push(`Row ${i + 2}: ${error instanceof Error ? error.message : String(error)}`);
    }
  });
  return out;
}
