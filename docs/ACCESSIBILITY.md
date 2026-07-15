# Accessibility Notes ♿

## Goals

NovaFit aims to make the same core workflows available through GUI and CLI while respecting Tkinter’s platform limitations.

## Implemented

- native ttk controls;
- visible labels;
- logical navigation rail;
- keyboard shortcuts;
- dark and light themes;
- textual metric cards;
- status messages;
- actionable dialogs;
- reduced decorative motion;
- non-color chart labels and values;
- CLI alternative;
- SVG reduced-motion media queries.

## Charts

Every major chart includes:

- title;
- axis labels where meaningful;
- legends;
- textual values;
- goal reference description;
- missing-data distinction;
- non-medical disclaimer.

Exported PNGs should be accompanied by the HTML report or a textual dashboard when used in an accessibility-sensitive context.

## Motion

The Tkinter pulse can be disabled in settings.

Animated SVGs use:

```css
@media (prefers-reduced-motion: reduce)
```

The profile README also supplies static picture sources for major banner/globe assets.

## Keyboard

Current shortcuts are documented in the GUI guide. Native Tab traversal is preserved.

## Known limits

- screen-reader behavior varies across Tk versions and operating systems;
- the Matplotlib toolbar has platform-specific accessibility limits;
- custom canvas decorations do not expose semantic nodes;
- high-contrast mode needs release-device validation;
- table sorting is not yet keyboard-configurable.

## Release review

Before release on Windows:

1. operate the form without a mouse;
2. inspect focus visibility;
3. test dark and light themes;
4. enable reduced motion;
5. test at 125% and 150% display scaling;
6. open the HTML report with browser zoom;
7. verify textual CLI dashboard output.
