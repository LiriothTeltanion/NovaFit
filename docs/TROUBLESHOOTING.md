# NovaFit Troubleshooting 🧰

## Setup and environment

### Python is not recognized

Run:

```bat
py -3 --version
python --version
```

If both fail, reinstall Python with PATH enabled, then open a new terminal.

### Virtual environment is incomplete

Delete `.venv` and rerun:

```text
setup_windows.bat
```

Do not copy a virtual environment between computers.

### Dependency installation fails

Check internet access and the system clock. Then run:

```bat
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## GUI

### No Tkinter module

Windows official Python normally includes it. Linux may need `python3-tk` from the system package manager.

### The window is too large

NovaFit has a minimum workspace for the analytics studio. Maximize the window or use the CLI to export charts on smaller displays.

### A chart looks cropped after resizing

Select another analytics view or press **Refresh charts**. The panel recalculates its physical Matplotlib size from the current Tk allocation.

### Animation is distracting

Enable **Reduce decorative motion** in Tools & Settings. Charts remain static in both modes.

## Data

### Database locked

Close duplicate NovaFit processes and external SQLite tools. Wait briefly for a backup operation. Retry.

### Existing historical database

Make a copy and run:

```bash
python scripts/migrate_legacy_db.py data/novafit.db
```

### Duplicate date

NovaFit intentionally stores one row per date. Saving the same date updates the editable fields.

### Import changes existing rows

Use:

```bash
--import-strategy skip
```

when existing dates should remain untouched.

### Import reports invalid rows

Open the source and confirm:

- ISO dates;
- non-negative numeric values;
- required date/steps/water fields;
- valid JSON root or CSV header names.

## Analytics

### No chart output

Confirm Matplotlib:

```bash
python -c "import matplotlib; print(matplotlib.__version__)"
```

### Headless server

```bash
MPLBACKEND=Agg python -m novafit --chart output.png
```

### Score seems unexpected

Read `docs/ANALYTICS.md`. The consistency score includes recording coverage and caps goal progress. It is not a total-performance score.

### Missing date displays as zero

Some line charts place the missing calendar position at zero to expose the gap. The calendar matrix retains a distinct empty cell. No missing measurement is presented as verified data.

## Weather

### Offline or timeout

Continue using NovaFit normally. Weather is optional. Retry when connectivity returns.

### Unsupported city

Use one of the configured aliases or add a reviewed coordinate pair in `config.py` with tests.

## Reports

### HTML opens without styling

The report is self-contained. If it appears as source text, open it with a web browser rather than a text editor.

### Private note visible

Reports intentionally include recent records. Create a sanitized copy or remove notes before sharing externally.

## Verification

### A test fails

Run the exact failing test from the repository root, for example:

```bash
python -m unittest tests.test_charts -v
```

Use `--debug` for CLI diagnostics, but do not paste private paths or data into public issue reports.
