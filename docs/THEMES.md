# NovaFit 4.2 Theme System 🎨

## Purpose

NovaFit uses one central theme registry for Tkinter widgets, animated canvas components, Matplotlib charts and offline HTML reports. The registry prevents color drift between the desktop interface and exported evidence.

## Included themes

| ID | Display name | Mode | Primary use |
|---|---|---|---|
| `midnight` | Midnight Neon | Dark | Default cyber command center |
| `aurora` | Aurora Borealis | Dark | Teal/violet focus and the 3.1 showcase |
| `desert` | Negev Sunrise | Dark | Warm Beersheba-inspired identity |
| `ocean` | Ocean Depth | Dark | Calm blue analytics |
| `forest` | Forest Focus | Dark | Habit consistency and green progress cues |
| `rose` | Rose Quartz | Dark | Creative magenta portfolio presentation |
| `cloud` | Cloud Day | Light | Bright accessible workspace |
| `solar` | Solar Paper | Light | Warm reading and lower-glare reports |
| `contrast` | High Contrast | Dark | Strong separation for accessibility review |

## Shared contract

Each theme defines:

- application background and panel surfaces;
- primary and secondary text;
- accent, success, warning and danger signals;
- borders and chart grids;
- extra blue and pink chart channels;
- light/dark classification.

The stable ID is stored in `data/config.json`. Display labels can change without invalidating saved settings.

## Keyboard and settings

- Press `Ctrl+T` to cycle through the curated order.
- Open **Tools & Settings** to select a theme by name.
- The selected theme persists locally.
- Legacy values `dark` and `light` migrate to `midnight` and `cloud`.

## Accessibility

Color is never intended to be the only signal. Labels, percentages, headings, icons and text descriptions accompany goal and warning states. The High Contrast theme is included for manual review, but it does not replace testing with Windows high-contrast settings and assistive technology.

Animation respects the `reduce_motion` setting. When enabled, canvas systems render a stable frame and GIF/SVG documentation includes static alternatives where practical.

## Adding a theme

1. Add one `ThemeDefinition` in `novafit/themes.py`.
2. Provide all required UI and chart keys.
3. Run `python -m unittest tests.test_themes -v`.
4. Generate the gallery with `python scripts/generate_showcase.py`.
5. Inspect text contrast, chart readability and both GUI workspaces.
6. Update this file and the README theme table.

Themes should improve comprehension rather than merely adding decoration.
