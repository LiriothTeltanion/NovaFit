# NovaFit Desktop GUI Guide 🖥️

## Launch

Windows:

```text
run_novafit.bat
```

Cross-platform:

```bash
python -m novafit
```

## Main layout

The window contains:

- a product header;
- a reduced-motion-aware pulse visualization;
- a persistent navigation rail;
- a hidden internal ttk notebook;
- the active workspace;
- a status line.

The notebook tabs are hidden intentionally. The navigation rail provides clearer product structure while ttk.Notebook still manages page switching reliably.

## Analytics Studio

Controls:

- view selector;
- range selector;
- PNG export;
- refresh button.

Metric cards:

- consistency score;
- tracked days;
- coverage;
- total steps;
- average steps;
- average hydration;
- balanced-goal days;
- current/longest streak;
- best day;
- recent change.

The horizontal split contains:

- embedded Matplotlib canvas and toolbar;
- textual signal summary;
- goal-completion bars.

Select a different view or range and the figure is rebuilt from current local records.

## Add daily record

Required fields:

- date;
- steps;
- water.

Optional fields:

- calories;
- mood;
- note.

Saving an existing date updates the same day. It does not create a second record for that date.

### Validation behavior

User input errors appear in an actionable dialog. The GUI does not show a stack trace unless a developer uses CLI debug mode.

Examples:

- invalid date → use `YYYY-MM-DD`;
- negative step count → enter zero or a positive value;
- water above the safe product bound → verify the units;
- note too long → shorten the private note.

## Record Library

Use the start and end date fields to filter records inclusively.

Actions:

- `Filter range`;
- `Show all`;
- double-click a row to edit;
- select and delete with confirmation.

The library is newest-first by default.

## Tools & Settings

### Portability

- Export JSON
- Import JSON
- Export CSV
- Import CSV
- Export visual HTML report

### Demonstration and data

- Add seven starter dates
- Generate thirty demo dates
- Export selected analytics PNG
- Clear all records

### Goals and visuals

- step goal;
- hydration goal;
- calorie reference;
- default chart days;
- default view;
- reduced decorative motion.

### Weather

Select a built-in Israeli city alias and request current weather. No health record is included in the request.

## Themes

The theme button switches between dark and light.

A theme change updates:

- ttk styles;
- navigation colors;
- the decorative pulse;
- embedded analytics.

The preference is stored in `data/config.json`.

## Keyboard workflow

| Shortcut | Action |
|---|---|
| `Ctrl+S` | Save form |
| `Ctrl+R` | Refresh data and charts |
| `Ctrl+E` | Export JSON |
| `Ctrl+T` | Toggle theme |
| `Ctrl+Q` | Quit |
| `F1` | About dialog |

## Status messages

Normal operations update the status bar for twelve seconds, then return to the local-first reminder.

Examples:

```text
Saved 2026-07-15 ✅
Analytics dashboard saved to data/overview.png ✅
Imported 42 record(s); skipped 2; invalid 1.
```

## Reduced motion

When enabled, the decorative header animation stops. Core interface behavior and Matplotlib charts remain available.

## Window sizing

Recommended:

```text
1440 × 920 or larger
```

Minimum:

```text
1120 × 760
```

At smaller dimensions, export PNG for the clearest dashboard view.

## Safe demo workflow

1. Use a separate database through the CLI.
2. Insert deterministic or Faker data.
3. Open the GUI against that database.
4. Capture screenshots.
5. Delete the demo data directory afterward.

Never capture a public portfolio screenshot from a real personal database unless every visible field has been reviewed.
