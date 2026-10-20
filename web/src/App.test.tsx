import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { App } from './App';
import { NovaFitWebDb } from './db';
import { languageKeys, tr } from './i18n';

let counter = 0;
const freshStore = () => new NovaFitWebDb(`novafit-test-${++counter}`);
const open = (path: string) => window.history.replaceState(null, '', path);

beforeEach(() => {
  localStorage.clear();
  open('/');
});

describe('catalogue exported from the desktop app', () => {
  it('has the same keys in English, Spanish and Hebrew', () => {
    const en = languageKeys('en').sort();
    expect(languageKeys('es').sort()).toEqual(en);
    expect(languageKeys('he').sort()).toEqual(en);
    expect(tr('es', 'training_vs_last_week', { change: 12 })).toBe('+12 min frente a la semana pasada');
  });
});

describe('training page', () => {
  it('saves a session and shows it in the table and the weekly card', async () => {
    open('/#/training');
    const user = userEvent.setup();
    render(<App store={freshStore()} today="2026-10-19" />);
    expect(await screen.findAllByText(/No sessions yet/)).toHaveLength(2); // chart and table empty states
    await user.type(screen.getByLabelText('Minutes'), '32');
    await user.click(screen.getByRole('button', { name: /Save session/ }));
    const table = await screen.findByRole('table');
    expect(within(table).getByText('Walking')).toBeInTheDocument();
    expect(within(table).getByText('160')).toBeInTheDocument(); // 32 min × RPE 5
    expect(screen.getByText('32 min')).toBeInTheDocument();
  });

  it('rejects an invalid duration with an alert', async () => {
    open('/#/training');
    const user = userEvent.setup();
    render(<App store={freshStore()} today="2026-10-19" />);
    await user.type(await screen.findByLabelText('Minutes'), '900');
    await user.click(screen.getByRole('button', { name: /Save session/ }));
    expect(await screen.findByRole('alert')).toHaveTextContent('Duration must be between 1 and 600');
  });
});

