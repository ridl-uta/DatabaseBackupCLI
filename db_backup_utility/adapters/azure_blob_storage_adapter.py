from __future__ import annotations

from db_backup_utility.adapters.storage_adapter import StorageAdapter
from db_backup_utility.exceptions.storage_exception import StorageException
from db_backup_utility.models.backup_config import BackupConfig
from db_backup_utility.models.backup_metadata import BackupMetadata
from db_backup_utility.models.restore_config import RestoreConfig
from db_backup_utility.models.storage_result import StorageResult


class AzureBlobStorageAdapter(StorageAdapter):
    """Scaffold placeholder for Azure Blob Storage support."""

    def store(self, file_path: str, config: BackupConfig) -> StorageResult:
        raise StorageException("Azure Blob Storage adapter is not implemented yet.")

    def retrieve(self, file_name: str, config: RestoreConfig) -> str:
        raise StorageException("Azure Blob Storage adapter is not implemented yet.")

    def list(self, config: BackupConfig) -> list[BackupMetadata]:
        raise StorageException("Azure Blob Storage adapter is not implemented yet.")

    def delete(self, file_name: str, config: BackupConfig) -> bool:
        raise StorageException("Azure Blob Storage adapter is not implemented yet.")
