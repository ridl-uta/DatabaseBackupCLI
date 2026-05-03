import sqlite3
from pathlib import Path

from db_backup_utility.factories.backup_strategy_factory import BackupStrategyFactory
from db_backup_utility.factories.storage_adapter_factory import StorageAdapterFactory
from db_backup_utility.models.backup_config import BackupConfig
from db_backup_utility.observers.backup_event_publisher import BackupEventPublisher
from db_backup_utility.services.backup_service import BackupService
from db_backup_utility.services.compression_service import CompressionService
from db_backup_utility.services.storage_service import StorageService


def test_backup_service_creates_sqlite_backup(tmp_path):
    database = tmp_path / "app.db"
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE items (id INTEGER PRIMARY KEY)")

    config = BackupConfig(
        db_type="sqlite",
        database_name=str(database),
        output_path=str(tmp_path / "backups"),
    )
    service = BackupService(
        BackupStrategyFactory(),
        CompressionService(),
        StorageService(StorageAdapterFactory()),
        BackupEventPublisher(),
    )

    result = service.create_backup(config)

    assert result.status == "success"
    assert result.storage_location is not None
    assert Path(result.storage_location).exists()

