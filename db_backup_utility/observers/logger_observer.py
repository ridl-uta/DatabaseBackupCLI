from __future__ import annotations

from db_backup_utility.models.backup_event import BackupEvent
from db_backup_utility.observers.backup_observer import BackupObserver
from db_backup_utility.services.logging_service import get_logger


class LoggerObserver(BackupObserver):
    def update(self, event: BackupEvent) -> None:
        logger = get_logger()
        message = f"{event.event_type} {event.status}: {event.message}"
        if event.error:
            logger.error("%s error=%s metadata=%s", message, event.error, event.metadata)
        else:
            logger.info("%s metadata=%s", message, event.metadata)

