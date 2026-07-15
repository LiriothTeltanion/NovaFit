"""
Module: legacy database migration
Purpose: Back up and upgrade a NovaFit v1 SQLite file without deleting health records.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Minimal deps; comments in ENGLISH; emojis sparingly.
"""

from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path

from novafit.database import NovaFitDatabase


def build_parser() -> argparse.ArgumentParser:
    """Create the legacy migration CLI parser.

    Returns:
        Configured argument parser.

    Raises:
        None.

    Example:
        >>> build_parser().prog
        'migrate_legacy_db'
    """
    parser = argparse.ArgumentParser(
        prog="migrate_legacy_db",
        description="Back up and upgrade an existing NovaFit SQLite database.",
    )
    parser.add_argument("database", type=Path, help="Path to the legacy novafit.db file.")
    return parser


def migrate(database_path: Path) -> Path:
    """Back up and initialize a legacy NovaFit database.

    Args:
        database_path: Existing SQLite file.

    Returns:
        Backup path created before migration.

    Raises:
        FileNotFoundError: If the source database does not exist.
        OSError: If backup or migration fails.

    Example:
        >>> migrate(Path('data/novafit.db'))  # doctest: +SKIP
    """
    if not database_path.exists():
        raise FileNotFoundError(f"Database not found: {database_path}")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = database_path.with_name(f"{database_path.stem}_backup_{stamp}{database_path.suffix}")
    shutil.copy2(database_path, backup)
    NovaFitDatabase(database_path).initialize()
    return backup


def main() -> int:
    """Run the legacy migration command.

    Returns:
        ``0`` after a successful backup and migration.

    Raises:
        Exception: Failures stay visible so no migration looks successful silently.

    Example:
        >>> main()  # doctest: +SKIP
        0
    """
    args = build_parser().parse_args()
    backup = migrate(args.database)
    print(f"Migration complete. Backup saved to {backup} ✅")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
