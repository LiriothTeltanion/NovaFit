import { REFERENCE_WEEKLY_MINUTES, type TrainingWeek } from '../domain/workouts';
import { tr, type Language } from '../i18n';

const W = 640;
const H = 220;
const PAD = 30;

/** Minutes per week against the WHO reference line; the current week is highlighted. */
export function WeeklyBars({ weeks, language }: { weeks: TrainingWeek[]; language: Language }) {
  const peak = Math.max(REFERENCE_WEEKLY_MINUTES, ...weeks.map((w) => w.minutes)) || 1;
  const baseline = H - PAD;
  const y = (minutes: number) => baseline - ((H - PAD * 2) * minutes) / peak;
  const slot = (W - PAD * 2) / Math.max(1, weeks.length);
  const lineY = y(REFERENCE_WEEKLY_MINUTES);
  const empty = weeks.every((w) => w.minutes === 0);
  const label = `${tr(language, 'training_weekly_minutes')}: ${weeks.map((w) => `${w.weekStart} ${w.minutes}`).join(', ')}`;
  return (
    <svg className="bars" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={label} preserveAspectRatio="xMidYMid meet">
      <line className="bars__reference" x1={PAD} x2={W - PAD} y1={lineY} y2={lineY} />
      <text className="bars__reference-label" x={W - PAD} y={lineY - 7} textAnchor="end">
        {REFERENCE_WEEKLY_MINUTES} min
      </text>
      {weeks.map((week, index) => {
        const x = PAD + slot * index + slot * 0.21;
        const top = y(week.minutes);
        const current = index === weeks.length - 1;
        const nearLine = Math.abs(top - 9 - lineY) < 9 && baseline - top > 24;
        return (
          <g key={week.weekStart}>
            {week.minutes > 0 && (
              <>
                <rect className={current ? 'bars__bar bars__bar--current' : 'bars__bar'} x={x} y={top} width={slot * 0.58} height={baseline - top} rx={5} />
                <text className={nearLine ? 'bars__value bars__value--inside' : 'bars__value'} x={x + slot * 0.29} y={nearLine ? top + 15 : top - 7} textAnchor="middle">
                  {week.minutes}
                </text>
              </>
            )}
            <text className="bars__axis" x={x + slot * 0.29} y={baseline + 17} textAnchor="middle">
              {week.weekStart.slice(8, 10)}/{week.weekStart.slice(5, 7)}
            </text>
          </g>
        );
      })}
      {empty && (
        <text className="bars__empty" x={W / 2} y={H / 2} textAnchor="middle">
          {tr(language, 'training_empty')}
        </text>
      )}
    </svg>
  );
}
