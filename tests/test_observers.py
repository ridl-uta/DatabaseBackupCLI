from datetime import datetime, timezone

from db_backup_utility.models.backup_event import BackupEvent
from db_backup_utility.observers.backup_event_publisher import BackupEventPublisher
from db_backup_utility.observers.backup_observer import BackupObserver


class RecordingObserver(BackupObserver):
    def __init__(self):
        self.events = []

    def update(self, event: BackupEvent) -> None:
        self.events.append(event)


def test_publisher_notifies_subscribers():
    publisher = BackupEventPublisher()
    observer = RecordingObserver()
    event = BackupEvent("BACKUP_STARTED", "running", "started", datetime.now(timezone.utc))

    publisher.subscribe(observer)
    publisher.notify(event)

    assert observer.events == [event]

