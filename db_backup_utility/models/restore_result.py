from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RestoreResult:
    status: str
    restored_database: str
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    error_message: str | None = None

