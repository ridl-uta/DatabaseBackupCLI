from __future__ import annotations

import argparse

from db_backup_utility.cli.backup_command import BackupCommand
from db_backup_utility.cli.list_backups_command import ListBackupsCommand
from db_backup_utility.cli.restore_command import RestoreCommand
from db_backup_utility.cli.schedule_command import ScheduleCommand
from db_backup_utility.cli.test_connection_command import TestConnectionCommand
from db_backup_utility.facade.backup_facade import BackupFacade


class CommandParser:
    def __init__(self, facade: BackupFacade) -> None:
        self.facade = facade

    def execute(self, argv: list[str] | None = None) -> None:
        parser = self._build_parser()
        args = parser.parse_args(argv)
        try:
            args.command.execute(args)
        except AttributeError:
            parser.print_help()

    def _build_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(prog="dbbackup")
        subparsers = parser.add_subparsers()

        backup = subparsers.add_parser("backup", help="Create a database backup")
        self._add_database_args(backup)
        backup.add_argument("--backup-type", default="full")
        backup.add_argument("--storage", default="local")
        backup.add_argument("--output-path", default="./backups")
        backup.add_argument("--cloud-bucket")
        backup.add_argument("--cloud-prefix", default="")
        backup.add_argument("--notify", action="store_true")
        backup.set_defaults(command=BackupCommand(self.facade))

        restore = subparsers.add_parser("restore", help="Restore a database backup")
        self._add_database_args(restore)
        restore.add_argument("--backup-file", required=True)
        restore.add_argument("--storage", default="local")
        restore.add_argument("--output-path", default="./backups")
        restore.add_argument("--cloud-bucket")
        restore.add_argument("--cloud-prefix", default="")
        restore.add_argument("--overwrite-existing", action="store_true")
        restore.set_defaults(command=RestoreCommand(self.facade))

        test = subparsers.add_parser("test-connection", help="Test database connectivity")
        self._add_database_args(test)
        test.set_defaults(command=TestConnectionCommand(self.facade))

        list_backups = subparsers.add_parser("list-backups", help="List stored backups")
        list_backups.add_argument("--db", default="sqlite")
        list_backups.add_argument("--database", default="")
        list_backups.add_argument("--storage", default="local")
        list_backups.add_argument("--output-path", default="./backups")
        list_backups.add_argument("--cloud-bucket")
        list_backups.add_argument("--cloud-prefix", default="")
        list_backups.set_defaults(command=ListBackupsCommand(self.facade))

        schedule = subparsers.add_parser("schedule", help="Schedule automatic backup")
        self._add_database_args(schedule)
        schedule.add_argument("--backup-type", default="full")
        schedule.add_argument("--storage", default="local")
        schedule.add_argument("--output-path", default="./backups")
        schedule.add_argument("--cron", required=True)
        schedule.set_defaults(command=ScheduleCommand(self.facade))
        return parser

    @staticmethod
    def _add_database_args(parser: argparse.ArgumentParser) -> None:
        parser.add_argument("--db", required=True)
        parser.add_argument("--host", default="localhost")
        parser.add_argument("--port", type=int, default=0)
        parser.add_argument("--username", default="")
        parser.add_argument("--password", default="")
        parser.add_argument("--database", required=True)
