from argparse import Namespace

from db_backup_utility.cli.backup_command import BackupCommand


class FakeFacade:
    def __init__(self):
        self.config = None

    def run_backup(self, config):
        self.config = config
        return Namespace(status="success", storage_location="/tmp/backup.gz")


def test_backup_command_builds_config(capsys):
    facade = FakeFacade()
    command = BackupCommand(facade)
    args = Namespace(
        db="sqlite",
        host="localhost",
        port=0,
        username="",
        password="",
        database="app.db",
        backup_type="full",
        storage="local",
        output_path="./backups",
        cloud_bucket=None,
        cloud_prefix="",
        notify=False,
    )

    command.execute(args)

    assert facade.config.db_type == "sqlite"
    assert facade.config.database_name == "app.db"
    assert "Backup succeeded" in capsys.readouterr().out
