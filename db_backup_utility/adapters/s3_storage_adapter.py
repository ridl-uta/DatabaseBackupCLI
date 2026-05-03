from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from db_backup_utility.adapters.storage_adapter import StorageAdapter
from db_backup_utility.exceptions.storage_exception import StorageException
from db_backup_utility.models.backup_config import BackupConfig
from db_backup_utility.models.backup_metadata import BackupMetadata
from db_backup_utility.models.restore_config import RestoreConfig
from db_backup_utility.models.storage_result import StorageResult


class S3StorageAdapter(StorageAdapter):
    def store(self, file_path: str, config: BackupConfig) -> StorageResult:
        source = Path(file_path).expanduser().resolve()
        if not source.exists():
            raise StorageException(f"Backup file does not exist: {source}")
        if not config.cloud_bucket:
            raise StorageException("--cloud-bucket is required for S3 storage.")

        key = self._build_key(source.name, config.cloud_prefix)
        self._client().upload_file(str(source), config.cloud_bucket, key)

        return StorageResult(
            status="success",
            location=f"s3://{config.cloud_bucket}/{key}",
            file_name=source.name,
        )

    def retrieve(self, file_name: str, config: RestoreConfig) -> str:
        bucket, key = self._resolve_bucket_and_key(
            file_name,
            config.cloud_bucket,
            config.cloud_prefix,
        )
        download_dir = Path(config.output_path).expanduser().resolve()
        download_dir.mkdir(parents=True, exist_ok=True)
        destination = download_dir / Path(key).name

        self._client().download_file(bucket, key, str(destination))
        return str(destination)

    def list(self, config: BackupConfig) -> list[BackupMetadata]:
        if not config.cloud_bucket:
            raise StorageException("--cloud-bucket is required for S3 storage.")

        prefix = self._clean_prefix(config.cloud_prefix)
        response = self._client().list_objects_v2(
            Bucket=config.cloud_bucket,
            Prefix=prefix,
        )

        backups: list[BackupMetadata] = []
        for item in response.get("Contents", []):
            key = item["Key"]
            last_modified = item.get("LastModified")
            if last_modified is None:
                last_modified = datetime.now(timezone.utc)
            backups.append(
                BackupMetadata(
                    backup_id=Path(key).stem,
                    database_name=config.database_name or "-",
                    db_type=config.db_type,
                    backup_type=config.backup_type,
                    file_name=Path(key).name,
                    storage_location=f"s3://{config.cloud_bucket}/{key}",
                    created_at=last_modified,
                    size_bytes=item.get("Size", 0),
                )
            )
        return backups

    def delete(self, file_name: str, config: BackupConfig) -> bool:
        bucket, key = self._resolve_bucket_and_key(
            file_name,
            config.cloud_bucket,
            config.cloud_prefix,
        )
        self._client().delete_object(Bucket=bucket, Key=key)
        return True

    @staticmethod
    def _client():
        try:
            import boto3
        except ImportError as exc:
            raise StorageException("Install AWS S3 support with: pip install boto3") from exc
        return boto3.client("s3")

    @staticmethod
    def _build_key(file_name: str, prefix: str = "") -> str:
        clean_prefix = S3StorageAdapter._clean_prefix(prefix)
        if not clean_prefix:
            return file_name
        return f"{clean_prefix}/{file_name}"

    @staticmethod
    def _clean_prefix(prefix: str = "") -> str:
        return prefix.strip("/")

    @staticmethod
    def _resolve_bucket_and_key(
        file_name: str,
        cloud_bucket: str | None,
        cloud_prefix: str = "",
    ) -> tuple[str, str]:
        parsed = urlparse(file_name)
        if parsed.scheme == "s3":
            bucket = parsed.netloc
            key = parsed.path.lstrip("/")
        else:
            if not cloud_bucket:
                raise StorageException(
                    "--cloud-bucket is required when backup file is not an s3:// URI."
                )
            bucket = cloud_bucket
            key = file_name.strip("/")
            if "/" not in key:
                key = S3StorageAdapter._build_key(file_name, cloud_prefix)

        if not bucket or not key:
            raise StorageException(f"Invalid S3 backup location: {file_name}")
        return bucket, key
