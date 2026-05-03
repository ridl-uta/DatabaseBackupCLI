# Database Backup Utility

Database Backup Utility is a Python command-line application for creating, storing, listing, and restoring database backups. The current implementation supports SQLite backup and restore, local file storage, AWS S3 storage, gzip compression, activity logging, and backup history recording.

The project is designed so new database engines, storage providers, notifications, and scheduling behavior can be added without rewriting the main backup workflow.

## What It Does

- Tests database connectivity before running backups.
- Creates database backup files.
- Compresses backup files with gzip.
- Stores backups locally or in AWS S3.
- Lists stored backups.
- Restores SQLite backups from local storage or S3.
- Logs backup and restore events.
- Records event history as JSON lines.
- Provides placeholders for MySQL, PostgreSQL, MongoDB, Google Cloud Storage, Azure Blob Storage, Slack notifications, and scheduling.

## Current Support

Implemented:

- SQLite connection test
- SQLite backup
- SQLite restore
- Local storage
- AWS S3 storage
- Gzip compression and decompression
- CLI commands
- Logging and history observers
- Unit tests

Scaffolded but not fully implemented:

- MySQL backup/restore
- PostgreSQL backup/restore
- MongoDB backup/restore
- Google Cloud Storage
- Azure Blob Storage
- Slack notifications
- Persistent scheduling

## Setup

```bash
cd /Users/imtiazevan/Desktop/Projects/temp/DesktopBackUpCLI
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Run tests:

```bash
python -m pytest
```

Show CLI help:

```bash
python -m db_backup_utility.cli.main --help
```

## Usage

Create a small SQLite database for testing:

```bash
python -c "import sqlite3; c=sqlite3.connect('test.db'); c.execute('create table if not exists items(id integer primary key, name text)'); c.execute('insert into items(name) values (?)', ('demo',)); c.commit(); c.close()"
```

Test SQLite connection:

```bash
python -m db_backup_utility.cli.main test-connection \
  --db sqlite \
  --database ./test.db
```

Back up SQLite to local storage:

```bash
python -m db_backup_utility.cli.main backup \
  --db sqlite \
  --database ./test.db \
  --backup-type full \
  --storage local \
  --output-path ./backups
```

List local backups:

```bash
python -m db_backup_utility.cli.main list-backups \
  --storage local \
  --output-path ./backups
```

Restore SQLite from a local backup:

```bash
python -m db_backup_utility.cli.main restore \
  --db sqlite \
  --database ./restored.db \
  --backup-file ./backups/test_YYYYMMDDHHMMSS.sqlite.gz \
  --storage local \
  --overwrite-existing
```

Back up SQLite to AWS S3:

```bash
python -m db_backup_utility.cli.main backup \
  --db sqlite \
  --database ./test.db \
  --backup-type full \
  --storage s3 \
  --output-path ./backups \
  --cloud-bucket my-backup-bucket \
  --cloud-prefix database-backups
```

List S3 backups:

```bash
python -m db_backup_utility.cli.main list-backups \
  --storage s3 \
  --cloud-bucket my-backup-bucket \
  --cloud-prefix database-backups
```

Restore SQLite from S3:

```bash
python -m db_backup_utility.cli.main restore \
  --db sqlite \
  --database ./restored.db \
  --backup-file s3://my-backup-bucket/database-backups/test_YYYYMMDDHHMMSS.sqlite.gz \
  --storage s3 \
  --output-path ./backups \
  --overwrite-existing
```

AWS credentials are not stored in this project. Use standard AWS configuration methods such as environment variables, `~/.aws/credentials`, `AWS_PROFILE`, or an IAM role.

## Human-Readable Architecture

The application is split into small layers. Each layer has one clear job.

```text
User runs CLI command
  -> CLI command object builds a config object
  -> Facade exposes a simple workflow method
  -> Service coordinates the actual work
  -> Factory selects the correct strategy or adapter
  -> Strategy performs database-specific behavior
  -> Adapter talks to local disk, S3, or another provider
  -> Observers record logs, history, or notifications
