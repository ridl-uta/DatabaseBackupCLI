from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RestoreConfig:
    db_type: str
    host: str = "localhost"
    port: int = 0
    username: str = ""
    password: str = ""
    target_database_name: str = ""
    backup_file_path: str = ""
    storage_type: str = "local"
    output_path: str = "./backups"
    cloud_bucket: str | None = None
    cloud_prefix: str = ""
    selected_tables: list[str] | None = None
    overwrite_existing: bool = False
