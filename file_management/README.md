
# Portable Backup Script

This is a sanitized, portable Python backup utility. It is safe for public repositories and does not include any host-specific paths or organization names.

## Features

- Copies files from one or more source directories to a destination.
- Skips hidden files and directories by default.
- Preserves timestamps and metadata with `shutil.copy2`.
- Progress bar support with `tqdm` (optional).
- Dry-run mode to preview actions.
- Logging to a configurable file (default: `./backup.log`).
- Optional desktop notifications if a notifier binary is provided.

## Installation

Clone this repository and ensure you have Python 3.8+ installed.

```bash
git clone https://github.com/rich-fleming/python.git
cd yourrepo
pip install -r requirements.txt
```

Optional dependency for progress bars:

```bash
pip install tqdm
```

## Configuration

You can configure the script via environment variables, a `.env` file, or CLI arguments.

Example `.env` file is provided as [.env.example](.env.example).

### Environment Variables

- `BACKUP_SOURCES`: Comma-separated list of source directories (e.g., `"~/Documents,~/Pictures"`)
- `BACKUP_DESTINATION`: Destination directory root (e.g., `"~/Backups/MyHost"`)
- `BACKUP_LOGFILE`: Log file path (default: `./backup.log`)
- `BACKUP_NOTIFIER`: Path to a notifier binary (optional)

### CLI Arguments

```bash
python3 18Fbackup_sanitized.py --sources "~/Documents,~/Pictures" --dest "~/Backups/MyHost"
```

Options:

- `--sources`: Comma-separated source directories.
- `--dest`: Destination root directory.
- `--logfile`: Log file path (default: `./backup.log`).
- `--notifier`: Path to notifier binary (optional).
- `--dry-run`: Simulate actions without copying.

## Example Usage

Dry run to preview what would be copied:

```bash
python3 18Fbackup_sanitized.py --sources "~/Documents,~/Pictures" --dest "~/Backups/MyHost" --dry-run
```

Run actual backup:

```bash
python3 18Fbackup_sanitized.py --sources "~/Documents,~/Pictures" --dest "~/Backups/MyHost"
```

## License

MIT License. See [LICENSE](LICENSE) for details.
