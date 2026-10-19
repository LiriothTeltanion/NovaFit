// Design tokens: the 12 desktop themes become CSS custom properties, so both apps share one palette.
import themes from './generated/themes.json';

export type ThemeId = keyof typeof themes;
export const THEMES = themes as Record<string, { label: string; mode: 'dark' | 'light'; ui: Record<string, string> }>;
export const DEFAULT_THEME: ThemeId = 'aurora';

/** Apply one theme to :root as --nf-<token> variables (panel_alt → --nf-panel-alt). */
export function applyTheme(themeId: string, root: HTMLElement = document.documentElement): void {
  const theme = THEMES[themeId] ?? THEMES[DEFAULT_THEME];
  for (const [token, value] of Object.entries(theme.ui)) root.style.setProperty(`--nf-${token.replace(/_/g, '-')}`, value);
  root.dataset.theme = themeId in THEMES ? themeId : DEFAULT_THEME;
  root.style.colorScheme = theme.mode;
}
