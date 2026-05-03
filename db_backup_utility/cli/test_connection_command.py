from __future__ import annotations

from argparse import Namespace

from db_backup_utility.cli.command import Command
from db_backup_utility.facade.backup_facade import BackupFacade
from db_backup_utility.models.backup_config import BackupConfig


class TestConnectionCommand(Command):
    def __init__(self, facade: BackupFacade) -> None:
        self.facade = facade

    def execute(self, args: Namespace) -> None:
        config = BackupConfig(
            db_type=args.db,
            host=args.host,
            port=args.port,
            username=args.username,
            password=args.password,
            database_name=args.database,
            storage_type="local",
        )
        self.facade.test_connection(config)
        print("Connection successful.")

