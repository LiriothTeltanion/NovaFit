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

  it('switches the document to Hebrew right-to-left', async () => {
    open('/?lang=he#/training');
    render(<App store={freshStore()} today="2026-10-19" />);
    await waitFor(() => expect(document.documentElement.dir).toBe('rtl'));
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('יומן אימונים');
  });
});
