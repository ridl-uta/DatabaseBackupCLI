from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class BackupMetadata:
    backup_id: str
    database_name: str
    db_type: str
    backup_type: str
    file_name: str
    storage_location: str
    created_at: datetime
    size_bytes: int

