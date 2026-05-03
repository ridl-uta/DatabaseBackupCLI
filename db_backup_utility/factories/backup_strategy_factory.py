from __future__ import annotations

from db_backup_utility.exceptions.configuration_exception import ConfigurationException
from db_backup_utility.strategies.database_backup_strategy import DatabaseBackupStrategy
from db_backup_utility.strategies.mongodb_backup_strategy import MongoDBBackupStrategy
from db_backup_utility.strategies.mysql_backup_strategy import MySQLBackupStrategy
from db_backup_utility.strategies.postgresql_backup_strategy import PostgreSQLBackupStrategy
from db_backup_utility.strategies.sqlite_backup_strategy import SQLiteBackupStrategy


class BackupStrategyFactory:
    def __init__(self) -> None:
        mysql = MySQLBackupStrategy()
        postgres = PostgreSQLBackupStrategy()
        mongo = MongoDBBackupStrategy()
        sqlite = SQLiteBackupStrategy()
        self._strategies: dict[str, DatabaseBackupStrategy] = {
            "mysql": mysql,
            "postgres": postgres,
            "postgresql": postgres,
            "mongodb": mongo,
            "mongo": mongo,
            "sqlite": sqlite,
        }

    def create(self, db_type: str) -> DatabaseBackupStrategy:
        try:
            return self._strategies[db_type.lower()]
        except KeyError as exc:
            raise ConfigurationException(f"Unsupported database type: {db_type}") from exc

