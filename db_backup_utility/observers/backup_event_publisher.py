from __future__ import annotations

from db_backup_utility.models.backup_event import BackupEvent
from db_backup_utility.observers.backup_observer import BackupObserver


class BackupEventPublisher:
    def __init__(self) -> None:
        self.observers: list[BackupObserver] = []

    def subscribe(self, observer: BackupObserver) -> None:
        self.observers.append(observer)

    def unsubscribe(self, observer: BackupObserver) -> None:
        self.observers.remove(observer)

    def notify(self, event: BackupEvent) -> None:
        for observer in self.observers:
            observer.update(event)

