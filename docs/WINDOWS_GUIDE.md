# NovaFit 4.2 Windows Guide 🪟⚙️

## Recommended standalone release

For the simplest installation, download
`NovaFit-vX.Y.Z-Windows-x64-Standalone.zip` from GitHub Releases, extract the
entire folder, and double-click `START_NOVAFIT.bat`. This official **onedir**
package includes Python, Tkinter, Matplotlib, Pillow, timezone data, and every
runtime dependency. Python does not need to be installed.

Keep the `_internal` directory beside `NovaFit.exe`; it is part of the program.
NovaFit stores private runtime data separately under
`%LOCALAPPDATA%\NovaFit`, so replacing an extracted application folder during
an upgrade does not replace the database or settings. `OPEN_DATA_FOLDER.bat`
opens that durable location. Every release also includes:

- `NovaFit-CLI.exe` for Windows Terminal and automation;
- `STANDALONE_MANIFEST.json` with a SHA-256 digest for every payload file;
- `BUILD_INFO.json` with version and source-commit provenance;
- a `.zip.sha256` sidecar plus the release-wide `SHA256SUMS.txt`.

The source-checkout workflow below remains supported for development.

## Supported route

NovaFit targets 64-bit Python **3.10–3.14** on current Windows 10 or Windows 11. Python 3.13 is the recommended fallback when a newer interpreter does not yet have every binary scientific package available.

## Installation and repair

1. Install Python from the official installer.
2. Enable **Add python.exe to PATH** and the **Python Launcher for Windows**.
3. Keep or extract NovaFit in a writable location, including your existing OneDrive project folder.
4. Double-click `VERIFY_ALL.bat` once for the complete repair and quality gate.
5. Wait for the dependency preflight, tests and isolated smoke summary.
6. Double-click `run_novafit.bat`.

The same recovery path fixes these common messages:

```text
ModuleNotFoundError: No module named 'matplotlib'
ZoneInfoNotFoundError: No time zone found with key Asia/Jerusalem
```

## What setup creates

```text
NovaFit\.venv\
```

All Python packages remain isolated inside that environment. Tests and the application use `.venv\Scripts\python.exe`, not whichever global interpreter happens to be first on PATH.

## Self-healing sequence

`bootstrap_windows.bat`:

1. checks whether the existing `.venv` already imports all required packages;
2. rebuilds an incomplete generated environment;
3. tries installed Python versions in a curated order;
4. installs wheel distributions with `--prefer-binary --only-binary=:all:`;
5. installs NovaFit in editable mode;
6. verifies Tkinter, Matplotlib, Pillow, Requests, Faker, `tzdata` and `Asia/Jerusalem`.

If Python 3.14 cannot obtain a binary wheel on a particular machine, the launcher can try an installed Python 3.13, 3.12, 3.11 or 3.10 interpreter automatically.

## Launcher reference

### REPAIR_AND_VERIFY.bat

Runtime-focused compatibility entry point. Calls environment repair, then the core test/smoke verifier.

### VERIFY_ALL.bat

Recommended complete checker. Adds package safety, Ruff and Pyright gates while
preserving local databases, exports and complete backups.

### bootstrap_windows.bat

Repairs dependencies and timezone support without running the full suite.

### setup_windows.bat

Runs bootstrap plus verification and leaves the application ready to launch.

### run_novafit.bat

- changes to the script directory;
- validates the local environment;
- repairs it automatically when required;
- opens the Tkinter application.

### run_cli.bat

Opens the interactive menu using the same local environment and keeps the console visible after exit.

### verify_windows.bat

Repairs/preflights the environment, then runs the same Python verifier used by CI.

### export_backup.bat

Creates a verified all-profile ZIP, with manifest and SHA-256 checksums, under `data\backups`.

### export_report.bat

Creates the offline HTML report with the current local database and selected theme.

### export_analytics_gallery.bat

Creates all four analytics views. The Python showcase generator can additionally build all twelve theme variants.

### open_data_folder.bat

Opens the configured default data directory in Explorer.

### BUILD_WINDOWS_STANDALONE.bat

Developer/release one-click builder. It creates an isolated Python 3.13 build
environment, runs the complete quality gate, regenerates the multi-resolution
Windows icon, creates both frozen executables, uses disposable data for the
frozen CLI smoke test, audits the exact onedir payload, and writes a versioned
ZIP with its SHA-256 sidecar under `dist`.

## Manual recovery

From Command Prompt in the NovaFit folder:

```bat
rmdir /s /q .venv
py -3.13 scripts\bootstrap_environment.py --verbose
.venv\Scripts\python.exe scripts\verify.py
```

Use `py -3.14` instead when that is your only installation.

## Windows Terminal recommendation

Windows Terminal renders UTF-8 and emoji more consistently than the legacy console. Functionality does not depend on emoji.

## Paths containing spaces

Launchers quote `%~dp0` and `.venv` paths. A short path is still recommended because it makes troubleshooting and screenshots easier.

The bootstrapper retries generated-environment cleanup and can move a stale
`.venv` out of the synced folder before rebuilding, which avoids transient
OneDrive directory-not-empty failures without moving the NovaFit repository.

## Portable data copy

Close NovaFit before manually copying `data\novafit.db`. WAL may use temporary sidecar files while the application is open.

## Uninstall

NovaFit has no system-wide service.

1. Export records if desired.
2. Delete the project folder.
3. Delete any separately copied reports/backups.

The virtual environment is contained inside the project. For the standalone
edition, delete the extracted application folder. Private data remains under
`%LOCALAPPDATA%\NovaFit` until the user explicitly removes or backs it up.
