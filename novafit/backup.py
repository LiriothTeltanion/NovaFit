"""Create verifiable, all-profile NovaFit backup archives."""

from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
import tempfile
import zipfile
from contextlib import closing
from pathlib import Path

from . import APP_NAME, __version__
from .config import CONFIG_PATH, DATA_DIR
from .database import NovaFitDatabase
from .time_utils import now_local, timestamp_label

BACKUP_DIR = DATA_DIR / "backups"
BACKUP_SCHEMA = "novafit-complete-backup-v3"


def create_complete_backup(
    database: NovaFitDatabase,
    destination: Path | None = None,
    *,
    config_path: Path = CONFIG_PATH,
) -> Path:
    """Create a consistent ZIP containing every profile, record, and setting.

    SQLite's online backup API is used so WAL-mode data remains consistent even
    while NovaFit is open. The archive includes SHA-256 hashes in its manifest.
    """
    database.initialize()
    created_at = now_local()
    target = destination or (BACKUP_DIR / f"novafit-complete-{created_at.strftime('%Y%m%d-%H%M%S')}.zip")
    target = Path(target)
    if target.suffix.lower() != ".zip":
        target = target / f"novafit-complete-{created_at.strftime('%Y%m%d-%H%M%S')}.zip"
    target.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="novafit-backup-") as temp_dir:
        staging = Path(temp_dir)
        database_snapshot = staging / "novafit.db"
        with (
            closing(sqlite3.connect(database.path)) as source,
            closing(sqlite3.connect(database_snapshot)) as sink,
        ):
            source.backup(sink)
        integrity = _database_integrity(database_snapshot)
        if integrity != "ok":
            raise RuntimeError(f"Backup database integrity check failed: {integrity}")

        included = [database_snapshot]
        if config_path.exists():
            config_copy = staging / "config.json"
            shutil.copy2(config_path, config_copy)
            included.append(config_copy)

        readme = staging / "RESTORE_INSTRUCTIONS.txt"
        readme.write_text(
            "NovaFit complete backup\n"
            "=======================\n\n"
            "This archive contains every local profile and health record in novafit.db.\n"
            "Keep it private. Before restoring, close NovaFit and preserve your current data folder.\n"
            "Use the manifest hashes to verify that files were not modified.\n",
            encoding="utf-8",
        )
        included.append(readme)

        manifest = {
            "schema": BACKUP_SCHEMA,
            "application": APP_NAME,
            "version": __version__,
            "created_at": created_at.isoformat(timespec="seconds"),
            "timezone": timestamp_label(),
            "database_integrity": integrity,
            "files": [
                {
                    "name": item.name,
                    "bytes": item.stat().st_size,
                    "sha256": _sha256(item),
                }
                for item in included
            ],
        }
        manifest_path = staging / "manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        included.append(manifest_path)

        temporary = target.with_suffix(target.suffix + ".tmp")
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for item in included:
                archive.write(item, item.name)
        _verify_archive(temporary)
        temporary.replace(target)
    return target


def inspect_complete_backup(source: Path) -> dict[str, object]:
    """Validate a NovaFit backup archive and return its trusted manifest."""
    source = Path(source)
    if not source.exists():
        raise FileNotFoundError(f"Backup not found: {source}")
    with zipfile.ZipFile(source, "r") as archive:
        names = set(archive.namelist())
        required = {"novafit.db", "manifest.json", "RESTORE_INSTRUCTIONS.txt"}
        missing = required - names
        if missing:
            raise ValueError(f"Backup is missing: {', '.join(sorted(missing))}")
        manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
        if manifest.get("schema") != BACKUP_SCHEMA:
            raise ValueError("Unsupported NovaFit backup schema.")
        for item in manifest.get("files", []):
            name = str(item["name"])
            payload = archive.read(name)
            digest = hashlib.sha256(payload).hexdigest()
            if digest != item["sha256"]:
                raise ValueError(f"Backup checksum mismatch: {name}")
        return manifest


def _database_integrity(path: Path) -> str:
    with closing(sqlite3.connect(path)) as connection:
        row = connection.execute("PRAGMA integrity_check").fetchone()
    return str(row[0])


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _verify_archive(path: Path) -> None:
    with zipfile.ZipFile(path, "r") as archive:
        failed = archive.testzip()
    if failed is not None:
        raise RuntimeError(f"Backup ZIP verification failed at {failed}.")
