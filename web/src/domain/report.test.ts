import { buildHtmlReport } from './report';
import { DEFAULT_GOALS } from './analytics';
import { buildEntry } from './entries';

describe('offline HTML report', () => {
  it('is self-contained, localized and escapes user text', () => {
    const entries = [buildEntry({ date: '2026-10-19', steps: 12000, waterL: 2.5, note: '<script>alert(1)</script>' })];
    const html = buildHtmlReport({ entries, sessions: [], goals: DEFAULT_GOALS, language: 'he', today: '2026-10-20', profileName: 'Mamá & <Kevin>' });
    expect(html).toContain('<html lang="he" dir="rtl">');
    expect(html).toContain("default-src 'none'");
    expect(html).not.toContain('<script>');
    expect(html).toContain('&lt;script&gt;alert(1)&lt;/script&gt;');
    expect(html).toContain('Mamá &amp; &lt;Kevin&gt;');
    expect(html).not.toMatch(/https?:\/\//);
  });
});
