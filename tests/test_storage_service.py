from pathlib import Path

from db_backup_utility.factories.storage_adapter_factory import StorageAdapterFactory
from db_backup_utility.models.backup_config import BackupConfig
from db_backup_utility.services.storage_service import StorageService


def test_storage_service_stores_local_file(tmp_path):
    source = tmp_path / "backup.sqlite.gz"
    source.write_text("backup", encoding="utf-8")
    output = tmp_path / "stored"
    config = BackupConfig(db_type="sqlite", database_name="app.db", output_path=str(output))

    result = StorageService(StorageAdapterFactory()).store(str(source), config)

    assert result.status == "success"
    assert Path(result.location).exists()

