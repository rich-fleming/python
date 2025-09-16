#!/usr/bin/env python3

import os
import argparse
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Iterable, List

try:
    from tqdm import tqdm  # progress bar (optional)
    HAS_TQDM = True
except Exception:
    HAS_TQDM = False

def parse_sources(s: str) -> List[Path]:
    # Comma-separated list of source directories
    parts = [p.strip() for p in s.split(',') if p.strip()]
    return [Path(p).expanduser().resolve() for p in parts]

def notify(title: str, message: str, notifier_path: str | None) -> None:
    """
    Send a desktop notification if a notifier binary is provided and exists.
    Safe default is no-op.
    """
    if not notifier_path:
        return
    np = Path(notifier_path)
    if np.exists():
        try:
            subprocess.run([str(np), "-title", title, "-message", message], check=False)
        except Exception:
            # Best-effort; don't fail backup because notifications failed
            pass

def log_line(logfile: Path, message: str) -> None:
    logfile.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with logfile.open("a", encoding="utf-8") as f:
        f.write(f"[{ts}] {message}\n")

def is_hidden(path: Path) -> bool:
    # Treat dot-prefixed paths as hidden; skip those by default
    return any(part.startswith('.') for part in path.parts)

def iter_files(src_dir: Path) -> Iterable[Path]:
    for root, _, files in os.walk(src_dir):
        r = Path(root)
        # Skip hidden directories quickly
        if is_hidden(r):
            continue
        for name in files:
            p = r / name
            if is_hidden(p):
                continue
            yield p

def copy_with_dirs(src: Path, base: Path, dest_root: Path, dry_run: bool) -> None:
    rel = src.relative_to(base)
    dest = dest_root / rel
    if dry_run:
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    # Use shutil.copy2 to preserve metadata
    shutil.copy2(src, dest)

# -------------------------
# Core
# -------------------------

def backup(sources: List[Path], destination: Path, dry_run: bool, logfile: Path, notifier: str | None) -> None:
    start = datetime.now()
    notify("Backup", "Backup starting…", notifier)
    log_line(logfile, "Backup started")

    # Validate sources and destination
    missing_sources = [s for s in sources if not s.exists()]
    if missing_sources:
        for s in missing_sources:
            log_line(logfile, f"Source not found: {s}")
        raise SystemExit(f"One or more sources do not exist. First missing: {missing_sources[0]}")

    if not dry_run:
        destination.mkdir(parents=True, exist_ok=True)

    # Count files for progress
    file_list: list[tuple[Path, Path]] = []
    for src in sources:
        for f in iter_files(src):
            file_list.append((f, src))

    iterator = file_list
    if HAS_TQDM:
        iterator = tqdm(file_list, desc="Copying files")

    copied = 0
    for f, base in iterator:
        dest_path = destination / f.relative_to(base)
        if dest_path.exists():
            # Simple optimization: skip if same size and mtime newer or equal at dest
            try:
                if f.stat().st_size == dest_path.stat().st_size and dest_path.stat().st_mtime >= f.stat().st_mtime:
                    continue
            except Exception:
                pass
        copy_with_dirs(f, base, destination, dry_run)
        copied += 1

    end = datetime.now()
    elapsed = end - start

    if dry_run:
        notify("Backup", "Dry run complete", notifier)
        log_line(logfile, f"Dry run completed. Files evaluated: {len(file_list)}; would copy: {copied}; elapsed: {elapsed}")
        print(f"Dry run completed. Files evaluated: {len(file_list)}; would copy: {copied}; elapsed: {elapsed}")
    else:
        notify("Backup", "Backup complete", notifier)
        log_line(logfile, f"Backup completed. Files evaluated: {len(file_list)}; copied: {copied}; elapsed: {elapsed}")
        print(f"Backup completed. Files evaluated: {len(file_list)}; copied: {copied}; elapsed: {elapsed}")

# -------------------------
# CLI
# -------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Portable backup utility")
    parser.add_argument("--sources", type=str, default=os.environ.get("BACKUP_SOURCES", ""),
                        help="Comma-separated list of source directories. Env: BACKUP_SOURCES")
    parser.add_argument("--dest", type=str, default=os.environ.get("BACKUP_DESTINATION", ""),
                        help="Destination directory root. Env: BACKUP_DESTINATION")
    parser.add_argument("--logfile", type=str, default=os.environ.get("BACKUP_LOGFILE", "./backup.log"),
                        help="Log file path. Env: BACKUP_LOGFILE. Default: ./backup.log")
    parser.add_argument("--notifier", type=str, default=os.environ.get("BACKUP_NOTIFIER"),
                        help="Optional path to a desktop notification binary (e.g., terminal-notifier). Env: BACKUP_NOTIFIER")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without copying")

    args = parser.parse_args()

    if not args.sources:
        raise SystemExit("No sources provided. Use --sources or BACKUP_SOURCES env.")
    if not args.dest:
        raise SystemExit("No destination provided. Use --dest or BACKUP_DESTINATION env.")

    sources = parse_sources(args.sources)
    destination = Path(args.dest).expanduser().resolve()
    logfile = Path(args.logfile).expanduser().resolve()

    try:
        backup(sources, destination, args.dry_run, logfile, args.notifier)
    except KeyboardInterrupt:
        log_line(Path(args.logfile), "Backup interrupted by user")
        notify("Backup", "Backup interrupted", args.notifier)
        print("\nBackup interrupted by user.")
        raise SystemExit(130)

if __name__ == "__main__":
    main()