describe('records, dashboard and coach', () => {
  it('saves a daily record, then the dashboard and coach read it', async () => {
    open('/#/records');
    const user = userEvent.setup();
    const store = freshStore();
    render(<App store={store} today="2026-10-19" />);
    await user.type(await screen.findByLabelText('Steps'), '11000');
    await user.type(screen.getByLabelText('Water (L)'), '2.4');
    await user.click(screen.getByLabelText('Happy'));
    await user.click(screen.getByRole('button', { name: /Save record/ }));
    expect(await screen.findByRole('status')).toHaveTextContent('2026-10-19');
    expect(await store.entries.get('2026-10-19')).toMatchObject({ steps: 11000, waterL: 2.4, mood: 'Happy' });

    await user.click(screen.getByRole('link', { name: tr('en', 'nav_dashboard') }));
    expect((await screen.findAllByText('11,000')).length).toBeGreaterThanOrEqual(2); // average and best day

    await user.click(screen.getByRole('link', { name: tr('en', 'nav_recommendations') }));
    expect(await screen.findByRole('heading', { level: 1 })).toHaveTextContent(tr('en', 'recommendation_title'));
    expect(screen.getByText(tr('en', 'data_confidence'))).toBeInTheDocument();
  });

  it('keeps profiles isolated and deletes only the removed profile', async () => {
    open('/#/records');
    const user = userEvent.setup();
    const store = freshStore();
    render(<App store={store} today="2026-10-19" />);
    await user.type(await screen.findByLabelText('Steps'), '7000');
    await user.type(screen.getByLabelText('Water (L)'), '2');
    await user.click(screen.getByRole('button', { name: /Save record/ }));
    await screen.findByRole('status');

    await user.click(screen.getByRole('link', { name: tr('en', 'nav_profiles') }));
    await user.type(await screen.findByLabelText(tr('en', 'display_name')), 'Mamá');
    await user.click(screen.getByRole('button', { name: tr('en', 'create') }));
    expect(await screen.findByRole('status')).toHaveTextContent('Mamá');
    await user.click(screen.getAllByRole('button', { name: tr('en', 'activate') })[0]);

    await user.click(screen.getByRole('link', { name: tr('en', 'nav_records') }));
    expect(await screen.findByText(tr('en', 'no_records'))).toBeInTheDocument();
    expect(await store.entries.count()).toBe(1); // the primary profile still has its record

    vi.spyOn(window, 'confirm').mockReturnValue(true);
    await user.click(screen.getByRole('link', { name: tr('en', 'nav_profiles') }));
    await user.click(await screen.findByRole('button', { name: `${tr('en', 'delete_profile')} Mamá` }));
    expect(await screen.findByRole('status')).toHaveTextContent(tr('en', 'profile_deleted', { name: 'Mamá' }));
    expect(await store.entries.count()).toBe(1);
  });

  it('drops an unsaved draft when the active profile changes', async () => {
    localStorage.setItem('novafit-web:profiles', JSON.stringify([{ id: 1, name: 'Kevin' }, { id: 2, name: 'Mamá' }]));
    open('/#/records');
    const user = userEvent.setup();
    const store = freshStore();
    render(<App store={store} today="2026-10-19" />);
    await user.type(await screen.findByLabelText('Steps'), '7000');
    await user.selectOptions(screen.getByLabelText(tr('en', 'user')), 'Mamá');
    expect(await screen.findByLabelText('Steps')).toHaveDisplayValue('');
    expect(await store.entries.count()).toBe(0);
  });

  it('skips to the content without leaving the current page', async () => {
    open('/#/training');
    const user = userEvent.setup();
    render(<App store={freshStore()} today="2026-10-19" />);
    await user.type(await screen.findByLabelText('Minutes'), '25');
    await user.click(screen.getByRole('link', { name: new RegExp(tr('en', 'nav_dashboard') + ' ↓') }));
    expect(window.location.hash).toBe('#/training');
    expect(document.activeElement).toBe(document.getElementById('main'));
    expect(screen.getByLabelText('Minutes')).toHaveDisplayValue('25');
  });

  it('exports a self-contained HTML report of the active profile', async () => {
    const blobs: Blob[] = [];
    const createObjectURL = vi.fn((blob: Blob) => { blobs.push(blob); return 'blob:report'; });
    Object.assign(URL, { createObjectURL, revokeObjectURL: vi.fn() });
    const click = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => undefined);
    open('/#/settings');
    const user = userEvent.setup();
    const store = freshStore();
    await store.entries.put({ date: '2026-10-19', steps: 9000, waterL: 2, calories: null, mood: null, note: null });
    render(<App store={store} today="2026-10-19" />);
    await user.click(await screen.findByRole('button', { name: tr('en', 'export_report') }));
    expect(click).toHaveBeenCalled();
    const html = await blobs[0].text();
    expect(html).toContain('<html lang="en" dir="ltr">');
    expect(html).toContain('NovaFit · Primary User');
    expect(html).toContain('9,000');
    click.mockRestore();
  });

  it('shows the trend lab with weekday rhythm and mood distribution', async () => {
    open('/#/trends');
    const user = userEvent.setup();
    const store = freshStore();
    await store.entries.bulkPut([
      { date: '2026-10-12', steps: 12000, waterL: 2.5, calories: null, mood: 'Happy', note: null },
      { date: '2026-10-19', steps: 10000, waterL: 2, calories: null, mood: 'Happy', note: null },
      { date: '2026-10-18', steps: 3000, waterL: 1, calories: null, mood: null, note: null },
    ]);
    render(<App store={store} today="2026-10-19" />);
    expect(await screen.findByRole('heading', { level: 1 })).toHaveTextContent(tr('en', 'chart_view_trend_lab'));
    const weekdays = await screen.findByRole('list', { name: tr('en', 'web_trend_weekday') });
    expect(within(weekdays).getByText('11,000')).toBeInTheDocument(); // two Mondays averaged
    const moods = screen.getByRole('list', { name: tr('en', 'web_trend_moods') });
    expect(within(moods).getAllByRole('listitem')).toHaveLength(2);
    expect(screen.getByText(tr('en', 'insight_best_weekday', { weekday: tr('en', 'weekday_monday') }), { exact: false })).toBeInTheDocument();
    await user.selectOptions(screen.getByLabelText(tr('en', 'web_trend_range')), '90');
    expect(screen.getByText(tr('en', 'web_trend_subtitle', { days: 90 }))).toBeInTheDocument();
  });

  it('switches the document to Hebrew right-to-left', async () => {
    open('/?lang=he#/training');
    render(<App store={freshStore()} today="2026-10-19" />);
    await waitFor(() => expect(document.documentElement.dir).toBe('rtl'));
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('יומן אימונים');
  });
});
