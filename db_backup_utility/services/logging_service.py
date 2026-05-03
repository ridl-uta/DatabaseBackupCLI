from __future__ import annotations

import logging
from pathlib import Path


def get_logger() -> logging.Logger:
    logger = logging.getLogger("db_backup_utility")
    if logger.handlers:
        return logger

    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_dir / "backup.log")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    return logger

