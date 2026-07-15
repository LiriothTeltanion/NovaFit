# Testing and Verification 🧪

## Automated result

```text
74 tests run
74 passed
0 failed
```

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
REPAIR_AND_VERIFY.bat
```

The verifier compiles the package, checks dependencies, runs all unit tests and executes an isolated smoke workflow with a temporary SQLite database.

## Smoke workflow

- insert starter records;
- print dashboard;
- print Motivation Center;
- print Spanish recommendations;
- create a Hebrew running profile;
- list profiles;
- export JSON;
- export Training Atlas PNG;
- export offline HTML report.

## GUI gate

The release process launches `NovaFitApp`, processes the event loop and captures real Tkinter workspaces under Xvfb. The final Windows release should additionally be opened manually on native Windows for DPI scaling and font-rendering review.

## Honest limitation

`74/74 passed` is not a claim of complete line or branch coverage. It reports the implemented automated cases exactly.
