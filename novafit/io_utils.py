"""
Module: import, export, and demo data
Purpose: Provide validated JSON/CSV portability and reproducible local sample data.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Minimal deps; comments in ENGLISH; emojis sparingly.
"""

from __future__ import annotations

import csv
import json
import logging
import random
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Iterable, Literal, Mapping

from . import APP_NAME, __version__
from .config import CSV_EXPORT_PATH, EXPORT_PATH
from .database import NovaFitDatabase
from .models import HealthEntry
from .time_utils import now_local, timestamp_label

LOGGER = logging.getLogger(__name__)
ImportStrategy = Literal["replace", "skip"]
MAX_IMPORT_BYTES = 25 * 1024 * 1024
MAX_IMPORT_ROWS = 100_000


@dataclass(frozen=True, slots=True)
class ImportResult:
    """Summarize a validated import operation.

    Attributes:
        imported: Number of rows written.
        skipped: Number of existing rows skipped by strategy.
        invalid: Number of malformed rows ignored.
        errors: Short actionable messages for invalid rows.

    Example:
        >>> ImportResult(1, 0, 0, ()).imported
        1
    """

    imported: int
    skipped: int
    invalid: int
    errors: tuple[str, ...]


def export_json(
    database: NovaFitDatabase,
    destination: Path = EXPORT_PATH,
) -> int:
    """Export all entries to versioned UTF-8 JSON.

    Args:
        database: Initialized or uninitialized NovaFit database.
        destination: JSON file to create atomically.

    Returns:
        Number of exported entries.

    Raises:
        OSError: If the destination cannot be written.
        sqlite3.Error: If the database cannot be read.

    Example:
        >>> export_json(NovaFitDatabase(Path('data/example.db')), Path('data/example.json')) >= 0
        True
    """
    entries = [entry.to_dict() for entry in database.list(limit=None)]
    payload = {
        "metadata": {
            "exported_at": now_local().isoformat(timespec="seconds"),
            "application": APP_NAME,
            "version": __version__,
            "timezone": timestamp_label(),
            "total_entries": len(entries),
            "schema": "novafit-health-export-v2",
        },
        "health_data": entries,
    }
    _atomic_write_text(
        destination,
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
    )
    return len(entries)


def export_csv(
    database: NovaFitDatabase,
    destination: Path = CSV_EXPORT_PATH,
) -> int:
    """Export all entries to spreadsheet-compatible UTF-8 CSV.

    Args:
        database: NovaFit data source.
        destination: CSV file to create.

    Returns:
        Number of exported entries.

    Raises:
        OSError: If the destination cannot be written.

    Example:
        >>> export_csv(NovaFitDatabase(Path('data/example.db')), Path('data/example.csv')) >= 0
        True
    """
    entries = database.list(limit=None)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    with temporary.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["Date", "Steps", "Water (L)", "Calories", "Mood", "Note"],
        )
        writer.writeheader()
        for entry in entries:
            writer.writerow(
                {
                    "Date": entry.entry_date.isoformat(),
                    "Steps": entry.steps,
                    "Water (L)": entry.water_l,
                    "Calories": "" if entry.calories is None else entry.calories,
                    "Mood": _spreadsheet_safe(entry.mood or ""),
                    "Note": _spreadsheet_safe(entry.note or ""),
                }
            )
    temporary.replace(destination)
    return len(entries)


def import_json(
    database: NovaFitDatabase,
    source: Path,
    *,
    strategy: ImportStrategy = "replace",
) -> ImportResult:
    """Import JSON rows after validating every record independently.

    Args:
        database: Destination database.
        source: JSON export or simple list of records.
        strategy: ``replace`` updates matching dates; ``skip`` preserves them.

    Returns:
        Import counts and concise row-level errors.

    Raises:
        FileNotFoundError: If the source does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
        ValueError: If the root structure or strategy is unsupported.

    Example:
        >>> result = import_json(NovaFitDatabase(Path('data/example.db')), Path('data/example.json'))
        >>> isinstance(result.imported, int)
        True
    """
    if not source.exists():
        raise FileNotFoundError(f"JSON file not found: {source}")
    _guard_import_file(source)
    payload = json.loads(source.read_text(encoding="utf-8-sig"))
    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, Mapping) and isinstance(payload.get("health_data"), list):
        rows = payload["health_data"]
    elif isinstance(payload, Mapping):
        rows = [payload]
    else:
        raise ValueError("JSON root must be an object or list of objects.")
    return _import_rows(database, rows, strategy=strategy)


