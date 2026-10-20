import type { DailyPoint } from '../domain/analytics';

const W = 640;
const H = 220;
const PAD = 30;

/** Daily bars with a dashed goal line; untracked days show a faint stub so gaps stay honest. */
export function DailyBars({ points, value, goal, label, format }: { points: DailyPoint[]; value: (p: DailyPoint) => number; goal: number; label: string; format: (v: number) => string }) {
  const peak = Math.max(goal, ...points.map(value)) || 1;
  const base = H - PAD;
  const y = (v: number) => base - ((H - PAD * 2) * v) / peak;
  const slot = (W - PAD * 2) / Math.max(1, points.length);
  const goalY = y(goal);
  return (
    <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`${label}: ${points.map((p) => `${p.date} ${p.tracked ? format(value(p)) : '—'}`).join(', ')}`}>
      <line className="chart__goal" x1={PAD} x2={W - PAD} y1={goalY} y2={goalY} />
      <text className="chart__goal-label" x={W - PAD} y={goalY - 6} textAnchor="end">{format(goal)}</text>
      {points.map((p, i) => {
        const x = PAD + slot * i + slot * 0.18;
        const w = slot * 0.64;
        const v = value(p);
        const met = v >= goal;
        return (
          <g key={p.date}>
            {p.tracked ? (
              <rect className={met ? 'chart__bar chart__bar--met' : 'chart__bar'} x={x} y={y(v)} width={w} height={Math.max(2, base - y(v))} rx={4} />
            ) : (
              <rect className="chart__bar chart__bar--missing" x={x} y={base - 3} width={w} height={3} rx={1.5} />
            )}
            {(i % Math.ceil(points.length / 7) === 0 || i === points.length - 1) && (
              <text className="chart__axis" x={x + w / 2} y={base + 16} textAnchor="middle">{p.date.slice(8, 10)}/{p.date.slice(5, 7)}</text>
            )}
          </g>
        );
      })}
    </svg>
  );
}

/** Smooth area for water with the goal line. */
export function WaterArea({ points, goal, label }: { points: DailyPoint[]; goal: number; label: string }) {
  const peak = Math.max(goal * 1.2, ...points.map((p) => p.waterL)) || 1;
  const base = H - PAD;
  const x = (i: number) => PAD + ((W - PAD * 2) * i) / Math.max(1, points.length - 1);
  const y = (v: number) => base - ((H - PAD * 2) * v) / peak;
  const tracked = points.map((p, i) => ({ p, i })).filter(({ p }) => p.tracked);
  const line = tracked.map(({ p, i }, k) => `${k ? 'L' : 'M'}${x(i).toFixed(1)} ${y(p.waterL).toFixed(1)}`).join(' ');
  const area = tracked.length ? `${line} L${x(tracked[tracked.length - 1].i).toFixed(1)} ${base} L${x(tracked[0].i).toFixed(1)} ${base} Z` : '';
  return (
    <svg className="chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`${label}: ${tracked.map(({ p }) => `${p.date} ${p.waterL} L`).join(', ')}`}>
      <defs>
        <linearGradient id="nf-water" x1="0" x2="0" y1="0" y2="1">
          <stop offset="0" stopColor="var(--nf-blue, var(--nf-accent))" stopOpacity=".55" />
          <stop offset="1" stopColor="var(--nf-blue, var(--nf-accent))" stopOpacity="0" />
        </linearGradient>
      </defs>
      <line className="chart__goal" x1={PAD} x2={W - PAD} y1={y(goal)} y2={y(goal)} />
      <text className="chart__goal-label" x={W - PAD} y={y(goal) - 6} textAnchor="end">{goal} L</text>
      {area && <path d={area} fill="url(#nf-water)" />}
      {line && <path className="chart__line" d={line} />}
      {tracked.map(({ p, i }) => (
        <circle key={p.date} className="chart__dot" cx={x(i)} cy={y(p.waterL)} r={3.2} />
      ))}
    </svg>
  );
}

/** Seven-week consistency map: one cell per day, colour by goals met. */
export function ConsistencyMap({ points, stepGoal, waterGoal, label, weekdays }: { points: DailyPoint[]; stepGoal: number; waterGoal: number; label: string; weekdays: string[] }) {
  const cell = 20;
  const gap = 4;
  const firstOffset = (new Date(`${points[0].date}T00:00:00Z`).getUTCDay() + 6) % 7;
  const columns = Math.ceil((points.length + firstOffset) / 7);
  const width = 34 + columns * (cell + gap);
  const height = 7 * (cell + gap);
  return (
    <svg className="chart chart--map" viewBox={`0 0 ${width} ${height}`} role="img" aria-label={label}>
      {weekdays.map((d, r) => (
        <text key={d} className="chart__axis" x={0} y={r * (cell + gap) + 14}>{d.slice(0, 2)}</text>
      ))}
      {points.map((p, i) => {
        const index = i + firstOffset;
        const level = !p.tracked ? 'none' : p.steps >= stepGoal && p.waterL >= waterGoal ? 'both' : p.steps >= stepGoal || p.waterL >= waterGoal ? 'one' : 'tracked';
        return (
          <rect key={p.date} className={`map__cell map__cell--${level}`} x={34 + Math.floor(index / 7) * (cell + gap)} y={(index % 7) * (cell + gap)} width={cell} height={cell} rx={5}>
            <title>{p.date}</title>
          </rect>
        );
      })}
    </svg>
  );
}
