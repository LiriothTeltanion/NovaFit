# Windows Environment Repair and Verification 🪟⚙️

## Why this exists

A Windows checker can fail even when the application source is correct if it launches the global interpreter without installing project dependencies. The two most visible symptoms are:

```text
ModuleNotFoundError: No module named 'matplotlib'
ZoneInfoNotFoundError: No time zone found with key Asia/Jerusalem
```

The first means the active Python environment lacks the chart dependency. The second means Windows/Python cannot find the IANA timezone database and the `tzdata` package is absent.

## Recommended entry point

From the extracted NovaFit folder, double-click:

```text
REPAIR_AND_VERIFY.bat
```

For the integrated NovaFit + GitHub Profile package, use:

```text
CHECK_EVERYTHING.bat
```

## Self-healing sequence

1. Detect an installed Python 3.10–3.14 interpreter.
2. Prefer an existing compatible `.venv` when healthy.
3. Create or repair `NovaFit/.venv`.
4. Upgrade `pip`, `setuptools` and `wheel`.
5. Install dependencies with `--prefer-binary`.
6. Install NovaFit in editable mode.
7. Verify imports for Tkinter, Matplotlib, Pillow, Requests, Faker and `tzdata`.
8. Verify `ZoneInfo("Asia/Jerusalem")`.
9. Run 47 unit/integration tests.
10. Run CLI, SQLite, PNG and HTML smoke checks.
11. In the integrated package, rebuild and validate the GitHub profile and audit distribution safety.

## Why `.venv` matters

The original failure path used a global interpreter such as:

```text
C:\Python314\python.exe
```

A global Python can exist while Matplotlib is installed somewhere else—or nowhere. The new BAT files consistently call:

```text
NovaFit\.venv\Scripts\python.exe
```

so setup, tests and launch use the same dependency environment.

## Python 3.14 fallback behavior

The launcher tests available Python installations in a curated order. If dependency installation fails for one interpreter, it can rebuild the generated `.venv` using another installed supported version. Python 3.13 remains a strong fallback for environments where a binary wheel has not yet been published for a newer interpreter.

## Timezone resilience

`tzdata` is installed by default. The application also calls a safe helper that falls back to the operating-system local timezone and then UTC if the IANA zone is unavailable. This keeps JSON export usable while preserving `Asia/Jerusalem` whenever the correct database is present.

## Manual recovery

Open Command Prompt in the NovaFit directory:

```bat
rmdir /s /q .venv
py -3.13 scripts\bootstrap_environment.py --verbose
.venv\Scripts\python.exe scripts\verify.py
```

Using Python 3.14 instead:

```bat
py -3.14 scripts\bootstrap_environment.py --verbose
```

## Offline limitation

First-time dependency repair needs access to a Python package index unless compatible wheels are already cached. After setup, NovaFit's core tracking, SQLite, Motivation Center, charts and reports work locally; only optional weather requires a network request.
