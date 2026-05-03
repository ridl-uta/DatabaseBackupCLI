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

## Architecture

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
