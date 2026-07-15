# Changelog

All notable NovaFit changes are documented here.

## 4.1.0 — 2026-07-16 · Living Wellness Studio

### Added

- Complete English, Spanish and Hebrew copy across every primary workspace, including dynamic states, confirmations, errors, exports and recommendations.
- RTL composition for Hebrew panels, forms, cards, tables, navigation and visual scenes.
- Persistent Canvas animation with visibility lifecycle, reduced-motion support and a 15–20 FPS budget.
- Antialiased app/navigation icons with default, active and muted states.
- Responsive compact and wide chart layouts with clearer ticks, legends and freshness labels.
- Verified all-profile ZIP backups containing SQLite, configuration and a SHA-256 manifest.
- One-click `run_novafit.bat` self-repair and a complete `VERIFY_ALL.bat` quality gate.
- Generated `portfolio/project.json`, `assets/manifest.json` and `docs/PROJECT_FACTS.md` for repository/profile synchronization.
- Windows and Ubuntu GitHub Actions coverage across supported Python versions, plus Ruff and Pyright gates.

### Changed

- Dashboard recency, recent windows and streaks now use the real current date instead of treating the latest historical row as today.
- Imports are bounded, validated and committed atomically; spreadsheet exports neutralize formula-like values.
- Numeric settings reject booleans, fractions where integers are required and non-finite values.
- GUI imports, exports, reports, weather and demo generation run away from the Tk main loop.
- Profile preferences are persisted consistently by both GUI and CLI.
- Runtime databases, exports, local configuration and old package backups are no longer tracked by Git.
- Version and documentation facts now come from package metadata instead of hand-written test badges.

### Verified

- Complete local verification through `VERIFY_ALL.bat`.
- Real Tkinter lifecycle and Hebrew panel smoke tests.
- Compact and wide renders for all four analytical workspaces.
- Complete backup creation, hash verification and database integrity restoration tests.
- Strict release-distribution audit without private runtime data.

## 4.0.0 — 2026-07-15 · Ultimate Wellness Intelligence

### Added

- Multi-user profiles with isolated records and per-profile goals.
- English, Spanish and Hebrew selector with Hebrew RTL shell behavior.
- Royal Sapphire, Cyber Lime and Sunset Arcade, bringing the theme total to twelve.
- Theme-aware Pillow icon system.
- Sport & Data Coach with explainable confidence and safety boundary.
- Training Atlas as the fourth analytics workspace.
- Profile-aware CLI flags and profile lifecycle commands.
- Real GUI captures for analytics, recommendations, profiles, Spanish and Hebrew.
- Workspace-safe audit plus strict clean-distribution mode.
- Release-staging policy that excludes databases, logs and local config.
- Distribution regression tests.

### Changed

- SQLite schema upgraded to v4 with `profiles` and `user_id`.
- Legacy single-user databases migrate to the protected primary profile.
- Hero Canvas now localizes English, Spanish and Hebrew copy.
- Windows and repository verification exercise recommendations, profiles and Training Atlas.
- Documentation rewritten around the actual Ultimate 4.0 product.

### Verified

- 74 automated tests passed.
- Python compile and isolated smoke workflow passed.
- Real Tkinter lifecycle passed under Xvfb.
- PNG, GIF, SVG and HTML showcase generation completed.

## 3.1.0 — 2026-07-15 · Aurora Motivation

- Added twelve themes, Motivation Center and self-healing Windows environment repair.
- Added timezone fallback, Matplotlib/Pillow/tzdata preflight and 74 tests.

## 3.0.0 — 2026-07-15 · Definitive Analytics

- Added Command Center, Trend Lab, Consistency Map and expanded documentation.

## 2.0.0 — 2026-07-15 · Restored Product

- Restored the modular Python application, CLI, GUI, SQLite, import/export and weather integration.
