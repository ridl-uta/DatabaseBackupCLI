from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class BackupResult:
    backup_id: str
    status: str
    backup_file_path: str | None
    compressed_file_path: str | None
    storage_location: str | None
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    error_message: str | None = None

