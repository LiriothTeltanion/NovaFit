# Testing and Verification 🧪

## Automated result

The authoritative test total is the one printed by the current workflow. It is
also generated into the project facts during documentation synchronization, so
the README and profile do not need a hand-maintained test claim.

## Coverage areas

- Validation and models
- Profile-scoped SQLite CRUD
- Legacy schema migration
- Profile preference round trips
- Primary-profile protection
- EN/ES/HE normalization and RTL metadata
- Twelve themes and legacy aliases
- Core and advanced analytics
- Training Atlas export and aliases
- Recommendation confidence, localization and safety scope
- Motivation behavior
- JSON and CSV round trips
- HTML report escaping
- CLI record, profile, recommendation and chart routes
- Windows environment contract
- Workspace versus strict-distribution audit contract
- Timezone fallback
- Weather success and offline recovery

## One-command verification

```bash
python scripts/verify.py
```

On Windows:

```text
VERIFY_ALL.bat
```

`VERIFY_ALL.bat` creates or repairs the isolated environment, installs the
development gates, then runs compilation, package audit, Ruff, Pyright, all
unit tests and an isolated smoke workflow. `REPAIR_AND_VERIFY.bat` remains a
runtime-focused compatibility route.

## Smoke workflow

- insert starter records;
- print dashboard;
- print Motivation Center;
- print Spanish recommendations;
- create a Hebrew running profile;
- list profiles;
- export JSON;
- create and verify a complete all-profile ZIP backup;
- export Training Atlas PNG;
- export offline HTML report.

## GUI gate

The release process launches `NovaFitApp`, processes the event loop and captures real Tkinter workspaces under Xvfb. The final Windows release should additionally be opened manually on native Windows for DPI scaling and font-rendering review.

## Honest limitation

Passing every currently discovered automated case is not a claim of complete line or branch coverage. The workflow result is the exact reproducible status of the implemented suite at that commit.
