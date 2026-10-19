# NovaFit web (early shell)

The NovaFit wellness studio in the browser: local-first (IndexedDB), English / Spanish / Hebrew with true RTL, and the
same twelve themes as the desktop app. This first slice ships the **Training Log**; the other workspaces still live in
the Tkinter app and are shown as "in the desktop app for now".

```bash
cd web
npm install
npm run dev            # http://localhost:5173  (add ?demo=1 to an empty browser profile for a demo week)
npm test               # Vitest: domain parity with the Python tests + app journeys
npm run build          # TypeScript + Vite production build in dist/
python scripts/export_from_python.py   # regenerate src/generated/*.json from the Python package (--check in CI)
```

## Why web, and how it reuses the desktop app

| Desktop (Python) | Web | How it is reused |
| --- | --- | --- |
| `novafit/i18n.py` — 381 keys × EN/ES/HE | `src/i18n.ts` | Exported as `src/generated/i18n.json`; one catalogue, no drift |
| `novafit/themes.py` — 12 themes | `src/theme.ts` + `styles.css` | Exported as CSS custom properties `--nf-*` |
| `novafit/workouts.py` | `src/domain/workouts.ts` | Ported 1:1; `workouts.test.ts` mirrors `tests/test_workouts.py` |
| SQLite (`novafit.db`) | IndexedDB via Dexie | Same fields; JSON export/import is the bridge (next slice) |
| Tkinter panels | React components | Rewritten; layout uses CSS logical properties so Hebrew mirrors by itself |

Stack aligned with Nova Music Lab: React 19, TypeScript 6, Vite 8, Dexie 4, Vitest 5, lucide-react. No backend, no
account, no analytics: data never leaves the browser.

## Roadmap (estimate)

1. **JSON bridge** — import/export the desktop's `novafit-health-export-v2` file (daily records + `training_sessions`).
2. **Daily records + dashboard** — port `models.py`, `validation.py`, `analytics.py`; SVG charts.
3. **Coach + motivation** — port `recommendations.py` / `motivation.py` (pure functions, already tested in Python).
4. **PWA + GitHub Pages** — publish under `/NovaFit/app/` next to the existing showcase; Playwright journeys.

Each step is one focused session; the desktop app stays the complete reference until the web reaches parity.

## Screenshots (real browser captures, demo data)

<img src="docs/training-es-aurora.png" width="49%" alt="NovaFit web Training Log in Spanish, Aurora theme" /> <img src="docs/training-he-solar.png" width="49%" alt="NovaFit web Training Log in Hebrew right-to-left, Solar Paper light theme" />
