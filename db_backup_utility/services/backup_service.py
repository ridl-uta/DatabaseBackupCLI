from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import time
import uuid

from db_backup_utility.exceptions.backup_exception import BackupException
from db_backup_utility.factories.backup_strategy_factory import BackupStrategyFactory
from db_backup_utility.models.backup_config import BackupConfig
from db_backup_utility.models.backup_event import BackupEvent
from db_backup_utility.models.backup_result import BackupResult
from db_backup_utility.observers.backup_event_publisher import BackupEventPublisher
from db_backup_utility.services.compression_service import CompressionService
from db_backup_utility.services.storage_service import StorageService


class BackupService:
    def __init__(
        self,
        strategy_factory: BackupStrategyFactory,
        compression_service: CompressionService,
        storage_service: StorageService,
        event_publisher: BackupEventPublisher,
    ) -> None:
        self.strategy_factory = strategy_factory
        self.compression_service = compression_service
        self.storage_service = storage_service
        self.event_publisher = event_publisher

    def create_backup(self, config: BackupConfig) -> BackupResult:
        backup_id = str(uuid.uuid4())
        start = datetime.now(timezone.utc)
        start_monotonic = time.monotonic()
        self._publish("BACKUP_STARTED", "running", "Backup started.", {"backup_id": backup_id})

        try:
            strategy = self.strategy_factory.create(config.db_type)
            strategy.test_connection(config)
            raw_backup_path = strategy.backup(config)
            compressed_path = self.compression_service.compress(
                raw_backup_path,
                config.compression_type,
            )
            if compressed_path != raw_backup_path:
                Path(raw_backup_path).unlink(missing_ok=True)
            storage_result = self.storage_service.store(compressed_path, config)

            end = datetime.now(timezone.utc)
            result = BackupResult(
                backup_id=backup_id,
                status="success",
                backup_file_path=raw_backup_path,
                compressed_file_path=compressed_path,
                storage_location=storage_result.location,
                start_time=start,
                end_time=end,
                duration_seconds=time.monotonic() - start_monotonic,
            )
            self._publish(
                "BACKUP_SUCCESS",
                "success",
                "Backup completed.",
                {"backup_id": backup_id, "location": storage_result.location},
            )
            return result
        except Exception as exc:
            end = datetime.now(timezone.utc)
            self._publish(
                "BACKUP_FAILED",
                "failed",
                "Backup failed.",
                {"backup_id": backup_id},
                error=str(exc),
            )
            return BackupResult(
                backup_id=backup_id,
                status="failed",
                backup_file_path=None,
                compressed_file_path=None,
                storage_location=None,
                start_time=start,
                end_time=end,
                duration_seconds=time.monotonic() - start_monotonic,
                error_message=str(exc),
            )

    def _publish(
        self,
        event_type: str,
        status: str,
        message: str,
        metadata: dict[str, str],
        error: str | None = None,
    ) -> None:
        self.event_publisher.notify(
            BackupEvent(
                event_type=event_type,
                status=status,
                message=message,
                timestamp=datetime.now(timezone.utc),
                metadata=metadata,
                error=error,
            )
        )

