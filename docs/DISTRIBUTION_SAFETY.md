# Distribution Safety and Checker Repair 🛡️

## Reported failure

The reported Windows run completed all NovaFit tests, smoke exports and GitHub-profile generation. The final audit then raised:

```text
ValueError: Private/runtime files must be removed: NovaFit\data\novafit.db
```

That database was a legitimate runtime file, not source-code leakage. Rejecting it inside the user’s working copy was incorrect.

## Correct model

### Workspace verification

`python tools/package_audit.py`

- verifies code, tests, Markdown links, SVG parsing and BAT line endings;
- reports runtime database/log files;
- leaves them untouched;
- passes when the rest of the workspace is healthy.

### Release-staging verification

`python tools/package_audit.py --strict-distribution`

- runs only inside a clean temporary staging tree;
- rejects databases, SQLite files, `.env`, keys, logs and local configuration;
- proves that the ZIP is safe to distribute.

## Release builder exclusion policy

The builder excludes:

- `.git/`
- `.venv/`
- caches and bytecode;
- `NovaFit/data/*` except `.gitkeep`;
- `*.db`, `*.sqlite*`;
- `.env` and secret-key formats;
- `novafit.log`;
- locally generated config and exports.

## Why not delete the user database?

A verification script should not destroy user data. The release builder should copy public files to a clean staging directory instead of mutating the working repository.

## Regression tests

Behavioral regression tests protect:

1. workspace preservation of runtime database paths;
2. strict-staging rejection of runtime files;
3. rejection of credential-like files in every mode;
4. default Windows verification not invoking release-strict mode on the user workspace.

The audit also validates required entry points, local Markdown links, SVG XML,
and Windows BAT line endings. It never deletes or rewrites a user file.
