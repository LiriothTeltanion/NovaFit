// Port of novafit/recommendations.py (Sport & Data Coach). Copy and weekly rhythms come from the Python
// module via coach.json; thresholds and ordering are the same, including the training cards.
import coach from '../generated/coach.json';
import type { Language } from '../i18n';
import { calculateDashboard, type Goals } from './analytics';
import type { HealthEntry } from './entries';
import { parseIsoDate, sessionLoad, type WorkoutSession } from './workouts';

export type Priority = 'high' | 'medium' | 'low';
export interface RecommendationItem {
  category: string;
  title: string;
  action: string;
  reason: string;
  priority: Priority;
}
export interface RecommendationPlan {
  confidencePct: number;
  summary: string;
  weekly: string[];
  items: RecommendationItem[];
  disclaimer: string;
}
export type ActivityLevel = 'beginner' | 'balanced' | 'active';

const COPY = coach.copy as Record<Language, Record<string, string>>;
const RHYTHM = coach.weeklyRhythm as Record<Language, Record<ActivityLevel, string[]>>;
const FOCUS = coach.focusLine as Record<Language, string>;
export const LOAD_JUMP_RATIO: number = coach.loadJumpRatio;

export interface TrainingSignals {
  totalSessions: number;
  sessions14d: number;
  loadRatio: number | null;
  singleKind: string | null;
}

export function trainingSignals(sessions: WorkoutSession[], today: string): TrainingSignals {
  const t = parseIsoDate(today).getTime();
  const age = (s: WorkoutSession) => Math.round((t - parseIsoDate(s.date).getTime()) / 86_400_000);
  const within = (s: WorkoutSession, a: number, b: number) => age(s) >= a && age(s) <= b;
  const acute = sessions.filter((s) => within(s, 0, 6));
  const chronic = sessions.filter((s) => within(s, 7, 27));
  const acuteLoad = acute.reduce((n, s) => n + (sessionLoad(s) ?? 0), 0);
  const chronicWeekly = chronic.reduce((n, s) => n + (sessionLoad(s) ?? 0), 0) / 3;
  const recent = sessions.filter((s) => within(s, 0, 27));
  const kinds = new Set(recent.map((s) => s.kind));
  return {
    totalSessions: sessions.length,
    sessions14d: sessions.filter((s) => within(s, 0, 13)).length,
    loadRatio: chronicWeekly > 0 && acute.some((s) => sessionLoad(s)) ? Math.round((acuteLoad / chronicWeekly) * 100) / 100 : null,
    singleKind: recent.length >= 4 && kinds.size === 1 ? [...kinds][0] : null,
  };
}

function trainingItems(sessions: WorkoutSession[] | null, language: Language, today: string, kindLabel: (k: string) => string): RecommendationItem[] {
  if (sessions == null) return [];
  const c = COPY[language];
  const s = trainingSignals(sessions, today);
  if (s.totalSessions === 0) return [{ category: 'training', title: c.start_title, action: c.start_action, reason: c.start_reason, priority: 'low' }];
  const items: RecommendationItem[] = [];
  if (s.loadRatio != null && s.loadRatio >= LOAD_JUMP_RATIO) {
    items.push({ category: 'training', title: c.load_title, action: c.load_action, reason: c.load_reason.replace('{pct}', String(Math.round((s.loadRatio - 1) * 100))), priority: 'high' });
  } else if (s.sessions14d === 0) {
    items.push({ category: 'training', title: c.resume_title, action: c.resume_action, reason: c.resume_reason, priority: 'medium' });
  }
  if (s.singleKind) {
    const kind = kindLabel(s.singleKind).toLocaleLowerCase();
    items.push({ category: 'training', title: c.variety_title, action: c.variety_action.replace('{kind}', kind), reason: c.variety_reason.replace('{kind}', kind), priority: 'low' });
  }
  return items;
}

export function buildPlan(
  entries: HealthEntry[],
  goals: Goals,
  level: ActivityLevel,
  language: Language,
  today: string,
  sessions: WorkoutSession[] | null,
  kindLabel: (k: string) => string,
  focusLabel?: string,
): RecommendationPlan {
  const c = COPY[language];
  const stats = calculateDashboard(entries, goals, today);
  const confidencePct = Math.min(100, Math.round(Math.min(1, stats.entryCount / 14) * 70 + Math.min(1, stats.trackingCoveragePct / 100) * 30));
  const summary = stats.entryCount === 0 ? c.empty : confidencePct < 65 ? c.emerging : c.stable;
  const items: RecommendationItem[] = [];
  if (stats.entryCount < 7) items.push({ category: 'data', title: c.track_title, action: c.track_action, reason: c.track_reason, priority: 'high' });
  else if (stats.trackingCoveragePct < 75) items.push({ category: 'data', title: c.coverage_title, action: c.coverage_action, reason: c.coverage_reason, priority: 'high' });
  if (stats.entryCount && stats.averageSteps < goals.stepGoal * 0.5) items.push({ category: 'movement', title: c.walk_title, action: c.walk_action, reason: c.walk_reason, priority: 'high' });
  else items.push({ category: 'movement', title: c.progress_title, action: c.progress_action, reason: c.progress_reason, priority: 'medium' });
  const training = trainingItems(sessions, language, today, kindLabel);
  items.push(...training.filter((i) => i.priority !== 'low'));
  if (stats.entryCount && stats.averageWaterL < goals.waterGoalL) items.push({ category: 'hydration', title: c.water_title, action: c.water_action, reason: c.water_reason, priority: 'medium' });
  items.push({ category: 'recovery', title: c.recovery_title, action: c.recovery_action, reason: c.recovery_reason, priority: 'medium' });
  const moodDays = entries.filter((e) => e.mood).length;
  if (stats.entryCount >= 4 && moodDays / Math.max(1, stats.entryCount) < 0.5) items.push({ category: 'context', title: c.mood_title, action: c.mood_action, reason: c.mood_reason, priority: 'low' });
  items.push(...training.filter((i) => i.priority === 'low'));
  return { confidencePct, summary, weekly: focusLabel ? [...RHYTHM[language][level], FOCUS[language].replace('{focus}', focusLabel)] : RHYTHM[language][level], items: items.slice(0, 5), disclaimer: c.disclaimer };
}
