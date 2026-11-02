import { readPrefs, readProfilePrefs, savePrefs, DEFAULT_PREFS } from './settings';

beforeEach(() => {
  localStorage.clear();
  window.history.replaceState(null, '', '/');
});

describe('per-profile preferences', () => {
  it('migrates the pre-profile key into profile 1', () => {
    localStorage.setItem('novafit-web:prefs', JSON.stringify({ language: 'he', theme: 'solar', goals: { stepGoal: 8000 }, why: 'walk' }));
    const prefs = readPrefs();
    expect(prefs).toMatchObject({ profileId: 1, language: 'he', theme: 'solar', why: 'walk', sportFocus: 'mixed' });
    expect(prefs.goals.stepGoal).toBe(8000);
  });

  it('keeps each profile separate and remembers the active one', () => {
    savePrefs({ ...DEFAULT_PREFS, profileId: 1, language: 'es', goals: { ...DEFAULT_PREFS.goals, stepGoal: 12000 } });
    const second = readProfilePrefs(2, readPrefs());
    expect(second).toMatchObject({ profileId: 2, language: 'es', why: '' }); // inherits language, not goals
    expect(second.goals.stepGoal).toBe(10000);
    savePrefs({ ...second, sportFocus: 'running', goals: { ...second.goals, waterGoalL: 3 } });
    expect(readPrefs()).toMatchObject({ profileId: 2, sportFocus: 'running' });
    expect(readProfilePrefs(1).goals.stepGoal).toBe(12000);
    expect(readProfilePrefs(2).goals.waterGoalL).toBe(3);
  });

  it('lets the URL override language and theme for a visit', () => {
    savePrefs({ ...DEFAULT_PREFS, language: 'es' });
    window.history.replaceState(null, '', '/?lang=he&theme=cloud');
    expect(readPrefs()).toMatchObject({ language: 'he', theme: 'cloud' });
  });
});
