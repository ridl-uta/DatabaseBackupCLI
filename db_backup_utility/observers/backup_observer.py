from __future__ import annotations

from abc import ABC, abstractmethod

from db_backup_utility.models.backup_event import BackupEvent


class BackupObserver(ABC):
    @abstractmethod
    def update(self, event: BackupEvent) -> None:
        """React to a backup utility event."""

