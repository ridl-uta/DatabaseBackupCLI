from db_backup_utility.exceptions.backup_exception import BackupException
from db_backup_utility.models.backup_config import BackupConfig
from db_backup_utility.models.restore_config import RestoreConfig
from db_backup_utility.models.restore_result import RestoreResult
from db_backup_utility.strategies.database_backup_strategy import DatabaseBackupStrategy


class PostgreSQLBackupStrategy(DatabaseBackupStrategy):
    def test_connection(self, config: BackupConfig | RestoreConfig) -> bool:
        raise BackupException("PostgreSQL support is scaffolded but not implemented yet.")

    def backup(self, config: BackupConfig) -> str:
        raise BackupException("PostgreSQL support is scaffolded but not implemented yet.")

    def restore(self, config: RestoreConfig, backup_file: str) -> RestoreResult:
        raise BackupException("PostgreSQL support is scaffolded but not implemented yet.")

