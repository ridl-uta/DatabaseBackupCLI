from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BackupConfig:
    db_type: str
    host: str = "localhost"
    port: int = 0
    username: str = ""
    password: str = ""
    database_name: str = ""
    backup_type: str = "full"
    storage_type: str = "local"
    compression_type: str = "gzip"
    output_path: str = "./backups"
    cloud_bucket: str | None = None
    cloud_prefix: str = ""
    schedule_expression: str | None = None
    notification_enabled: bool = False
