# NovaFit Security & Privacy 🔒

## Security posture

NovaFit is a personal local desktop application and learning portfolio. It uses secure defaults proportional to that scope but does not claim medical, enterprise, or regulated-system certification.

## Assets being protected

Potentially sensitive artifacts:

- SQLite database;
- JSON and CSV exports;
- HTML reports;
- screenshots;
- free-text notes;
- local log paths.

## Local-first boundary

NovaFit does not:

- create accounts;
- upload records;
- use remote analytics;
- synchronize in the background;
- include advertising trackers;
- include an AI API;
- expose a server port.

## Weather boundary

The optional weather request includes:

```text
latitude
longitude
current weather fields requested
```

It excludes:

```text
steps
water
calories
mood
notes
database contents
export contents
```

TLS certificate verification remains enabled.

## Database controls

- parameterized statements;
- SQLite constraints;
- unique date;
- bounded validation before persistence;
- explicit transaction commits;
- reliable connection closure;
- no SQL built from user text except controlled schema migration identifiers.

## Import controls

- root-shape validation;
- row-shape validation;
- domain validation per row;
- explicit replace/skip strategy;
- malformed-row accounting;
- limited error summary.

## Output controls

- atomic JSON/settings writes;
- HTML escaping for text fields;
- no remote scripts in reports;
- no remote fonts in reports;
- ignored runtime artifacts.

## Destructive actions

GUI clear-all requires two confirmations. CLI delete targets one explicit date.

## Threat assumptions

NovaFit assumes:

- one local user profile;
- an operating system account with appropriate file permissions;
- no hostile local administrator;
- no untrusted plugin code;
- no sharing of exports by default.

## Out of scope

- full-disk encryption;
- encrypted SQLite;
- biometric access;
- multi-user authorization;
- remote breach response;
- clinical data governance;
- regulatory compliance certification.

## Safe publication checklist

Before committing or sharing:

```bash
git status --short
git diff --cached --name-only
```

Confirm no files match:

```text
*.db
*.sqlite
.env
private exports
personal HTML reports
screenshots with real records
logs containing private paths
```

## Dependency safety

Dependencies are bounded in `requirements.txt`. Release review should include vulnerability and update checks appropriate to the current environment.

## Reporting a security issue

Do not place a real private record or secret in a public issue. Describe the behavior using synthetic data and provide the smallest reproducible example.
