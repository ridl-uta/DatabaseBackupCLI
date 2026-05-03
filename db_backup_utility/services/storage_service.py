from __future__ import annotations

from db_backup_utility.factories.storage_adapter_factory import StorageAdapterFactory
from db_backup_utility.models.backup_config import BackupConfig
from db_backup_utility.models.backup_metadata import BackupMetadata
from db_backup_utility.models.restore_config import RestoreConfig
from db_backup_utility.models.storage_result import StorageResult


class StorageService:
    def __init__(self, adapter_factory: StorageAdapterFactory) -> None:
        self.adapter_factory = adapter_factory

    def store(self, file_path: str, config: BackupConfig) -> StorageResult:
        adapter = self.adapter_factory.create(config.storage_type)
        return adapter.store(file_path, config)

    def retrieve(self, file_name: str, config: RestoreConfig) -> str:
        adapter = self.adapter_factory.create(config.storage_type)
        return adapter.retrieve(file_name, config)

    def list_backups(self, config: BackupConfig) -> list[BackupMetadata]:
        adapter = self.adapter_factory.create(config.storage_type)
        return adapter.list(config)

