# NovaFit 4.1 Release Checklist ✅

## Source

- [ ] `git status --short` reviewed
- [ ] Branch name is focused and intentional
- [ ] No generated dependency folders staged
- [ ] No database, export, log or secret staged
- [ ] Version is `4.1.0` in package and project metadata
- [ ] `python scripts/sync_docs.py --check`
- [ ] Changelog updated

## Automated quality

- [ ] `python -m compileall -q novafit scripts tests`
- [ ] `python -m unittest discover -s tests -v`
- [ ] `python scripts/verify.py`
- [ ] `VERIFY_ALL.bat`
- [ ] `git diff --check`
- [ ] GitHub Actions green on Windows and Ubuntu

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

## Release

- [ ] Commit messages are descriptive
- [ ] Direct-main publication was explicitly authorized, or a reviewed pull request is ready
- [ ] Tag `v4.1.0`
- [ ] Attach source ZIP
- [ ] Attach Windows-ready ZIP
- [ ] Attach SHA-256 checksums
- [ ] Publish release notes from changelog
- [ ] `.github/workflows/release.yml` completed successfully for the tag
