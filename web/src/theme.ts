// Design tokens: the 12 desktop themes become CSS custom properties, so both apps share one palette.
import themes from './generated/themes.json';

export type ThemeId = keyof typeof themes;
export const THEMES = themes as Record<string, { label: string; mode: 'dark' | 'light'; ui: Record<string, string> }>;
export const DEFAULT_THEME: ThemeId = 'aurora';

/** Apply one theme to :root as --nf-<token> variables (panel_alt → --nf-panel-alt). */
export function applyTheme(themeId: string, root: HTMLElement = document.documentElement): void {
  const theme = THEMES[themeId] ?? THEMES[DEFAULT_THEME];
  for (const [token, value] of Object.entries(theme.ui)) root.style.setProperty(`--nf-${token.replace(/_/g, '-')}`, value);
  // Text that sits on panels needs WCAG AA contrast. Bright accents read well on dark themes, but on the light
  // themes (Cloud, Solar Paper) they are darkened toward the text colour; muted copy is strengthened the same way.
  const light = theme.mode === 'light';
  root.style.setProperty('--nf-accent-text', light ? `color-mix(in srgb, ${theme.ui.accent} 52%, ${theme.ui.text})` : theme.ui.accent);
  root.style.setProperty('--nf-muted-text', light ? `color-mix(in srgb, ${theme.ui.muted} 55%, ${theme.ui.text})` : theme.ui.muted);
  root.dataset.theme = themeId in THEMES ? themeId : DEFAULT_THEME;
  root.style.colorScheme = theme.mode;
}
