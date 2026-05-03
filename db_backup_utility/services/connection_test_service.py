from __future__ import annotations

from db_backup_utility.factories.backup_strategy_factory import BackupStrategyFactory
from db_backup_utility.models.backup_config import BackupConfig


class ConnectionTestService:
    def __init__(self, strategy_factory: BackupStrategyFactory) -> None:
        self.strategy_factory = strategy_factory

    def test_connection(self, config: BackupConfig) -> bool:
        strategy = self.strategy_factory.create(config.db_type)
        return strategy.test_connection(config)

