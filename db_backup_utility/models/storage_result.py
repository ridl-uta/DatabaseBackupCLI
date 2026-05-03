from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StorageResult:
    status: str
    location: str
    file_name: str
    error_message: str | None = None