def import_csv(
    database: NovaFitDatabase,
    source: Path,
    *,
    strategy: ImportStrategy = "replace",
) -> ImportResult:
    """Import CSV data with tolerant legacy column aliases.

    Args:
        database: Destination database.
        source: CSV file with date, steps, and water columns.
        strategy: ``replace`` updates matching dates; ``skip`` preserves them.

    Returns:
        Import counts and concise row-level errors.

    Raises:
        FileNotFoundError: If the source does not exist.
        ValueError: If the strategy is unsupported.
        OSError: If the file cannot be read.

    Example:
        >>> result = import_csv(NovaFitDatabase(Path('data/example.db')), Path('data/example.csv'))
        >>> isinstance(result.invalid, int)
        True
    """
    if not source.exists():
        raise FileNotFoundError(f"CSV file not found: {source}")
    _guard_import_file(source)
    with source.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        return _import_rows(
            database,
            (_normalize_csv_row(row) for row in reader),
            strategy=strategy,
        )


def generate_demo_data(
    database: NovaFitDatabase,
    days: int = 30,
    *,
    end_date: date | None = None,
    locale: str = "en_US",
    replace: bool = True,
) -> int:
    """Generate realistic local demo records with Faker when available.

    Args:
        database: Destination database.
        days: Number of daily records, between 1 and 365.
        end_date: Latest generated day; today is used by default.
        locale: Faker locale when the optional dependency is installed.
        replace: Whether generated dates replace existing records.

    Returns:
        Number of rows inserted or replaced.

    Raises:
        ValueError: If the requested day count is outside 1–365.

    Example:
        >>> generate_demo_data(NovaFitDatabase(Path('data/example.db')), 3) >= 0
        True
    """
    if not 1 <= days <= 365:
        raise ValueError("Demo days must be between 1 and 365.")

    try:
        from faker import Faker  # Imported lazily to keep core operations available.

        fake = Faker(locale)
        integer = fake.random_int
        uniform = fake.pyfloat
        choice = fake.random_element
    except ImportError:
        LOGGER.warning("Faker is unavailable; using Python's deterministic fallback generator.")
        generator = random.Random(20260715)
        integer = lambda min, max: generator.randint(min, max)  # noqa: E731
        uniform = lambda min_value, max_value, right_digits=1: round(  # noqa: E731
            generator.uniform(min_value, max_value), right_digits
        )
        choice = lambda elements: generator.choice(list(elements))  # noqa: E731

    final_day = end_date or date.today()
    moods = ("Focused", "Calm", "Energetic", "Tired", "Happy", "Motivated")
    written = 0
    for offset in range(days):
        current = final_day - timedelta(days=offset)
        weekday_factor = 0.82 if current.weekday() in {4, 5} else 1.0
        steps = round(integer(min=3_000, max=16_000) * weekday_factor)
        entry = HealthEntry.build(
            current,
            steps,
            uniform(min_value=1.2, max_value=3.8, right_digits=1),
            integer(min=1_500, max=2_800),
            choice(elements=moods),
            "Generated demonstration record",
        )
        if replace:
            database.upsert(entry)
            written += 1
        elif database.insert_if_missing(entry):
            written += 1
    return written


