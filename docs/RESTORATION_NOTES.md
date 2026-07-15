# NovaFit Restoration Notes

## Why restoration was necessary

The public repository history showed a functional modular NovaFit package followed by a commit that removed the package modules while documentation and launchers continued to describe a working product.

That mismatch damaged reproducibility and recruiter trust.

## Evidence used

The rebuild was grounded in:

- historical modular commits;
- the public README feature contract;
- launcher behavior;
- SQLite schema examples;
- CLI and GUI descriptions;
- previous import/export code;
- weather integration code;
- project-specific coding rules.

## Preserved product ideas

- daily steps, water, calories and mood;
- local SQLite storage;
- CLI and desktop GUI;
- JSON/CSV portability;
- sample and Faker records;
- optional weather;
- goals and trends;
- Windows launchers.

## Replaced implementation decisions

### SSL

Historical code disabled SSL verification globally and called Requests with `verify=False`.

Definitive behavior:

- normal TLS verification;
- bounded timeout;
- recoverable network errors;
- no global SSL environment changes.

### Database access

Historical modules mixed direct SQLite calls across interfaces.

Definitive behavior:

- one database adapter;
- parameterized queries;
- context-managed connections;
- compatible schema upgrade;
- explicit backup-first migration script.

### Validation

Historical paths validated fields inconsistently.

Definitive behavior:

- one immutable domain model;
- one validation layer;
- shared rules for GUI, CLI, JSON and CSV.

### Analytics

Historical dashboards were mostly summary values and basic chart promises.

Definitive behavior:

- three visual studios;
- documented formulas;
- explicit missing dates;
- deterministic exports;
- grounded text insights;
- no medical claims.

### Delivery

Historical README instructions did not reflect the deleted code.

Definitive behavior:

- ready-to-run launchers;
- automated tests;
- CI;
- release verifier;
- complete documentation;
- actual GUI capture.

## Git strategy

Recommended:

```text
fix(novafit): restore complete modular application
feat(analytics): add definitive three-view analytics studio
feat(reporting): add offline visual reports
chore(ci): verify Windows and Ubuntu release paths
docs(novafit): publish definitive product documentation
```

Do not force-push merely to hide the destructive historical commit. A transparent restoration demonstrates incident recovery and engineering ownership.