```

### CLI Layer

The CLI layer parses terminal input and maps each command to a command object. It does not contain backup logic.

Examples:

- `backup` maps to `BackupCommand`
- `restore` maps to `RestoreCommand`
- `test-connection` maps to `TestConnectionCommand`
- `list-backups` maps to `ListBackupsCommand`
- `schedule` maps to `ScheduleCommand`

### Facade Layer

`BackupFacade` gives the CLI one simple interface for workflows such as backup, restore, test connection, list backups, and schedule backup. The facade hides the number of services involved.

### Service Layer

Services coordinate application work:

- `BackupService` runs the backup workflow.
- `RestoreService` runs the restore workflow.
- `ConnectionTestService` validates database access.
- `StorageService` stores, retrieves, and lists backup files.
- `CompressionService` compresses and decompresses backup files.
- `SchedulerService` accepts schedule requests.

### Strategy Layer

Strategies contain database-specific behavior. SQLite, MySQL, PostgreSQL, and MongoDB do not back up or restore the same way, so each database gets its own strategy class.

Only SQLite is implemented right now. Other database strategies are present as extension points.

### Factory Layer

Factories choose which strategy or adapter to use:

- `BackupStrategyFactory` selects the database strategy.
- `StorageAdapterFactory` selects local, S3, GCS, or Azure storage.
- `RestoreStrategyFactory` reuses database strategy creation for restore.
- `NotificationAdapterFactory` creates notification adapters.

### Adapter Layer

Adapters wrap external systems behind a common interface. Local disk and AWS S3 have different APIs, but the rest of the app calls both through the same methods: `store`, `retrieve`, `list`, and `delete`.

### Observer Layer

Observers react to events without changing the backup workflow. Logging and history recording are implemented this way. Slack notifications are scaffolded.

## Why The Project Is Extendable

The project is extendable because each changing behavior has a dedicated extension point.

To add a new database:

1. Create a new database strategy.
2. Implement `test_connection`, `backup`, and `restore`.
3. Register it in `BackupStrategyFactory`.

The CLI, facade, and backup service do not need to know the details.

To add a new storage provider:

1. Create a new storage adapter.
2. Implement `store`, `retrieve`, `list`, and `delete`.
3. Register it in `StorageAdapterFactory`.

The backup service still just calls `StorageService.store()`.

To add a new notification channel:

1. Create an adapter for the provider.
2. Create an observer.
3. Subscribe the observer to `BackupEventPublisher`.

The backup workflow does not need to change.

## Why The Project Is Readable

- The CLI files only parse commands and build config objects.
- The facade has short methods that describe workflows in plain terms.
- Services coordinate use cases without provider-specific details.
- Database-specific code lives in strategy classes.
- Storage-specific code lives in adapter classes.
- Factories keep object selection in one place.
- Dataclasses make the data passed between layers explicit.
- Custom exceptions keep errors understandable.
- Tests cover the main behavior and show intended usage.

## Project Structure

```text
db_backup_utility/
  adapters/      Storage and external API wrappers
  cli/           Command-line parser and command objects
  config/        Environment/config helpers
  exceptions/    Project-specific exceptions
  facade/        Simple workflow entry point
  factories/     Strategy and adapter selection
  models/        Dataclasses for configs, results, events, metadata
  observers/     Logging, history, notification event listeners
  services/      Backup, restore, compression, storage, scheduling logic
  strategies/    Database-specific backup/restore implementations
