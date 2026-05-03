from datetime import datetime, timezone
from pathlib import Path

import pytest

from db_backup_utility.adapters.s3_storage_adapter import S3StorageAdapter
from db_backup_utility.exceptions.storage_exception import StorageException
from db_backup_utility.models.backup_config import BackupConfig
from db_backup_utility.models.restore_config import RestoreConfig


class FakeS3Client:
    def __init__(self):
        self.uploads = []
        self.downloads = []
        self.deleted = []

    def upload_file(self, source, bucket, key):
        self.uploads.append((source, bucket, key))

    def download_file(self, bucket, key, destination):
        self.downloads.append((bucket, key, destination))
        Path(destination).write_text("downloaded", encoding="utf-8")

    def list_objects_v2(self, Bucket, Prefix):
        return {
            "Contents": [
                {
                    "Key": f"{Prefix}/app.sqlite.gz" if Prefix else "app.sqlite.gz",
                    "Size": 123,
                    "LastModified": datetime(2026, 1, 1, tzinfo=timezone.utc),
                }
            ]
        }

    def delete_object(self, Bucket, Key):
        self.deleted.append((Bucket, Key))


def test_s3_store_uploads_file_with_prefix(monkeypatch, tmp_path):
    client = FakeS3Client()
    monkeypatch.setattr(S3StorageAdapter, "_client", staticmethod(lambda: client))
    source = tmp_path / "app.sqlite.gz"
    source.write_text("backup", encoding="utf-8")
    config = BackupConfig(
        db_type="sqlite",
        database_name="app.db",
        storage_type="s3",
        cloud_bucket="bucket",
        cloud_prefix="database-backups",
    )

    result = S3StorageAdapter().store(str(source), config)

    assert client.uploads == [(str(source.resolve()), "bucket", "database-backups/app.sqlite.gz")]
    assert result.location == "s3://bucket/database-backups/app.sqlite.gz"


def test_s3_store_requires_bucket(tmp_path):
    source = tmp_path / "app.sqlite.gz"
    source.write_text("backup", encoding="utf-8")
    config = BackupConfig(db_type="sqlite", database_name="app.db", storage_type="s3")

    with pytest.raises(StorageException, match="cloud-bucket"):
        S3StorageAdapter().store(str(source), config)


def test_s3_retrieve_downloads_uri(monkeypatch, tmp_path):
    client = FakeS3Client()
    monkeypatch.setattr(S3StorageAdapter, "_client", staticmethod(lambda: client))
    config = RestoreConfig(
        db_type="sqlite",
        target_database_name="restored.db",
        storage_type="s3",
        output_path=str(tmp_path),
    )

    path = S3StorageAdapter().retrieve("s3://bucket/database-backups/app.sqlite.gz", config)

    assert client.downloads == [
        ("bucket", "database-backups/app.sqlite.gz", str(tmp_path / "app.sqlite.gz"))
    ]
    assert Path(path).exists()


def test_s3_list_returns_metadata(monkeypatch):
    monkeypatch.setattr(S3StorageAdapter, "_client", staticmethod(lambda: FakeS3Client()))
    config = BackupConfig(
        db_type="sqlite",
        database_name="app.db",
        storage_type="s3",
        cloud_bucket="bucket",
        cloud_prefix="database-backups",
    )

    backups = S3StorageAdapter().list(config)

    assert len(backups) == 1
    assert backups[0].storage_location == "s3://bucket/database-backups/app.sqlite.gz"
    assert backups[0].size_bytes == 123


def test_s3_delete_removes_object(monkeypatch):
    client = FakeS3Client()
    monkeypatch.setattr(S3StorageAdapter, "_client", staticmethod(lambda: client))
    config = BackupConfig(
        db_type="sqlite",
        database_name="app.db",
        storage_type="s3",
        cloud_bucket="bucket",
    )

    deleted = S3StorageAdapter().delete("database-backups/app.sqlite.gz", config)

    assert deleted is True
    assert client.deleted == [("bucket", "database-backups/app.sqlite.gz")]
