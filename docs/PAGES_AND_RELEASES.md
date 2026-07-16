# GitHub Pages, PWA Showcase and Desktop Releases 🌐🪟

## Stable public URL

The public NovaFit showcase lives at:

**https://liriothteltanion.github.io/NovaFit/**

This URL follows the latest verified `main` deployment. It stays stable across
desktop versions and should be used by the GitHub profile, social cards and
portfolio links.

## Three delivery surfaces, three honest boundaries

| Surface | Purpose | Personal data | Full NovaFit runtime |
|---|---|---|---|
| **GitHub Pages / installable PWA showcase** | Public product story, visual tour, verified project facts and release links | Never reads or stores desktop profiles, SQLite records, exports or backups | **No** |
| **Windows release executable** | One-click desktop experience with Tkinter, analytics, local profiles and backups | Remains on the user's computer | **Yes** |
| **Source + BAT/CLI route** | Development, inspection, self-repair and advanced CLI use | Remains in the configured local workspace | **Yes** |

Installing the Pages showcase from a browser installs the public presentation
shell. It does not turn the website into the Tkinter application and does not
gain access to `data/novafit.db`, OneDrive, local exports or Windows files.

## Verified Pages deployment

`.github/workflows/pages.yml` deploys only after the **NovaFit Quality** workflow
has completed successfully for a `push` to `main` from this repository. A fork
pull request or an unrelated workflow run cannot provide deployment code.

The deployment sequence is:

1. check out the exact green commit SHA;
2. copy tracked `site/` files into temporary `_site/` staging;
3. copy the existing public `assets/` tree to `_site/assets/`;
4. copy generated `portfolio/project.json` to `_site/project.json`;
5. run `tools/site_audit.py` against that exact artifact;
6. upload the audited artifact with the official Pages action;
7. deploy through the protected `github-pages` environment.

The build job has read-only repository access. Only the separate deployment job
receives `pages: write` and `id-token: write`.

## Pages privacy gate

The site audit fails when it finds:

- SQLite databases, logs, backups, executables, ZIP files, environment files or keys;
- `data/`, `.venv/`, `.git/` or `.nova-pack-backup/` paths;
- absolute private computer paths such as `C:\Users\...` or `/home/...`;
- credential-like values;
- symbolic links;
- broken local HTML/CSS/manifest links;
- an invalid PWA manifest or project manifest;
- a canonical URL outside the official Pages address.

The audit is offline and deterministic. External links are not treated as proof
of availability; their destinations remain owned by the external service.

## Source and generated facts

`site/` owns the hand-designed public experience. It does not duplicate the
large visual library or factual counters:

- media comes from root `assets/` during staging;
- version, test count, release URL and privacy facts come from generated
  `portfolio/project.json`;
- `scripts/sync_docs.py --write` updates the public manifest and
  `docs/PROJECT_FACTS.md` from source metadata;
- `scripts/stage_pages.py` produces the temporary deployable tree;
- `_site/` is generated and must never be committed.

## Local verification

Run the full Windows contract:

```text
VERIFY_ALL.bat
```

Or validate a staged Pages artifact directly:

```bash
python scripts/stage_pages.py --output _site
python tools/site_audit.py --site-root _site --base-path /NovaFit/
```

The temporary `_site/` directory can be recreated at any time and is ignored by
Git. The site source and root assets remain the only tracked inputs.

## Windows one-click delivery

Desktop downloads belong to GitHub Releases, not to the Pages artifact. The
Windows packaging pipeline is expected to create the executable and supporting
release files, audit the produced distribution, and attach them to the matching
tag. Pages links users to the release rather than copying binaries into the web
artifact.

Users can choose:

1. the Windows executable from the latest verified GitHub Release;
2. `run_novafit.bat` when working from source;
3. `VERIFY_ALL.bat` when the local environment needs complete repair and QA.

Code signing must not be claimed unless the published executable is actually
signed and its signature has been verified on native Windows.

## Version and tag strategy

The target release for this delivery layer is **NovaFit 4.2.0**, tagged
**`v4.2.0`** only after all of these are true:

- package and generated manifest versions match `4.2.0`;
- `main` quality is green;
- Pages deploys the exact green commit;
- the Windows executable passes native launch and privacy checks;
- release notes describe both the showcase and desktop boundaries.

Tags are immutable release coordinates. Do not move or recreate `v4.2.0` after
publication. Use `v4.2.1` for a compatible bug fix and a later minor version for
new product behavior. The stable Pages URL continues to follow verified `main`
and is deliberately not versioned.
