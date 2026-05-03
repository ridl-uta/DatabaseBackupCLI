from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from db_backup_utility.models.backup_config import BackupConfig
from db_backup_utility.models.restore_config import RestoreConfig
from db_backup_utility.models.restore_result import RestoreResult


class DatabaseBackupStrategy(ABC):
    @abstractmethod
    def test_connection(self, config: BackupConfig | RestoreConfig) -> bool:
        """Validate database connectivity."""

    @abstractmethod
    def backup(self, config: BackupConfig) -> str:
        """Create a raw database backup and return its path."""

    @abstractmethod
    def restore(self, config: RestoreConfig, backup_file: str) -> RestoreResult:
        """Restore a database from a raw backup file."""

    @staticmethod
    def _database_path(config: BackupConfig | RestoreConfig) -> Path:
        database = getattr(config, "database_name", "") or getattr(
            config, "target_database_name", ""
        )
        return Path(database).expanduser()

