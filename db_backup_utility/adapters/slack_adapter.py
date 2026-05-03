from __future__ import annotations

import requests


class SlackAdapter:
    def __init__(self, webhook_url: str | None = None) -> None:
        self.webhook_url = webhook_url

    def send_message(self, message: str) -> None:
        if not self.webhook_url:
            return
        requests.post(self.webhook_url, json={"text": message}, timeout=10)

