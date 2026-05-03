from __future__ import annotations

import os

from db_backup_utility.adapters.slack_adapter import SlackAdapter


class NotificationAdapterFactory:
    def create_slack_adapter(self) -> SlackAdapter:
        return SlackAdapter(webhook_url=os.getenv("SLACK_WEBHOOK_URL"))

