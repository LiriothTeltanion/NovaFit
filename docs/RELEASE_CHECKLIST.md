# NovaFit 4.2 Release Checklist ✅

## Source

- [ ] `git status --short` reviewed
- [ ] Branch name is focused and intentional
- [ ] No generated dependency folders staged
- [ ] No database, export, log or secret staged
- [ ] Version is `4.2.0` in package and generated project metadata
- [ ] `python scripts/sync_docs.py --check`
- [ ] Changelog updated

## Automated quality

- [ ] `python -m compileall -q novafit scripts tests`
- [ ] `python -m unittest discover -s tests -v`
- [ ] `python scripts/verify.py`
- [ ] `VERIFY_ALL.bat`
- [ ] `git diff --check`
- [ ] GitHub Actions green on Windows and Ubuntu
- [ ] Exact staged Pages artifact passes `tools/site_audit.py`

## Core product

- [ ] Add a record
- [ ] Update the same date
- [ ] Filter record library
- [ ] Delete a synthetic date
- [ ] Dashboard refreshes
- [ ] All four analytics views render
- [ ] 7, 30, 90 and 365-day ranges render
- [ ] Dark and light themes render
- [ ] Reduced motion setting persists

## Portability

- [ ] JSON export/import round trip
- [ ] CSV export/import round trip
- [ ] Replace strategy verified
- [ ] Skip strategy verified
- [ ] HTML report opens offline
- [ ] PNG export is readable at full resolution

## Windows

- [ ] `setup_windows.bat`
- [ ] `run_novafit.bat`
- [ ] `run_cli.bat`
- [ ] `verify_windows.bat`
- [ ] `export_backup.bat`
- [ ] `export_report.bat`
- [ ] `export_analytics_gallery.bat`
- [ ] `open_data_folder.bat`
- [ ] `BUILD_WINDOWS_STANDALONE.bat`
- [ ] Frozen `NovaFit-CLI.exe --version`, `--sample`, and `--dashboard` smoke pass
- [ ] Standalone data is isolated under `%LOCALAPPDATA%\NovaFit`
- [ ] Exact onedir manifest audit passes

## Privacy

- [ ] Screenshot uses deterministic demo records
- [ ] Weather tested without health payload
- [ ] No personal export included in release ZIP
- [ ] No personal SQLite file included
- [ ] No runtime log included
- [ ] `.gitignore` reviewed

## Documentation

- [ ] README images render
- [ ] Links resolve inside repository
- [ ] CLI help matches README
- [ ] Analytics formulas match code
- [ ] Test count matches current run
- [ ] `docs/PROJECT_FACTS.md`, `portfolio/project.json` and `assets/manifest.json` are synchronized
- [ ] Actual GUI screenshot labeled honestly
- [ ] Conceptual assets are not called real screenshots

## GitHub Pages

- [ ] `site/` contains no duplicated root `assets/`, runtime `data/` or private paths
- [ ] `_site/` is generated from `site/`, public `assets/` and `portfolio/project.json`
- [ ] `manifest.webmanifest`, service worker, canonical URL and local links pass audit
- [ ] Pages workflow follows a green same-repository `main` push, not a fork PR run
- [ ] `https://liriothteltanion.github.io/NovaFit/` loads after deployment
- [ ] PWA copy describes a public showcase, not the Tkinter desktop runtime
- [ ] Download links point to GitHub Releases; no executable or ZIP is embedded in Pages

## Release

- [ ] Commit messages are descriptive
- [ ] Direct-main publication was explicitly authorized, or a reviewed pull request is ready
- [ ] Create immutable tag `v4.2.0` only after Pages and native Windows verification
- [ ] Attach source ZIP
- [ ] Attach Windows-ready ZIP
- [ ] Attach `NovaFit-vX.Y.Z-Windows-x64-Standalone.zip`
- [ ] Verify the standalone `.zip.sha256` sidecar
- [ ] Attach SHA-256 checksums
- [ ] Publish release notes from changelog
- [ ] `.github/workflows/release.yml` completed successfully for the tag
