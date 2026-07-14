<div align="center">

# 🏃 NovaFit

### Local-first health tracking through a Python CLI and Tkinter desktop interface

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Quality](https://img.shields.io/github/actions/workflow/status/LiriothTeltanion/NovaFit/quality.yml?style=for-the-badge&label=smoke%20tests)](https://github.com/LiriothTeltanion/NovaFit/actions)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)

**Steps · water · calories · mood · trends · import/export · weather**

</div>

---

## ✨ What NovaFit is

NovaFit is a small offline-friendly health tracker created for a Developers
Institute hackathon. It stores daily metrics in a local SQLite database and
offers two interfaces over the same data:

- 🖥️ an interactive command-line application;
- 🪟 a Tkinter desktop GUI;
- 📊 dashboards and goal progress;
- 📁 JSON and CSV import/export;
- 🎲 sample and Faker-generated data;
- 🌦️ optional current weather from Open-Meteo.

The health database and personal exports stay inside the local `data/` folder
and are ignored by Git.

> **Important:** NovaFit is a local Python application, not a browser app.
> GitHub Pages cannot execute Python or Tkinter. The GitHub repository is the
> source and documentation; a public live demo would require a separate web
> frontend.

## 🚀 Windows quick start

### CLI

Double-click:

```text
run_cli.bat
```

### GUI

Double-click:

```text
run_gui.bat
```

On first launch, the scripts call `setup.bat`, create `.venv`, install the
dependencies and then start NovaFit.

## 💻 Manual setup

```powershell
git clone https://github.com/LiriothTeltanion/NovaFit.git
cd NovaFit

py -3 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt

# CLI
.venv\Scripts\python -m novafit.cli

# GUI
.venv\Scripts\python -m novafit.gui
```

Python 3.10 or newer is recommended.

## 🧪 Validate the repository

```powershell
powershell -ExecutionPolicy Bypass -File .\check_novafit.ps1 -InstallDependencies
```

The diagnostic script verifies required files, compiles the package, runs smoke
tests and explains the GitHub Pages limitation.

Equivalent manual checks:

```powershell
.venv\Scripts\python -m compileall -q novafit
.venv\Scripts\python -m unittest discover -s tests -v
```

GitHub Actions runs the same smoke checks on pushes and pull requests.

## 🧭 CLI capabilities

```text
📝 Add or update daily entries
⚡ Quick entry for today
📋 List recent entries
🗑️ Delete an entry
📈 View dashboard summaries
🔍 Search a date range
🌦️ Fetch weather for supported Israeli cities
📤 Export JSON or CSV
📥 Import JSON or CSV
🎲 Generate demonstration data
🌟 Load sample data
```

## 🗂️ Project structure

```text
NovaFit/
├─ novafit/
│  ├─ __init__.py
│  ├─ cli.py
│  ├─ gui.py
│  ├─ config.py
│  ├─ database.py
│  ├─ export.py
│  ├─ utils.py
│  └─ weather.py
├─ tests/
│  └─ test_smoke.py
├─ .github/workflows/
│  └─ quality.yml
├─ setup.bat
├─ run_cli.bat
├─ run_gui.bat
├─ check_novafit.ps1
├─ requirements.txt
└─ README.md
```

## 💾 Local data

NovaFit creates files under `data/`, including:

- `novafit.db` — SQLite health log;
- `config.json` — local preferences;
- JSON/CSV exports selected by the user.

These files are intentionally excluded by `.gitignore`. Commit only fictional
sample data that is explicitly safe to share.

## 🔒 Network and privacy notes

- Health logs are stored locally.
- Weather lookup is optional.
- Weather requests use normal HTTPS certificate verification.
- NovaFit does not require an API key for Open-Meteo.
- Do not commit real health exports or the local SQLite database.

## 🛠️ Current status

This repository was restored after a commit accidentally removed the complete
`novafit/` package while leaving launchers and documentation behind. The
restoration reintroduces the application modules, adds repeatable diagnostics
and removes the previous TLS-verification bypass.

The project remains an educational desktop application. Before presenting it
as a production health product, it would need broader automated tests,
accessibility review, packaging, data migrations and a clearer privacy policy.

## 🗺️ Practical roadmap

1. Package a signed Windows executable.
2. Add database migration tests and import-validation tests.
3. Add charts to the GUI with a lightweight plotting layer.
4. Separate user-facing text for English, Spanish and Hebrew.
5. Build an optional web companion instead of trying to run Tkinter on Pages.
6. Publish versioned releases only after automated checks pass.

## 👤 Author

**Kevin Cusnir · Lirioth Teltanion**  
Developers Institute full-stack project · Beersheba, Israel

## 📄 License

MIT — see `LICENSE`.
