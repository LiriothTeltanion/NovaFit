# NovaFit CLI Reference ⌨️

## General form

```bash
python -m novafit.cli [global options] [one action] [action options]
```

Only one primary action is accepted per invocation.

## Global options

```text
-h, --help
--version
--log-level DEBUG|INFO|WARNING|ERROR|CRITICAL
--debug
--db PATH
```

## Interactive menu

```bash
python -m novafit.cli --menu
```

Running without an action also opens the menu.

## Add or update

```bash
python -m novafit.cli \
  --add 2026-07-15 \
  --steps 10420 \
  --water 2.4 \
  --calories 2050 \
  --mood Focused \
  --note "Evening walk"
```

Required with `--add`:

- `--steps`
- `--water`

Optional:

- `--calories`
- `--mood`
- `--note`

## List

```bash
python -m novafit.cli --list
python -m novafit.cli --list 50
```

## Dashboard

```bash
python -m novafit.cli --dashboard
```

The text dashboard remains useful over SSH, inside CI smoke checks, or where Tkinter is unavailable.

## Delete

```bash
python -m novafit.cli --delete 2026-07-15
```

The script reports whether a matching row existed.

## Sample and demo records

```bash
python -m novafit.cli --sample
python -m novafit.cli --seed 30
```

`--sample` uses a fixed seven-day example. `--seed` uses Faker when installed and a deterministic fallback otherwise.

## JSON

```bash
python -m novafit.cli --export-json data/backup.json
python -m novafit.cli --import-json data/backup.json --import-strategy replace
python -m novafit.cli --import-json data/backup.json --import-strategy skip
```

## CSV

```bash
python -m novafit.cli --export-csv data/backup.csv
python -m novafit.cli --import-csv data/backup.csv --import-strategy replace
```

## Weather

```bash
python -m novafit.cli --weather "Be'er Sheva"
```

The city is normalized case-insensitively.

## Chart export

```bash
python -m novafit.cli \
  --chart data/overview.png \
  --chart-view overview \
  --chart-days 90 \
  --chart-theme dark
```

View values:

```text
overview
trends
consistency
command_center
trend_lab
consistency_map
```

## HTML report

```bash
python -m novafit.cli \
  --report-html data/report.html \
  --chart-view consistency \
  --chart-days 180 \
  --chart-theme light
```

## Settings

```bash
python -m novafit.cli --settings
```

Only safe preferences are displayed. Health records and notes are not printed by this action.

## Separate database examples

```bash
python -m novafit.cli --db data/interview-demo.db --sample
python -m novafit.cli --db data/interview-demo.db --dashboard
python -m novafit.cli --db data/interview-demo.db --chart data/interview.png
```

## Logging

Normal:

```bash
python -m novafit.cli --log-level INFO --dashboard
```

Developer diagnostics:

```bash
python -m novafit.cli --debug --log-level DEBUG --import-json broken.json
```

End users receive short actionable errors by default. Debug mode is intended for development.

## Exit codes

- `0` — requested operation completed;
- non-zero — validation, file, database, dependency, or network failure.

## Automation pattern

```bash
set -e
python -m novafit.cli --db data/automation.db --sample
python -m novafit.cli --db data/automation.db --dashboard
python -m novafit.cli --db data/automation.db --export-json data/automation.json
python -m novafit.cli --db data/automation.db --chart data/automation.png --chart-view overview
```

## Quoting notes

Use quotes for values containing spaces:

```bash
--mood "Very focused"
--note "Morning walk near home"
--weather "Tel Aviv"
```

On Windows batch files, use `%~dp0`-based paths so launchers work from any current directory.
