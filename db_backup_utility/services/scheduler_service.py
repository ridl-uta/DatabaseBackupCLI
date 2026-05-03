from __future__ import annotations

from db_backup_utility.models.backup_config import BackupConfig


class SchedulerService:
    def schedule(self, config: BackupConfig) -> str:
        if not config.schedule_expression:
            raise ValueError("Schedule expression is required.")
        return f"scheduled:{config.db_type}:{config.database_name}:{config.schedule_expression}"

    def remove_schedule(self, schedule_id: str) -> bool:
        return bool(schedule_id)

