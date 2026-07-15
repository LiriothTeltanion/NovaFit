# NovaFit Design System 🎨

## Product tone

NovaFit uses a technical wellness-cockpit aesthetic without presenting itself as medical software.

Keywords:

```text
local-first · calm · clear · neon accents · evidence-based · private
```

## Dark palette

| Token | Value | Use |
|---|---|---|
| Background | `#07111f` | Main desktop surface |
| Panel | `#0d1b2a` | Navigation and chart shell |
| Panel alt | `#13263a` | Cards and selected navigation |
| Text | `#e6f4ff` | Primary copy |
| Muted | `#91a8bd` | Secondary copy |
| Cyan | `#22d3ee` | Primary signal |
| Purple | `#8b5cf6` | Rolling/identity signal |
| Green | `#34d399` | Goal success |
| Amber | `#fbbf24` | Goal/reference |
| Pink | `#fb7185` | Negative/mood accent |

## Light palette

The light system preserves semantic relationships while increasing surface luminance.

## Typography

Tkinter uses Segoe UI where available and platform fallback otherwise.

Hierarchy:

- product title: 24 bold;
- metric value: 15 bold;
- body: 10;
- card title: 8 bold uppercase;
- chart title: approximately 10–19 depending on level.

## Spacing

- outer page padding: 18–22;
- cards: 12–18;
- navigation item: 14 × 11;
- related controls: 4–8;
- major sections: 12–18.

## Analytics colors

- movement: cyan;
- rolling average: purple;
- success: green;
- goal reference: amber;
- below-goal tracked point: coral/pink;
- hydration: blue/cyan/green;
- missing calendar cell: panel surface.

## Visual principles

1. Text remains available beside visual signals.
2. Color communicates status but is not the only indicator.
3. Missing records are not treated as zero performance.
4. Personal data screenshots use demo records.
5. Animation is decorative and optional.
6. Charts prioritize a question, not chart variety.

## Asset rules

Repository SVGs:

- contain no external JavaScript;
- use system fonts;
- include `title` and `desc`;
- respect reduced motion;
- avoid remote resources.

## Screenshot rules

- use deterministic demonstration data;
- remove local filesystem paths where possible;
- do not include notification overlays;
- identify conceptual mockups separately from real captures;
- regenerate after meaningful UI changes.
