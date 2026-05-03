from __future__ import annotations

import os

from dotenv import load_dotenv


class ConfigLoader:
    def __init__(self, env_file: str | None = None) -> None:
        load_dotenv(env_file)

    def get(self, key: str, default: str | None = None) -> str | None:
        return os.getenv(key, default)

