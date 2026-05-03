from db_backup_utility.observers.backup_event_publisher import BackupEventPublisher
from db_backup_utility.observers.backup_observer import BackupObserver


class NotificationService:
    def __init__(self, event_publisher: BackupEventPublisher) -> None:
        self.event_publisher = event_publisher

    def subscribe(self, observer: BackupObserver) -> None:
        self.event_publisher.subscribe(observer)

