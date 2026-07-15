# NovaFit Data Model 💾

## Domain object

`HealthEntry` is immutable and validated.

```python
HealthEntry(
    entry_date=date,
    steps=int,
    water_l=float,
    calories=int | None,
    mood=str | None,
    note=str | None,
)
```

Use `HealthEntry.build()` for user, CSV, JSON and database values.

## Validation limits

The application rejects:

- malformed ISO dates;
- negative steps;
- step values beyond the product bound;
- negative or implausibly high water;
- negative or implausibly high calories;
- mood or note text beyond configured lengths.

Empty optional values become `None`.

## SQLite schema

```sql
CREATE TABLE logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL UNIQUE,
    steps INTEGER NOT NULL DEFAULT 0 CHECK (steps >= 0),
    water_l REAL NOT NULL DEFAULT 0 CHECK (water_l >= 0),
    calories INTEGER CHECK (calories IS NULL OR calories >= 0),
    mood TEXT,
    note TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

## Repository methods

| Method | Behavior |
|---|---|
| `initialize()` | Create/upgrade schema |
| `upsert(entry)` | Insert or update by date |
| `insert_if_missing(entry)` | Insert only when absent |
| `get(date)` | Return one entry or `None` |
| `list(limit)` | Newest-first rows |
| `search(start, end)` | Inclusive date range |
| `delete(date)` | Remove one row |
| `clear()` | Remove all rows |
| `count()` | Return row count |

## Connection configuration

Each connection:

- has a timeout;
- enables foreign keys;
- enables WAL mode;
- returns `sqlite3.Row` values;
- closes in a context-manager `finally` block.

## Migration

The application checks `PRAGMA table_info(logs)` and adds compatible missing columns.

The explicit migration script copies the existing database before initializing the current schema.

## JSON schema

Export envelope:

```text
metadata
health_data[]
```

Metadata identifies:

- export time;
- application;
- version;
- timezone;
- row count;
- schema label.

## CSV schema

Canonical columns:

```text
Date
Steps
Water (L)
Calories
Mood
Note
```

Import recognizes normalized alternatives such as `date`, `entry_date`, `water_l` and `water`.

## Import strategies

### replace

A validated matching date updates the existing row.

### skip

A validated matching date remains unchanged and increments the skipped count.

Invalid rows never enter SQLite.

## Atomic writes

JSON and settings are written to a temporary sibling file and then replaced atomically.

CSV is generated as a complete export file with UTF-8 BOM.

## Privacy classification

Treat these as private:

- `.db` files;
- JSON exports;
- CSV exports;
- HTML reports;
- screenshots containing records;
- logs when errors include local paths.

The repository `.gitignore` excludes expected runtime artifacts, but developers must still review staged files.
