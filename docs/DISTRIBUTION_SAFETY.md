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

Three source-contract tests protect:

1. presence of strict distribution mode;
2. workspace allowance for runtime database paths;
3. default Windows checker not invoking strict mode on the user workspace.
