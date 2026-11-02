import { useRef, useState, type FormEvent } from 'react';
import { Download, FileText, Upload } from 'lucide-react';
import type { ActivityLevel } from '../domain/coach';
import { tr, type Language } from '../i18n';
import { SPORT_FOCUSES, type Prefs, type SportFocus } from '../settings';

interface Props {
  language: Language;
  prefs: Prefs;
  onSave: (prefs: Prefs) => void;
  onExport: () => Promise<void>;
  onImport: (text: string) => Promise<string>;
  onExportCsv: () => Promise<void>;
  onExportReport: () => Promise<void>;
  onImportCsv: (text: string) => Promise<string>;
}

export function SettingsPage({ language, prefs, onSave, onExport, onImport, onExportCsv, onExportReport, onImportCsv }: Props) {
  const t = (key: string) => tr(language, key);
  const [draft, setDraft] = useState({ stepGoal: String(prefs.goals.stepGoal), waterGoalL: String(prefs.goals.waterGoalL), calorieGoal: String(prefs.goals.calorieGoal), activityLevel: prefs.activityLevel, sportFocus: prefs.sportFocus, why: prefs.why });
  const [message, setMessage] = useState<{ tone: 'ok' | 'error'; text: string } | null>(null);
  const fileInput = useRef<HTMLInputElement>(null);
  const csvInput = useRef<HTMLInputElement>(null);

  function submit(event: FormEvent) {
    event.preventDefault();
    const stepGoal = Number(draft.stepGoal), waterGoalL = Number(draft.waterGoalL.replace(',', '.')), calorieGoal = Number(draft.calorieGoal);
    if (!(Number.isInteger(stepGoal) && stepGoal > 0 && stepGoal <= 100_000) || !(waterGoalL > 0 && waterGoalL <= 10) || !(Number.isInteger(calorieGoal) && calorieGoal > 0 && calorieGoal <= 10_000)) {
      setMessage({ tone: 'error', text: `${t('preferences_save_error')}: 1–100000 · 0.1–10 L · 1–10000` });
      return;
    }
    onSave({ ...prefs, goals: { stepGoal, waterGoalL, calorieGoal }, activityLevel: draft.activityLevel, sportFocus: draft.sportFocus, why: draft.why.trim().slice(0, 160) });
    setMessage({ tone: 'ok', text: `${t('settings_saved')} ✅` });
  }

  async function importFile(file: File | undefined, csv = false) {
    if (!file) return;
    try {
      setMessage({ tone: 'ok', text: await (csv ? onImportCsv : onImport)(await file.text()) });
    } catch (error) {
      setMessage({ tone: 'error', text: `${t(csv ? 'csv_import_failed' : 'json_import_failed')}: ${error instanceof Error ? error.message : String(error)}` });
    } finally {
      for (const input of [fileInput.current, csvInput.current]) if (input) input.value = '';
    }
  }

  return (
    <section className="page" aria-labelledby="settings-title">
      <header className="page__header">
        <h1 id="settings-title">{t('nav_tools')}</h1>
        <p>{t('motivation_purpose_hint')}</p>
      </header>
      <div className="settings">
        <form className="card form" onSubmit={submit}>
          <h2 className="card__value">{t('goals')}</h2>
          <label>{t('step_goal')}<input inputMode="numeric" value={draft.stepGoal} onChange={(e) => setDraft({ ...draft, stepGoal: e.target.value })} /></label>
          <label>{t('water_goal')}<input inputMode="decimal" value={draft.waterGoalL} onChange={(e) => setDraft({ ...draft, waterGoalL: e.target.value })} /></label>
          <label>{t('calorie_reference')}<input inputMode="numeric" value={draft.calorieGoal} onChange={(e) => setDraft({ ...draft, calorieGoal: e.target.value })} /></label>
          <label>
            {t('activity_level')}
            <select value={draft.activityLevel} onChange={(e) => setDraft({ ...draft, activityLevel: e.target.value as ActivityLevel })}>
              {(['beginner', 'balanced', 'active'] as const).map((level) => <option key={level} value={level}>{t(`activity_${level}`)}</option>)}
            </select>
          </label>
          <label>
            {t('sport_focus')}
            <select value={draft.sportFocus} onChange={(e) => setDraft({ ...draft, sportFocus: e.target.value as SportFocus })}>
              {SPORT_FOCUSES.map((focus) => <option key={focus} value={focus}>{t(`sport_${focus}`)}</option>)}
            </select>
          </label>
          <label>
            {t('motivation_personal_why')}
            <input value={draft.why} maxLength={160} placeholder={t('web_why_placeholder')} onChange={(e) => setDraft({ ...draft, why: e.target.value })} />
          </label>
          <button className="button button--accent" type="submit">{t('save_preferences')}</button>
        </form>
        <article className="card form">
          <h2 className="card__value">{t('data_management')}</h2>
          <p className="card__detail">{t('web_import_hint')}</p>
          <button className="button button--quiet" type="button" onClick={() => void onExport()}><Download aria-hidden size={18} /> {t('export_json')}</button>
          <label className="button button--quiet file-button">
            <Upload aria-hidden size={18} /> {t('import_json')}
            <input ref={fileInput} type="file" accept="application/json,.json" className="visually-hidden" onChange={(e) => void importFile(e.target.files?.[0])} />
          </label>
          <button className="button button--quiet" type="button" onClick={() => void onExportCsv()}><Download aria-hidden size={18} /> {t('export_csv')}</button>
          <label className="button button--quiet file-button">
            <Upload aria-hidden size={18} /> {t('import_csv')}
            <input ref={csvInput} type="file" accept="text/csv,.csv" className="visually-hidden" onChange={(e) => void importFile(e.target.files?.[0], true)} />
          </label>
          <button className="button button--quiet" type="button" onClick={() => void onExportReport()}><FileText aria-hidden size={18} /> {t('export_report')}</button>
          <p className="card__detail">{t('web_storage_note')}</p>
        </article>
      </div>
      {message && <p className={`form__message form__message--${message.tone}`} role={message.tone === 'error' ? 'alert' : 'status'}>{message.text}</p>}
    </section>
  );
}
