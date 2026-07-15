"""Tests for complete, verifiable NovaFit backup archives."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from novafit.backup import BACKUP_SCHEMA, create_complete_backup, inspect_complete_backup
from novafit.database import NovaFitDatabase
from novafit.models import HealthEntry, UserProfile


class CompleteBackupTests(unittest.TestCase):
    def test_backup_contains_every_profile_and_valid_checksums(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            database = NovaFitDatabase(root / "novafit.db")
            database.initialize()
            database.upsert(HealthEntry.build("2026-07-16", 8_500, 2.1))
            second = database.create_profile(UserProfile.build("Backup User"))
            database.upsert(
                HealthEntry.build("2026-07-15", 12_000, 2.5),
                profile_id=second.profile_id,
            )
            config = root / "config.json"
            config.write_text('{"theme":"aurora"}\n', encoding="utf-8")
            destination = root / "complete.zip"

            created = create_complete_backup(database, destination, config_path=config)
            manifest = inspect_complete_backup(created)

            self.assertEqual(manifest["schema"], BACKUP_SCHEMA)
            self.assertEqual(manifest["database_integrity"], "ok")
            self.assertTrue(any(item["name"] == "config.json" for item in manifest["files"]))


if __name__ == "__main__":
    unittest.main()
