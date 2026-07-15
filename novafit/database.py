"""
Module: SQLite persistence
Purpose: Provide transactional multi-profile CRUD, safe schema upgrades, and
    testable local storage without exposing wellness data to a server.
Author: Kevin "Lirioth" Cusnir
Date: 2026-07-15 | TZ: Asia/Jerusalem
Notes: Standard-library SQLite; comments in ENGLISH; emojis sparingly.
"""

from __future__ import annotations

import logging
import sqlite3
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Any

from .config import DB_PATH
from .models import HealthEntry, UserProfile

LOGGER = logging.getLogger(__name__)
SCHEMA_VERSION = 4
DEFAULT_PROFILE_NAME = "Primary User"


class NovaFitDatabase:
    """Manage the NovaFit SQLite database through a small explicit API.

    Args:
        path: SQLite file location. Tests may supply a temporary path.

    Example:
        >>> db = NovaFitDatabase(Path('data/example.db'))
        >>> db.initialize()
    """

    def __init__(self, path: Path = DB_PATH, active_profile_id: int = 1) -> None:
        self.path = Path(path)
        self.active_profile_id = active_profile_id

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        """Open a configured SQLite connection and close it reliably.

        Yields:
            A connection using dictionary-like ``sqlite3.Row`` results.

        Raises:
            sqlite3.Error: If the database cannot be opened.

        Example:
            >>> db = NovaFitDatabase(Path('data/example.db'))
            >>> with db.connect() as connection:
            ...     isinstance(connection, sqlite3.Connection)
            True
        """
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        try:
            yield connection
        finally:
            connection.close()

    def initialize(self) -> None:
        """Create tables and upgrade older single-user NovaFit databases.

        Legacy ``logs`` rows are migrated to profile ``1`` and the old unique
        date constraint becomes ``UNIQUE(user_id, date)``. No health row is
        discarded during the supported migration.

        Returns:
            None.

        Raises:
            sqlite3.Error: If schema creation or migration fails.

        Example:
            >>> NovaFitDatabase(Path('data/example.db')).initialize()
        """
        with self.connect() as connection:
            self._create_profile_tables(connection)
            self._ensure_default_profile(connection)
            if self._table_exists(connection, "logs"):
                columns = self._column_names(connection, "logs")
                if "user_id" not in columns:
                    self._rebuild_legacy_logs(connection)
                else:
                    self._migrate_log_columns(connection)
            else:
                self._create_logs_table(connection)
            self._create_indexes(connection)
            connection.execute(
                """
                INSERT INTO app_meta(key, value) VALUES('schema_version', ?)
                ON CONFLICT(key) DO UPDATE SET value = excluded.value
                """,
                (str(SCHEMA_VERSION),),
            )
            connection.commit()
        if self.get_profile(self.active_profile_id) is None:
            self.active_profile_id = 1

    def set_active_profile(self, profile_id: int) -> UserProfile:
        """Select the profile used by CRUD methods without an explicit id.

        Args:
            profile_id: Existing local profile identifier.

        Returns:
            The selected profile.

        Raises:
            ValueError: If the profile does not exist.

        Example:
            >>> db = NovaFitDatabase(Path('data/example.db'))
            >>> db.initialize(); db.set_active_profile(1).profile_id
            1
        """
        profile = self.get_profile(profile_id)
        if profile is None:
            raise ValueError(f"Profile {profile_id} does not exist.")
        self.active_profile_id = profile_id
        return profile

    def list_profiles(self) -> list[UserProfile]:
        """Return every local user profile in creation order.

        Returns:
            Profiles ordered by identifier.

        Raises:
            sqlite3.Error: If the query fails.

        Example:
            >>> len(NovaFitDatabase(Path('data/example.db')).list_profiles()) >= 1
            True
        """
        self.initialize()
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT id, display_name, avatar, language, theme, step_goal,
                       water_goal_l, calorie_goal, activity_level, sport_focus
                FROM profiles ORDER BY id
                """
            ).fetchall()
        return [self._row_to_profile(row) for row in rows]

    def get_profile(self, profile_id: int) -> UserProfile | None:
        """Return one profile by identifier.

        Args:
            profile_id: Local profile identifier.

        Returns:
            Matching profile or ``None``.

        Raises:
            sqlite3.Error: If the query fails.

        Example:
            >>> db = NovaFitDatabase(Path('data/example.db'))
            >>> db.initialize(); db.get_profile(1) is not None
            True
        """
        with self.connect() as connection:
            if not self._table_exists(connection, "profiles"):
                return None
            row = connection.execute(
                """
                SELECT id, display_name, avatar, language, theme, step_goal,
                       water_goal_l, calorie_goal, activity_level, sport_focus
                FROM profiles WHERE id = ?
                """,
                (profile_id,),
            ).fetchone()
        return self._row_to_profile(row) if row else None

    def profile_by_name(self, display_name: str) -> UserProfile | None:
        """Return a profile using case-insensitive display-name matching.

        Args:
            display_name: Name entered by a user or CLI flag.

        Returns:
            Matching profile or ``None``.

        Example:
            >>> db = NovaFitDatabase(Path('data/example.db'))
            >>> db.initialize(); db.profile_by_name('primary user') is not None
            True
        """
        self.initialize()
        with self.connect() as connection:
            row = connection.execute(
                """
                SELECT id, display_name, avatar, language, theme, step_goal,
                       water_goal_l, calorie_goal, activity_level, sport_focus
                FROM profiles WHERE display_name = ? COLLATE NOCASE
                """,
                (display_name.strip(),),
            ).fetchone()
        return self._row_to_profile(row) if row else None

    def create_profile(self, profile: UserProfile) -> UserProfile:
        """Insert a validated local user profile.

        Args:
            profile: Profile with ``profile_id`` normally set to ``None``.

        Returns:
            Stored profile including its new identifier.

        Raises:
            sqlite3.IntegrityError: If the display name already exists.

        Example:
            >>> db = NovaFitDatabase(Path('data/example.db'))
            >>> db.initialize(); db.create_profile(UserProfile.build('Guest')).display_name
            'Guest'
        """
        self.initialize()
        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO profiles(
                    display_name, avatar, language, theme, step_goal,
                    water_goal_l, calorie_goal, activity_level, sport_focus
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                self._profile_parameters(profile),
            )
            connection.commit()
            profile_id = int(cursor.lastrowid)
        stored = self.get_profile(profile_id)
        if stored is None:  # Defensive programmer-error guard.
            raise RuntimeError("Profile insertion succeeded but could not be read back.")
        return stored

    def update_profile(self, profile: UserProfile) -> UserProfile:
        """Update an existing profile and its recommendation preferences.

        Args:
            profile: Validated profile with an identifier.

        Returns:
            Updated profile.

        Raises:
            ValueError: If no profile identifier is supplied or found.
            sqlite3.IntegrityError: If the name conflicts with another profile.

        Example:
            >>> db = NovaFitDatabase(Path('data/example.db'))
            >>> db.initialize(); p = db.get_profile(1)
            >>> db.update_profile(UserProfile.build('Primary User', profile_id=p.profile_id)).profile_id
            1
        """
        if profile.profile_id is None:
            raise ValueError("Profile id is required for update.")
        self.initialize()
        with self.connect() as connection:
            cursor = connection.execute(
                """
                UPDATE profiles SET
                    display_name = ?, avatar = ?, language = ?, theme = ?,
                    step_goal = ?, water_goal_l = ?, calorie_goal = ?,
                    activity_level = ?, sport_focus = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (*self._profile_parameters(profile), profile.profile_id),
            )
            connection.commit()
        if cursor.rowcount == 0:
            raise ValueError(f"Profile {profile.profile_id} does not exist.")
        updated = self.get_profile(profile.profile_id)
        if updated is None:
            raise RuntimeError("Updated profile could not be read back.")
        return updated

    def delete_profile(self, profile_id: int) -> bool:
        """Delete a non-primary profile and its entries.

        Args:
            profile_id: Profile identifier to delete.

        Returns:
            ``True`` when deleted.

        Raises:
            ValueError: If attempting to delete the protected primary profile.

        Example:
            >>> db = NovaFitDatabase(Path('data/example.db'))
            >>> db.initialize(); db.delete_profile(999)
            False
        """
        if profile_id == 1:
            raise ValueError("The primary profile cannot be deleted; rename it instead.")
        self.initialize()
        with self.connect() as connection:
            cursor = connection.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
            connection.commit()
        if self.active_profile_id == profile_id:
            self.active_profile_id = 1
        return cursor.rowcount > 0

    def upsert(self, entry: HealthEntry, profile_id: int | None = None) -> None:
        """Insert a day or update its measurements for one profile.

        Args:
            entry: Validated health record.
            profile_id: Optional profile override.

        Returns:
            None.

        Raises:
            sqlite3.Error: If the transaction fails.
            ValueError: If the profile does not exist.

        Example:
            >>> db = NovaFitDatabase(Path('data/example.db'))
            >>> db.initialize(); db.upsert(HealthEntry.build('2026-07-15', 1, 1))
        """
        user_id = self._resolve_profile_id(profile_id)
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO logs(user_id, date, steps, water_l, calories, mood, note)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id, date) DO UPDATE SET
                    steps = excluded.steps,
                    water_l = excluded.water_l,
                    calories = excluded.calories,
                    mood = excluded.mood,
                    note = excluded.note,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (
                    user_id,
                    entry.entry_date.isoformat(),
                    entry.steps,
                    entry.water_l,
                    entry.calories,
                    entry.mood,
                    entry.note,
                ),
            )
            connection.commit()

    def insert_if_missing(self, entry: HealthEntry, profile_id: int | None = None) -> bool:
        """Insert an entry only when its profile/date pair is new.

        Args:
            entry: Validated health record.
            profile_id: Optional profile override.

        Returns:
            ``True`` when inserted, otherwise ``False``.

        Example:
            >>> db = NovaFitDatabase(Path('data/example.db'))
            >>> db.initialize(); isinstance(db.insert_if_missing(HealthEntry.build('2026-07-15', 1, 1)), bool)
            True
        """
        user_id = self._resolve_profile_id(profile_id)
        with self.connect() as connection:
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO logs(user_id, date, steps, water_l, calories, mood, note)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    entry.entry_date.isoformat(),
                    entry.steps,
                    entry.water_l,
                    entry.calories,
                    entry.mood,
                    entry.note,
                ),
            )
            connection.commit()
            return cursor.rowcount > 0

    def get(self, entry_date: str | date, profile_id: int | None = None) -> HealthEntry | None:
        """Return one record by profile and date.

        Args:
            entry_date: ISO text or date object.
            profile_id: Optional profile override.

        Returns:
            Matching entry or ``None``.

        Example:
            >>> NovaFitDatabase(Path('data/example.db')).get('2026-07-15') is None
            True
        """
        normalized = HealthEntry.build(entry_date, 0, 0).entry_date.isoformat()
        user_id = self._resolve_profile_id(profile_id)
        with self.connect() as connection:
            row = connection.execute(
                """
                SELECT date, steps, water_l, calories, mood, note
                FROM logs WHERE user_id = ? AND date = ?
                """,
                (user_id, normalized),
            ).fetchone()
        return self._row_to_entry(row) if row else None

    def list(self, limit: int | None = 30, profile_id: int | None = None) -> list[HealthEntry]:
        """List entries for one profile from newest to oldest.

        Args:
            limit: Maximum rows, or ``None`` for all rows.
            profile_id: Optional profile override.

        Returns:
            Health entries ordered by date descending.

        Raises:
            ValueError: If a supplied limit is not positive.

        Example:
            >>> isinstance(NovaFitDatabase(Path('data/example.db')).list(5), list)
            True
        """
        user_id = self._resolve_profile_id(profile_id)
        if limit is not None and limit <= 0:
            raise ValueError("Limit must be greater than zero.")
        query = (
            "SELECT date, steps, water_l, calories, mood, note "
            "FROM logs WHERE user_id = ? ORDER BY date DESC"
        )
        parameters: Sequence[Any] = (user_id,)
        if limit is not None:
            query += " LIMIT ?"
            parameters = (user_id, limit)
        with self.connect() as connection:
            rows = connection.execute(query, parameters).fetchall()
        return [self._row_to_entry(row) for row in rows]

    def search(
        self,
        start_date: str | date,
        end_date: str | date,
        profile_id: int | None = None,
    ) -> list[HealthEntry]:
        """Return profile records inside an inclusive date range.

        Args:
            start_date: Inclusive lower ISO date.
            end_date: Inclusive upper ISO date.
            profile_id: Optional profile override.

        Returns:
            Matching entries from newest to oldest.

        Raises:
            ValueError: If dates are invalid or reversed.

        Example:
            >>> isinstance(NovaFitDatabase(Path('data/example.db')).search('2026-07-01', '2026-07-31'), list)
            True
        """
        start = HealthEntry.build(start_date, 0, 0).entry_date
        end = HealthEntry.build(end_date, 0, 0).entry_date
        if start > end:
            raise ValueError("Start date cannot be after end date.")
        user_id = self._resolve_profile_id(profile_id)
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT date, steps, water_l, calories, mood, note
                FROM logs
                WHERE user_id = ? AND date BETWEEN ? AND ?
                ORDER BY date DESC
                """,
                (user_id, start.isoformat(), end.isoformat()),
            ).fetchall()
        return [self._row_to_entry(row) for row in rows]

    def delete(self, entry_date: str | date, profile_id: int | None = None) -> bool:
        """Delete one profile record by date.

        Args:
            entry_date: ISO text or date object.
            profile_id: Optional profile override.

        Returns:
            ``True`` when a record was removed.

        Example:
            >>> isinstance(NovaFitDatabase(Path('data/example.db')).delete('2026-07-15'), bool)
            True
        """
        normalized = HealthEntry.build(entry_date, 0, 0).entry_date.isoformat()
        user_id = self._resolve_profile_id(profile_id)
        with self.connect() as connection:
            cursor = connection.execute(
                "DELETE FROM logs WHERE user_id = ? AND date = ?",
                (user_id, normalized),
            )
            connection.commit()
            return cursor.rowcount > 0

    def clear(self, profile_id: int | None = None) -> int:
        """Remove all records for one profile while preserving other users.

        Args:
            profile_id: Optional profile override.

        Returns:
            Number of deleted records.

        Example:
            >>> isinstance(NovaFitDatabase(Path('data/example.db')).clear(), int)
            True
        """
        user_id = self._resolve_profile_id(profile_id)
        with self.connect() as connection:
            cursor = connection.execute("DELETE FROM logs WHERE user_id = ?", (user_id,))
            connection.commit()
            return cursor.rowcount

    def count(self, profile_id: int | None = None) -> int:
        """Return the record count for one profile.

        Args:
            profile_id: Optional profile override.

        Returns:
            Profile row count.

        Example:
            >>> isinstance(NovaFitDatabase(Path('data/example.db')).count(), int)
            True
        """
        user_id = self._resolve_profile_id(profile_id)
        with self.connect() as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS total FROM logs WHERE user_id = ?",
                (user_id,),
            ).fetchone()
        return int(row["total"])

    def _resolve_profile_id(self, profile_id: int | None) -> int:
        self.initialize()
        selected = profile_id if profile_id is not None else self.active_profile_id
        if self.get_profile(selected) is None:
            raise ValueError(f"Profile {selected} does not exist.")
        return selected

    @staticmethod
    def _profile_parameters(profile: UserProfile) -> tuple[Any, ...]:
        return (
            profile.display_name,
            profile.avatar,
            profile.language,
            profile.theme,
            profile.step_goal,
            profile.water_goal_l,
            profile.calorie_goal,
            profile.activity_level,
            profile.sport_focus,
        )

    @staticmethod
    def _row_to_profile(row: sqlite3.Row) -> UserProfile:
        return UserProfile.build(
            row["display_name"],
            profile_id=int(row["id"]),
            avatar=row["avatar"],
            language=row["language"],
            theme=row["theme"],
            step_goal=row["step_goal"],
            water_goal_l=row["water_goal_l"],
            calorie_goal=row["calorie_goal"],
            activity_level=row["activity_level"],
            sport_focus=row["sport_focus"],
        )

    @staticmethod
    def _row_to_entry(row: sqlite3.Row) -> HealthEntry:
        return HealthEntry.build(
            row["date"],
            row["steps"],
            row["water_l"],
            row["calories"],
            row["mood"],
            row["note"],
        )

    @staticmethod
    def _table_exists(connection: sqlite3.Connection, table: str) -> bool:
        row = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?",
            (table,),
        ).fetchone()
        return row is not None

    @staticmethod
    def _column_names(connection: sqlite3.Connection, table: str) -> set[str]:
        return {row["name"] for row in connection.execute(f"PRAGMA table_info({table})")}

    def _create_profile_tables(self, connection: sqlite3.Connection) -> None:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                display_name TEXT NOT NULL UNIQUE COLLATE NOCASE,
                avatar TEXT NOT NULL DEFAULT 'nova',
                language TEXT NOT NULL DEFAULT 'en',
                theme TEXT NOT NULL DEFAULT 'aurora',
                step_goal INTEGER NOT NULL DEFAULT 10000 CHECK(step_goal > 0),
                water_goal_l REAL NOT NULL DEFAULT 2.0 CHECK(water_goal_l > 0),
                calorie_goal INTEGER NOT NULL DEFAULT 2000 CHECK(calorie_goal > 0),
                activity_level TEXT NOT NULL DEFAULT 'balanced',
                sport_focus TEXT NOT NULL DEFAULT 'mixed',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS app_meta (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """
        )

    @staticmethod
    def _ensure_default_profile(connection: sqlite3.Connection) -> None:
        connection.execute(
            """
            INSERT OR IGNORE INTO profiles(
                id, display_name, avatar, language, theme, step_goal,
                water_goal_l, calorie_goal, activity_level, sport_focus
            ) VALUES (1, ?, 'nova', 'en', 'aurora', 10000, 2.0, 2000, 'balanced', 'mixed')
            """,
            (DEFAULT_PROFILE_NAME,),
        )

    @staticmethod
    def _create_logs_table(connection: sqlite3.Connection) -> None:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL DEFAULT 1 REFERENCES profiles(id) ON DELETE CASCADE,
                date TEXT NOT NULL,
                steps INTEGER NOT NULL DEFAULT 0 CHECK (steps >= 0),
                water_l REAL NOT NULL DEFAULT 0 CHECK (water_l >= 0),
                calories INTEGER CHECK (calories IS NULL OR calories >= 0),
                mood TEXT,
                note TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, date)
            )
            """
        )

    def _rebuild_legacy_logs(self, connection: sqlite3.Connection) -> None:
        LOGGER.info("Migrating legacy single-user logs to profile-aware schema")
        legacy_name = "logs_legacy_v2"
        connection.execute("DROP TABLE IF EXISTS logs_legacy_v2")
        connection.execute("DROP INDEX IF EXISTS idx_logs_date")
        connection.execute(f"ALTER TABLE logs RENAME TO {legacy_name}")
        self._create_logs_table(connection)
        columns = self._column_names(connection, legacy_name)
        note_expr = "note" if "note" in columns else "NULL"
        created_expr = "COALESCE(created_at, CURRENT_TIMESTAMP)" if "created_at" in columns else "CURRENT_TIMESTAMP"
        updated_expr = "COALESCE(updated_at, CURRENT_TIMESTAMP)" if "updated_at" in columns else "CURRENT_TIMESTAMP"
        connection.execute(
            f"""
            INSERT INTO logs(user_id, date, steps, water_l, calories, mood, note, created_at, updated_at)
            SELECT 1, date, COALESCE(steps, 0), COALESCE(water_l, 0), calories,
                   mood, {note_expr}, {created_expr}, {updated_expr}
            FROM {legacy_name}
            """
        )
        connection.execute(f"DROP TABLE {legacy_name}")

    def _migrate_log_columns(self, connection: sqlite3.Connection) -> None:
        columns = self._column_names(connection, "logs")
        additions = {
            "note": "TEXT",
            "created_at": "TEXT",
            "updated_at": "TEXT",
        }
        for name, definition in additions.items():
            if name in columns:
                continue
            LOGGER.info("Adding legacy-compatible column: %s", name)
            connection.execute(f"ALTER TABLE logs ADD COLUMN {name} {definition}")
        connection.execute("UPDATE logs SET created_at = COALESCE(created_at, CURRENT_TIMESTAMP)")
        connection.execute("UPDATE logs SET updated_at = COALESCE(updated_at, CURRENT_TIMESTAMP)")

    @staticmethod
    def _create_indexes(connection: sqlite3.Connection) -> None:
        connection.executescript(
            """
            CREATE INDEX IF NOT EXISTS idx_logs_user_date ON logs(user_id, date DESC);
            CREATE INDEX IF NOT EXISTS idx_profiles_name ON profiles(display_name COLLATE NOCASE);
            """
        )
