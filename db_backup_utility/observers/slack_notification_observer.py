from __future__ import annotations

from db_backup_utility.adapters.slack_adapter import SlackAdapter
from db_backup_utility.models.backup_event import BackupEvent
from db_backup_utility.observers.backup_observer import BackupObserver


class SlackNotificationObserver(BackupObserver):
    def __init__(self, slack_adapter: SlackAdapter) -> None:
        self.slack_adapter = slack_adapter

    def update(self, event: BackupEvent) -> None:
        self.slack_adapter.send_message(f"{event.event_type} {event.status}: {event.message}")