tests/           Unit tests
```

## Method Inventory

### CLI

- `Command.execute(args)`: Base command contract.
- `BackupCommand.__init__(facade)`: Store the facade dependency.
- `BackupCommand.execute(args)`: Build `BackupConfig` and run backup.
- `RestoreCommand.__init__(facade)`: Store the facade dependency.
- `RestoreCommand.execute(args)`: Build `RestoreConfig` and run restore.
- `TestConnectionCommand.__init__(facade)`: Store the facade dependency.
- `TestConnectionCommand.execute(args)`: Build `BackupConfig` and test connection.
- `ListBackupsCommand.__init__(facade)`: Store the facade dependency.
- `ListBackupsCommand.execute(args)`: Build `BackupConfig` and list backups.
- `ScheduleCommand.__init__(facade)`: Store the facade dependency.
- `ScheduleCommand.execute(args)`: Build `BackupConfig` and schedule a backup.
- `CommandParser.__init__(facade)`: Store the facade dependency.
- `CommandParser.execute(argv=None)`: Parse arguments and execute the chosen command.
- `CommandParser._build_parser()`: Build the argparse command tree.
- `CommandParser._add_database_args(parser)`: Add shared DB flags.
- `build_facade()`: Wire dependencies together.
- `main(argv=None)`: CLI entry point.

### Facade

- `BackupFacade.__init__(...)`: Receive workflow services.
- `BackupFacade.run_backup(config)`: Run the backup workflow.
- `BackupFacade.run_restore(config)`: Run the restore workflow.
- `BackupFacade.test_connection(config)`: Test database connectivity.
- `BackupFacade.list_backups(config)`: List stored backups.
- `BackupFacade.schedule_backup(config)`: Schedule a backup request.

### Services

- `BackupService.__init__(...)`: Receive factories, compression, storage, and event publisher.
- `BackupService.create_backup(config)`: Test connection, create backup, compress, store, publish events, and return `BackupResult`.
- `BackupService._publish(...)`: Publish a backup event.
- `RestoreService.__init__(...)`: Receive restore factory, storage, compression, and event publisher.
- `RestoreService.restore_backup(config)`: Retrieve backup, decompress, restore, publish events, and return `RestoreResult`.
- `RestoreService._publish(...)`: Publish a restore event.
- `ConnectionTestService.__init__(strategy_factory)`: Store the strategy factory.
- `ConnectionTestService.test_connection(config)`: Select strategy and test DB connection.
- `StorageService.__init__(adapter_factory)`: Store the storage adapter factory.
- `StorageService.store(file_path, config)`: Store a backup with the selected adapter.
- `StorageService.retrieve(file_name, config)`: Retrieve a backup with the selected adapter.
- `StorageService.list_backups(config)`: List backups with the selected adapter.
- `CompressionService.compress(file_path, compression_type="gzip")`: Compress a file.
- `CompressionService.decompress(file_path)`: Decompress a `.gz` file.
- `SchedulerService.schedule(config)`: Accept a schedule request.
- `SchedulerService.remove_schedule(schedule_id)`: Remove a schedule placeholder.
- `NotificationService.__init__(event_publisher)`: Store event publisher.
- `NotificationService.subscribe(observer)`: Subscribe an observer.
- `get_logger()`: Return the application logger.

### Factories

- `BackupStrategyFactory.__init__()`: Register database strategy instances.
- `BackupStrategyFactory.create(db_type)`: Return the strategy for a DB type.
- `RestoreStrategyFactory`: Reuses backup strategy selection for restore.
- `StorageAdapterFactory.__init__()`: Register storage adapter instances.
- `StorageAdapterFactory.create(storage_type)`: Return the adapter for a storage type.
- `NotificationAdapterFactory.create_slack_adapter()`: Create a Slack adapter.

### Strategies

- `DatabaseBackupStrategy.test_connection(config)`: Base contract for connection testing.
- `DatabaseBackupStrategy.backup(config)`: Base contract for creating a raw backup.
- `DatabaseBackupStrategy.restore(config, backup_file)`: Base contract for restore.
- `DatabaseBackupStrategy._database_path(config)`: Resolve database path-like config fields.
- `SQLiteBackupStrategy.test_connection(config)`: Open SQLite database read-only and run a simple query.
- `SQLiteBackupStrategy.backup(config)`: Copy SQLite database to a timestamped backup file.
- `SQLiteBackupStrategy.restore(config, backup_file)`: Restore SQLite by copying the backup file to the target path.
- `MySQLBackupStrategy.test_connection(config)`: Placeholder for MySQL connection testing.
- `MySQLBackupStrategy.backup(config)`: Placeholder for MySQL backup.
- `MySQLBackupStrategy.restore(config, backup_file)`: Placeholder for MySQL restore.
- `PostgreSQLBackupStrategy.test_connection(config)`: Placeholder for PostgreSQL connection testing.
- `PostgreSQLBackupStrategy.backup(config)`: Placeholder for PostgreSQL backup.
- `PostgreSQLBackupStrategy.restore(config, backup_file)`: Placeholder for PostgreSQL restore.
- `MongoDBBackupStrategy.test_connection(config)`: Placeholder for MongoDB connection testing.
- `MongoDBBackupStrategy.backup(config)`: Placeholder for MongoDB backup.
- `MongoDBBackupStrategy.restore(config, backup_file)`: Placeholder for MongoDB restore.

### Adapters

- `StorageAdapter.store(file_path, config)`: Base contract for storing a file.
- `StorageAdapter.retrieve(file_name, config)`: Base contract for retrieving a file.
- `StorageAdapter.list(config)`: Base contract for listing files.
- `StorageAdapter.delete(file_name, config)`: Base contract for deleting a file.
- `LocalStorageAdapter.store(file_path, config)`: Copy a file into the local output path.
- `LocalStorageAdapter.retrieve(file_name, config)`: Resolve and validate a local backup path.
- `LocalStorageAdapter.list(config)`: Return local backup metadata.
- `LocalStorageAdapter.delete(file_name, config)`: Delete a local backup file.
- `S3StorageAdapter.store(file_path, config)`: Upload a backup file to S3.
- `S3StorageAdapter.retrieve(file_name, config)`: Download a backup from S3.
- `S3StorageAdapter.list(config)`: List S3 backup objects as metadata.
- `S3StorageAdapter.delete(file_name, config)`: Delete an S3 object.
- `S3StorageAdapter._client()`: Create a boto3 S3 client.
- `S3StorageAdapter._build_key(file_name, prefix="")`: Build an S3 object key.
- `S3StorageAdapter._clean_prefix(prefix="")`: Normalize an S3 prefix.
- `S3StorageAdapter._resolve_bucket_and_key(file_name, cloud_bucket, cloud_prefix="")`: Resolve S3 bucket and key from config or URI.
- `GoogleCloudStorageAdapter.store(file_path, config)`: Placeholder.
- `GoogleCloudStorageAdapter.retrieve(file_name, config)`: Placeholder.
- `GoogleCloudStorageAdapter.list(config)`: Placeholder.
- `GoogleCloudStorageAdapter.delete(file_name, config)`: Placeholder.
- `AzureBlobStorageAdapter.store(file_path, config)`: Placeholder.
- `AzureBlobStorageAdapter.retrieve(file_name, config)`: Placeholder.
- `AzureBlobStorageAdapter.list(config)`: Placeholder.
- `AzureBlobStorageAdapter.delete(file_name, config)`: Placeholder.
- `SlackAdapter.__init__(webhook_url=None)`: Store optional Slack webhook URL.
- `SlackAdapter.send_message(message)`: Send a Slack webhook message if configured.

### Observers

- `BackupObserver.update(event)`: Base observer contract.
- `BackupEventPublisher.__init__()`: Create empty observer list.
- `BackupEventPublisher.subscribe(observer)`: Add an observer.
- `BackupEventPublisher.unsubscribe(observer)`: Remove an observer.
- `BackupEventPublisher.notify(event)`: Notify all observers.
- `LoggerObserver.update(event)`: Write event details to the log file.
- `HistoryRecorderObserver.__init__(history_path="logs/history.jsonl")`: Set history output path.
- `HistoryRecorderObserver.update(event)`: Append event as JSON.
- `SlackNotificationObserver.__init__(slack_adapter)`: Store Slack adapter.
- `SlackNotificationObserver.update(event)`: Send event message to Slack adapter.

### Config

- `ConfigLoader.__init__(env_file=None)`: Load `.env` values.
- `ConfigLoader.get(key, default=None)`: Read a config value from the environment.

### Models

The model files define dataclasses and do not contain custom methods beyond dataclass-generated initialization and representation:

- `BackupConfig`
- `RestoreConfig`
- `BackupResult`
- `RestoreResult`
- `StorageResult`
- `BackupEvent`
- `BackupMetadata`

### Exceptions

The exception classes are named failure types and do not define custom methods:

- `BackupException`
- `ConnectionException`
- `StorageException`
- `RestoreException`
- `CompressionException`
- `ConfigurationException`

