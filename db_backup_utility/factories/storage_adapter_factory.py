from __future__ import annotations

from db_backup_utility.adapters.azure_blob_storage_adapter import AzureBlobStorageAdapter
from db_backup_utility.adapters.google_cloud_storage_adapter import GoogleCloudStorageAdapter
from db_backup_utility.adapters.local_storage_adapter import LocalStorageAdapter
from db_backup_utility.adapters.s3_storage_adapter import S3StorageAdapter
from db_backup_utility.adapters.storage_adapter import StorageAdapter
from db_backup_utility.exceptions.configuration_exception import ConfigurationException


class StorageAdapterFactory:
    def __init__(self) -> None:
        local = LocalStorageAdapter()
        s3 = S3StorageAdapter()
        gcs = GoogleCloudStorageAdapter()
        azure = AzureBlobStorageAdapter()
        self._adapters: dict[str, StorageAdapter] = {
            "local": local,
            "s3": s3,
            "aws-s3": s3,
            "gcs": gcs,
            "google-cloud": gcs,
            "azure": azure,
            "azure-blob": azure,
        }

    def create(self, storage_type: str) -> StorageAdapter:
        try:
            return self._adapters[storage_type.lower()]
        except KeyError as exc:
            raise ConfigurationException(f"Unsupported storage type: {storage_type}") from exc

