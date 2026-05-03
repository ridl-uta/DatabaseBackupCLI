from __future__ import annotations

from argparse import Namespace

from db_backup_utility.cli.command import Command
from db_backup_utility.facade.backup_facade import BackupFacade
from db_backup_utility.models.restore_config import RestoreConfig


class RestoreCommand(Command):
    def __init__(self, facade: BackupFacade) -> None:
        self.facade = facade

    def execute(self, args: Namespace) -> None:
        config = RestoreConfig(
            db_type=args.db,
            host=args.host,
            port=args.port,
            username=args.username,
            password=args.password,
            target_database_name=args.database,
            backup_file_path=args.backup_file,
            storage_type=args.storage,
            output_path=args.output_path,
            cloud_bucket=args.cloud_bucket,
            cloud_prefix=args.cloud_prefix,
            overwrite_existing=args.overwrite_existing,
        )
        result = self.facade.run_restore(config)
        if result.status == "success":
            print(f"Restore succeeded: {result.restored_database}")
        else:
            print(f"Restore failed: {result.error_message}")
