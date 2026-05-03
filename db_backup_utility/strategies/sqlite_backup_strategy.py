from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import shutil
import sqlite3
import time

from db_backup_utility.exceptions.connection_exception import ConnectionException
from db_backup_utility.exceptions.restore_exception import RestoreException
from db_backup_utility.models.backup_config import BackupConfig
from db_backup_utility.models.restore_config import RestoreConfig
from db_backup_utility.models.restore_result import RestoreResult
from db_backup_utility.strategies.database_backup_strategy import DatabaseBackupStrategy


class SQLiteBackupStrategy(DatabaseBackupStrategy):
    def test_connection(self, config: BackupConfig | RestoreConfig) -> bool:
        database_path = self._database_path(config)
        if not database_path.exists():
            raise ConnectionException(f"SQLite database does not exist: {database_path}")
        uri = f"file:{database_path}?mode=ro"
        with sqlite3.connect(uri, uri=True) as connection:
            connection.execute("SELECT 1")
        return True

    def backup(self, config: BackupConfig) -> str:
        source = Path(config.database_name).expanduser().resolve()
        if not source.exists():
            raise ConnectionException(f"SQLite database does not exist: {source}")

        output_dir = Path(config.output_path).expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        destination = output_dir / f"{source.stem}_{timestamp}.sqlite"
        shutil.copy2(source, destination)
        return str(destination)

    def restore(self, config: RestoreConfig, backup_file: str) -> RestoreResult:
        start = datetime.now(timezone.utc)
        start_monotonic = time.monotonic()
        target = Path(config.target_database_name).expanduser().resolve()
        source = Path(backup_file).expanduser().resolve()

        if target.exists() and not config.overwrite_existing:
            raise RestoreException(
                f"Target database exists. Use --overwrite-existing to replace it: {target}"
            )

        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        end = datetime.now(timezone.utc)
        return RestoreResult(
            status="success",
            restored_database=str(target),
            start_time=start,
            end_time=end,
            duration_seconds=time.monotonic() - start_monotonic,
        )

