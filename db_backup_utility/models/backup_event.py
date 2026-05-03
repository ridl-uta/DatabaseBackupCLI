from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class BackupEvent:
    event_type: str
    status: str
    message: str
    timestamp: datetime
    metadata: dict[str, Any] | None = None
    error: str | None = None