def initialize_sample_data(database: NovaFitDatabase, *, replace: bool = False) -> int:
    """Create a small seven-day starter dataset without network access.

    Args:
        database: Destination database.
        replace: Whether starter dates may replace existing records.

    Returns:
        Number of rows written.

    Raises:
        sqlite3.Error: If the database cannot be updated.

    Example:
        >>> initialize_sample_data(NovaFitDatabase(Path('data/example.db'))) >= 0
        True
    """
    samples = (
        (8_500, 2.1, 1_850, "Happy"),
        (12_000, 2.5, 2_100, "Energetic"),
        (6_500, 1.8, 1_650, "Tired"),
        (10_500, 2.2, 1_950, "Calm"),
        (15_000, 3.0, 2_300, "Motivated"),
        (7_800, 2.0, 1_700, "Focused"),
        (9_200, 2.3, 1_800, "Happy"),
    )
    first_day = date.today() - timedelta(days=len(samples) - 1)
    written = 0
    for offset, (steps, water, calories, mood) in enumerate(samples):
        entry = HealthEntry.build(
            first_day + timedelta(days=offset),
            steps,
            water,
            calories,
            mood,
            "NovaFit starter sample",
        )
        if replace:
            database.upsert(entry)
            written += 1
        elif database.insert_if_missing(entry):
            written += 1
    return written


def backup_file(source: Path, backup_dir: Path) -> Path | None:
    """Copy a file into a timestamped backup folder when it exists.

    Args:
        source: File to preserve.
        backup_dir: Directory that receives the copy.

    Returns:
        Backup path, or ``None`` when the source is absent.

    Raises:
        OSError: If an existing source cannot be copied.

    Example:
        >>> backup_file(Path('missing.file'), Path('backups')) is None
        True
    """
    if not source.exists():
        return None
    import shutil

    backup_dir.mkdir(parents=True, exist_ok=True)
    destination = backup_dir / source.name
    shutil.copy2(source, destination)
    return destination


def _import_rows(
    database: NovaFitDatabase,
    rows: Iterable[Any],
    *,
    strategy: ImportStrategy,
) -> ImportResult:
    if strategy not in {"replace", "skip"}:
        raise ValueError("Import strategy must be 'replace' or 'skip'.")

    invalid = 0
    errors: list[str] = []
    valid_entries: list[HealthEntry] = []
    for index, raw in enumerate(rows, start=1):
        if index > MAX_IMPORT_ROWS:
            raise ValueError(f"Import cannot exceed {MAX_IMPORT_ROWS:,} rows.")
        if not isinstance(raw, Mapping):
            invalid += 1
            errors.append(f"Row {index}: expected an object.")
            continue
        try:
            entry = HealthEntry.from_mapping(raw)
            valid_entries.append(entry)
        except (TypeError, ValueError) as exc:
            invalid += 1
            if len(errors) < 10:
                errors.append(f"Row {index}: {exc}")
    imported, skipped = database.write_many(
        valid_entries,
        replace=strategy == "replace",
    )
    return ImportResult(imported, skipped, invalid, tuple(errors))


def _normalize_csv_row(row: Mapping[str, Any]) -> dict[str, Any]:
    lowered = {str(key).strip().lower(): value for key, value in row.items()}
    return {
        "date": lowered.get("date") or lowered.get("entry_date"),
        "steps": lowered.get("steps"),
        "water_l": (lowered.get("water (l)") or lowered.get("water_l") or lowered.get("water")),
        "calories": lowered.get("calories"),
        "mood": lowered.get("mood"),
        "note": lowered.get("note"),
    }


def _atomic_write_text(destination: Path, content: str) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(destination)


def _guard_import_file(source: Path) -> None:
    """Reject unexpectedly large imports before loading them into memory."""
    size = source.stat().st_size
    if size > MAX_IMPORT_BYTES:
        raise ValueError(
            f"Import file is {size / (1024 * 1024):.1f} MiB; the safety limit is "
            f"{MAX_IMPORT_BYTES // (1024 * 1024)} MiB."
        )


def _spreadsheet_safe(value: str) -> str:
    """Neutralize text that spreadsheet programs could interpret as a formula."""
    if value and value[0] in {"=", "+", "-", "@"}:
        return "'" + value
    return value
