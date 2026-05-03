from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path

from db_backup_utility.models.backup_event import BackupEvent
from db_backup_utility.observers.backup_observer import BackupObserver


class HistoryRecorderObserver(BackupObserver):
    def __init__(self, history_path: str = "logs/history.jsonl") -> None:
        self.history_path = Path(history_path)

    def update(self, event: BackupEvent) -> None:
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        payload = asdict(event)
        payload["timestamp"] = event.timestamp.isoformat()
        with self.history_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(payload, sort_keys=True) + "\n")

