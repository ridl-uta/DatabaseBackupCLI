from __future__ import annotations

from datetime import datetime, timezone

from db_backup_utility.factories.restore_strategy_factory import RestoreStrategyFactory
from db_backup_utility.models.backup_event import BackupEvent
from db_backup_utility.models.restore_config import RestoreConfig
from db_backup_utility.models.restore_result import RestoreResult
from db_backup_utility.observers.backup_event_publisher import BackupEventPublisher
from db_backup_utility.services.compression_service import CompressionService
from db_backup_utility.services.storage_service import StorageService


class RestoreService:
    def __init__(
        self,
        restore_strategy_factory: RestoreStrategyFactory,
        storage_service: StorageService,
        compression_service: CompressionService,
        event_publisher: BackupEventPublisher,
    ) -> None:
        self.restore_strategy_factory = restore_strategy_factory
        self.storage_service = storage_service
        self.compression_service = compression_service
        self.event_publisher = event_publisher

    def restore_backup(self, config: RestoreConfig) -> RestoreResult:
        self._publish("RESTORE_STARTED", "running", "Restore started.")
        try:
            stored_file = self.storage_service.retrieve(config.backup_file_path, config)
            raw_backup = self.compression_service.decompress(stored_file)
            strategy = self.restore_strategy_factory.create(config.db_type)
            result = strategy.restore(config, raw_backup)
            self._publish("RESTORE_SUCCESS", "success", "Restore completed.")
            return result
        except Exception as exc:
            self._publish("RESTORE_FAILED", "failed", "Restore failed.", error=str(exc))
            now = datetime.now(timezone.utc)
            return RestoreResult(
                status="failed",
                restored_database=config.target_database_name,
                start_time=now,
                end_time=now,
                duration_seconds=0,
                error_message=str(exc),
            )

    def _publish(
        self,
        event_type: str,
        status: str,
        message: str,
        error: str | None = None,
    ) -> None:
        self.event_publisher.notify(
            BackupEvent(
                event_type=event_type,
                status=status,
                message=message,
                timestamp=datetime.now(timezone.utc),
                error=error,
            )
        )

