# NovaFit Ultimate GUI Guide 🖥️

## Purpose

The desktop interface is a Tkinter/ttk application designed for Windows and cross-platform Python environments. It prioritizes local data ownership, profile isolation, accessible labels and useful visual density.

## Global shell

The shell contains:

- active-profile selector;
- language selector;
- twelve-theme selector;
- animated health-intelligence hero;
- persistent sidebar with Pillow icons;
- hidden notebook used as a page router;
- status bar for recoverable feedback.

The default geometry is `1580x980`, with a minimum of `1180x760`. UI scale can be configured between `0.8` and `1.5`.

## Pages

### Command Center

The chart view can switch between Command Center, Trend Lab, Consistency Map and Training Atlas. Calendar ranges cover 7–365 days. PNG export uses the same profile-scoped records shown on screen.

### Motivation Center

Shows deterministic motivation, purpose, streaks, milestone progress, achievements and a visual pacing reset. Reduced motion stops continuous animation.

### Sport & Data Coach

Shows data confidence, recommendation cards, priority, action, reason, weekly rhythm and scope disclaimer. Export produces a plain-text plan.

### Add Daily Record

Validates date, steps, water, optional calories, mood and private note. Existing dates update only inside the active profile.

### Record Library

Supports date-range filtering, full history, edit, delete and active-profile isolation.

### User Profiles

Creates and updates profiles with avatar, language, theme, goals, activity level and sport focus. The primary profile cannot be deleted.

### Tools & Settings

Contains JSON/CSV import/export, HTML report export, demo data, weather, goals, theme, language, UI scale and reduced-motion settings.

## Visual system

- `ttk.Style` uses theme palette tokens.
- Pillow-generated icons avoid unreliable platform emoji.
- The animated hero uses only Tk Canvas primitives.
- Charts use Matplotlib and inherit the active theme.
- All decorative icons are paired with readable text.

## Manual QA checklist

1. Resize from minimum to full screen.
2. Switch through all twelve themes.
3. Switch EN → ES → HE and verify RTL sidebar placement.
4. Create a second profile and add the same date to both profiles.
5. Verify charts and recommendations change with the active profile.
6. Enable reduced motion and confirm Canvas animation stops.
7. Export PNG and HTML.
8. Test keyboard shortcuts: `Ctrl+R`, `Ctrl+T`, `Ctrl+M`, `Ctrl+K`, `Ctrl+E`, `Ctrl+Q`.
