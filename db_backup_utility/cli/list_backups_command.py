from __future__ import annotations

from argparse import Namespace

from db_backup_utility.cli.command import Command
from db_backup_utility.facade.backup_facade import BackupFacade
from db_backup_utility.models.backup_config import BackupConfig


class ListBackupsCommand(Command):
    def __init__(self, facade: BackupFacade) -> None:
        self.facade = facade

    def execute(self, args: Namespace) -> None:
        config = BackupConfig(
            db_type=args.db,
            database_name=args.database,
            storage_type=args.storage,
            output_path=args.output_path,
            cloud_bucket=args.cloud_bucket,
            cloud_prefix=args.cloud_prefix,
        )
        backups = self.facade.list_backups(config)
        for backup in backups:
            print(
                f"{backup.file_name}\t{backup.size_bytes} bytes\t"
                f"{backup.created_at.isoformat()}\t{backup.storage_location}"
            )
