from __future__ import annotations

from db_backup_utility.models.backup_config import BackupConfig
from db_backup_utility.models.backup_metadata import BackupMetadata
from db_backup_utility.models.backup_result import BackupResult
from db_backup_utility.models.restore_config import RestoreConfig
from db_backup_utility.models.restore_result import RestoreResult
from db_backup_utility.services.backup_service import BackupService
from db_backup_utility.services.connection_test_service import ConnectionTestService
from db_backup_utility.services.restore_service import RestoreService
from db_backup_utility.services.scheduler_service import SchedulerService
from db_backup_utility.services.storage_service import StorageService


class BackupFacade:
    def __init__(
        self,
        backup_service: BackupService,
        restore_service: RestoreService,
        connection_test_service: ConnectionTestService,
        storage_service: StorageService,
        scheduler_service: SchedulerService,
    ) -> None:
        self.backup_service = backup_service
        self.restore_service = restore_service
        self.connection_test_service = connection_test_service
        self.storage_service = storage_service
        self.scheduler_service = scheduler_service

    def run_backup(self, config: BackupConfig) -> BackupResult:
        return self.backup_service.create_backup(config)

    def run_restore(self, config: RestoreConfig) -> RestoreResult:
        return self.restore_service.restore_backup(config)

    def test_connection(self, config: BackupConfig) -> bool:
        return self.connection_test_service.test_connection(config)

    def list_backups(self, config: BackupConfig) -> list[BackupMetadata]:
        return self.storage_service.list_backups(config)

    def schedule_backup(self, config: BackupConfig) -> str:
        return self.scheduler_service.schedule(config)

