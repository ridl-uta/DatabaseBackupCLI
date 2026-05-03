from db_backup_utility.adapters.local_storage_adapter import LocalStorageAdapter
from db_backup_utility.factories.backup_strategy_factory import BackupStrategyFactory
from db_backup_utility.factories.storage_adapter_factory import StorageAdapterFactory
from db_backup_utility.strategies.sqlite_backup_strategy import SQLiteBackupStrategy


def test_backup_strategy_factory_returns_sqlite_strategy():
    strategy = BackupStrategyFactory().create("sqlite")

    assert isinstance(strategy, SQLiteBackupStrategy)


def test_storage_adapter_factory_returns_local_adapter():
    adapter = StorageAdapterFactory().create("local")

    assert isinstance(adapter, LocalStorageAdapter)

