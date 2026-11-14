// Port of novafit/motivation.py: the same grounded headline, micro-action, weekly challenge, milestone and badges.
import { tr, type Language } from '../i18n';
import { calculateDashboard, type Goals } from './analytics';
import type { HealthEntry } from './entries';
import { parseIsoDate } from './workouts';

export interface Achievement {
  title: string;
  description: string;
  earned: boolean;
  progressPct: number;
  icon: string;
}

export interface MotivationSnapshot {
  headline: string;
  message: string;
  dailySpark: string;
  microAction: string;
  weeklyChallenge: string;
  nextMilestone: string;
  milestoneProgressPct: number;
  celebrationLevel: number;
  achievements: Achievement[];
}

/** Python's date.toordinal() for an ISO date (1970-01-01 is ordinal 719163). */
export const ordinal = (iso: string) => Math.round(parseIsoDate(iso).getTime() / 86_400_000) + 719_163;

export function sparkKey(today: string, entryCount: number, offset = 0): string {
  return `spark_${((ordinal(today) + entryCount + offset) % 8) + 1}`;
}

export function buildMotivation(entries: HealthEntry[], goals: Goals, language: Language, today: string, sparkOffset = 0): MotivationSnapshot {
  const t = (key: string, values?: Record<string, string | number>) => tr(language, key, values);
  const s = calculateDashboard(entries, goals, today);
  const spark = t(sparkKey(today, s.entryCount, sparkOffset));
  const badges: Array<[string, string, number, number, string]> = [
    ['achievement_first_title', 'achievement_first_body', s.entryCount, 1, '🌱'],
    ['achievement_week_title', 'achievement_week_body', s.entryCount, 7, '🧱'],
    ['achievement_month_title', 'achievement_month_body', s.entryCount, 30, '🗓️'],
    ['achievement_rhythm_title', 'achievement_rhythm_body', s.longestTrackingStreakDays, 7, '🔥'],
    ['achievement_goals_title', 'achievement_goals_body', s.perfectGoalDays, 7, '✨'],
    ['achievement_momentum_title', 'achievement_momentum_body', s.consistencyScore, 75, '🚀'],
  ];
  const achievements = badges.map(([title, body, value, target, icon]) => ({
    title: t(title), description: t(body), earned: value >= target, progressPct: Math.min(100, Math.round((value / target) * 100)), icon,
  }));
  if (s.entryCount === 0) {
    return { headline: t('motivation_empty_headline'), message: t('motivation_empty_message'), dailySpark: spark, microAction: t('motivation_empty_action'),
      weeklyChallenge: t('motivation_empty_challenge'), nextMilestone: t('motivation_first_milestone'), milestoneProgressPct: 0, celebrationLevel: 0, achievements };
  }
  const headline = s.currentStreakDays >= 14 ? t('motivation_headline_streak', { days: s.currentStreakDays })
    : s.consistencyScore >= 80 ? t('motivation_headline_dependable')
    : s.recentStepChangePct != null && s.recentStepChangePct > 8 ? t('motivation_headline_climbing')
    : s.activeLast7Days >= 5 ? t('motivation_headline_returning') : t('motivation_headline_next');
  const stepRate = (s.stepGoalDays / s.entryCount) * 100;
  const waterRate = (s.waterGoalDays / s.entryCount) * 100;
  const weakest = [[s.trackingCoveragePct, 'tracking'], [stepRate, 'steps'], [waterRate, 'water']].reduce((a, b) => ((b[0] as number) < (a[0] as number) ? b : a))[1] as string;
  const microAction = weakest === 'tracking' ? t('motivation_action_tracking')
    : weakest === 'steps' ? t('motivation_action_steps', { goal: goals.stepGoal.toLocaleString('en') })
    : t('motivation_action_water', { goal: goals.waterGoalL.toFixed(1) });
  let nextMilestone = t('motivation_archive_complete'), milestoneProgressPct = 100;
  const days = [3, 7, 14, 30, 60, 90, 180, 365].find((target) => s.entryCount < target);
  const streak = [3, 7, 14, 30, 60].find((target) => s.currentStreakDays < target);
  if (days) [nextMilestone, milestoneProgressPct] = [t('motivation_milestone_days', { target: days }), Math.min(99, Math.round((s.entryCount / days) * 100))];
  else if (streak) [nextMilestone, milestoneProgressPct] = [t('motivation_milestone_streak', { target: streak }), Math.min(99, Math.round((s.currentStreakDays / streak) * 100))];
  return {
    headline,
    message: t('motivation_message', { entries: s.entryCount, streak: s.currentStreakDays, score: s.consistencyScore, perfect: s.perfectGoalDays }),
    dailySpark: spark,
    microAction,
    weeklyChallenge: t(`motivation_challenge_${weakest}`),
    nextMilestone,
    milestoneProgressPct,
    celebrationLevel: s.consistencyScore >= 85 ? 3 : s.consistencyScore >= 65 ? 2 : 1,
    achievements,
  };
}
