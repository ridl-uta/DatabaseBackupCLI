from __future__ import annotations

from abc import ABC, abstractmethod

from db_backup_utility.models.backup_config import BackupConfig
from db_backup_utility.models.backup_metadata import BackupMetadata
from db_backup_utility.models.restore_config import RestoreConfig
from db_backup_utility.models.storage_result import StorageResult


class StorageAdapter(ABC):
    @abstractmethod
    def store(self, file_path: str, config: BackupConfig) -> StorageResult:
        """Store a backup file."""

    @abstractmethod
    def retrieve(self, file_name: str, config: RestoreConfig) -> str:
        """Return a local path for a stored backup file."""

    @abstractmethod
    def list(self, config: BackupConfig) -> list[BackupMetadata]:
        """List known backup files."""

    @abstractmethod
    def delete(self, file_name: str, config: BackupConfig) -> bool:
        """Delete a backup file."""

