from __future__ import annotations

import sys

from dotenv import load_dotenv

from db_backup_utility.adapters.slack_adapter import SlackAdapter
from db_backup_utility.cli.command_parser import CommandParser
from db_backup_utility.facade.backup_facade import BackupFacade
from db_backup_utility.factories.backup_strategy_factory import BackupStrategyFactory
from db_backup_utility.factories.restore_strategy_factory import RestoreStrategyFactory
from db_backup_utility.factories.storage_adapter_factory import StorageAdapterFactory
from db_backup_utility.observers.backup_event_publisher import BackupEventPublisher
from db_backup_utility.observers.history_recorder_observer import HistoryRecorderObserver
from db_backup_utility.observers.logger_observer import LoggerObserver
from db_backup_utility.observers.slack_notification_observer import SlackNotificationObserver
from db_backup_utility.services.backup_service import BackupService
from db_backup_utility.services.compression_service import CompressionService
from db_backup_utility.services.connection_test_service import ConnectionTestService
from db_backup_utility.services.restore_service import RestoreService
from db_backup_utility.services.scheduler_service import SchedulerService
from db_backup_utility.services.storage_service import StorageService


def build_facade() -> BackupFacade:
    load_dotenv()
    event_publisher = BackupEventPublisher()
    event_publisher.subscribe(LoggerObserver())
    event_publisher.subscribe(HistoryRecorderObserver())
    event_publisher.subscribe(SlackNotificationObserver(SlackAdapter()))

    backup_strategy_factory = BackupStrategyFactory()
    storage_service = StorageService(StorageAdapterFactory())
    compression_service = CompressionService()

    backup_service = BackupService(
        backup_strategy_factory,
        compression_service,
        storage_service,
        event_publisher,
    )
    restore_service = RestoreService(
        RestoreStrategyFactory(),
        storage_service,
        compression_service,
        event_publisher,
    )
    connection_test_service = ConnectionTestService(backup_strategy_factory)
    scheduler_service = SchedulerService()

    return BackupFacade(
        backup_service,
        restore_service,
        connection_test_service,
        storage_service,
        scheduler_service,
    )


def main(argv: list[str] | None = None) -> None:
    parser = CommandParser(build_facade())
    try:
        parser.execute(argv)
    except Exception as exc:
        raise SystemExit(f"Error: {exc}") from exc


if __name__ == "__main__":
    main(sys.argv[1:])

