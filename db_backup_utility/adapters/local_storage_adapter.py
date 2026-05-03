from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import shutil

from db_backup_utility.adapters.storage_adapter import StorageAdapter
from db_backup_utility.exceptions.storage_exception import StorageException
from db_backup_utility.models.backup_config import BackupConfig
from db_backup_utility.models.backup_metadata import BackupMetadata
from db_backup_utility.models.restore_config import RestoreConfig
from db_backup_utility.models.storage_result import StorageResult


class LocalStorageAdapter(StorageAdapter):
    def store(self, file_path: str, config: BackupConfig) -> StorageResult:
        source = Path(file_path).expanduser().resolve()
        if not source.exists():
            raise StorageException(f"Backup file does not exist: {source}")

        destination_dir = Path(config.output_path).expanduser().resolve()
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = destination_dir / source.name

        if source != destination:
            shutil.copy2(source, destination)

        return StorageResult(status="success", location=str(destination), file_name=destination.name)

    def retrieve(self, file_name: str, config: RestoreConfig) -> str:
        path = Path(file_name).expanduser()
        if not path.is_absolute():
            path = Path(config.backup_file_path).expanduser()
        path = path.resolve()
        if not path.exists():
            raise StorageException(f"Backup file does not exist: {path}")
        return str(path)

    def list(self, config: BackupConfig) -> list[BackupMetadata]:
        directory = Path(config.output_path).expanduser().resolve()
        if not directory.exists():
            return []

        metadata: list[BackupMetadata] = []
        for path in sorted(directory.iterdir()):
            if not path.is_file():
                continue
            stat = path.stat()
            metadata.append(
                BackupMetadata(
                    backup_id=path.stem,
                    database_name=config.database_name or "-",
                    db_type=config.db_type,
                    backup_type=config.backup_type,
                    file_name=path.name,
                    storage_location=str(path),
                    created_at=datetime.fromtimestamp(stat.st_mtime, timezone.utc),
                    size_bytes=stat.st_size,
                )
            )
        return metadata

    def delete(self, file_name: str, config: BackupConfig) -> bool:
        path = Path(config.output_path).expanduser().resolve() / file_name
        if not path.exists():
            return False
        path.unlink()
        return True

