#!/usr/bin/env python3
"""
Victoria 2 Localisation Line Ending Fixer
==========================================

Fixes CSV files to use Victoria 2's required double carriage return line endings (\r\r\n).

Usage:
    python fix-line-endings.py [path] [--dry-run] [--no-backup]
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import Tuple, List

def fix_file_line_endings(file_path: Path, dry_run=False, no_backup=False) -> Tuple[bool, str]:
    """
    Fix line endings in a single CSV file.
    
    Args:
        file_path: Path to the CSV file
        dry_run: Simulate only
        no_backup: specific flag to skip backup
        
    Returns:
        Tuple of (success, message)
    """
    try:
        # Read file as binary to preserve exact content
        with open(file_path, 'rb') as f:
            content = f.read()

        original_size = len(content)

        # First, normalize any existing \r\n to single \n for consistent processing
        normalized = content.replace(b'\r\n', b'\n')

        # Now convert all \n to \r\r\n (double carriage return + line feed)
        fixed = normalized.replace(b'\n', b'\r\r\n')

        # Remove any accidental triple carriage returns that might have occurred
        fixed = fixed.replace(b'\r\r\r\n', b'\r\r\n')

        new_size = len(fixed)

        # Check if file actually needed fixing
        if fixed == content:
            return True, f"Already correct ({original_size} bytes)"

        if dry_run:
            return True, f"[DRY RUN] Would fix: {original_size} -> {new_size} bytes"

        # Create backup
        if not no_backup:
            backup_path = file_path.with_suffix(file_path.suffix + '.bak_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
            try:
                shutil.copy2(file_path, backup_path)
            except Exception as e:
                return False, f"Backup failed: {e}"

        # Write fixed content
        with open(file_path, 'wb') as f:
            f.write(fixed)

        msg = f"Fixed: {original_size} -> {new_size} bytes"
        if not no_backup:
            msg += " (Backup created)"
        return True, msg

    except Exception as e:
        return False, f"Error: {e}"


def verify_file(file_path: Path) -> bool:
    """
    Verify that a file has correct \r\r\n line endings.
    """
    try:
        with open(file_path, 'rb') as f:
            sample = f.read(10240)
        return b'\r\r\n' in sample
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description="Fix V2 CSV line endings.")
    parser.add_argument("path", nargs="?", help="Target file or directory")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without changes")
    parser.add_argument("--no-backup", action="store_true", help="Skip backup creation")
    args = parser.parse_args()

    # Determine target path
    script_path = Path(__file__).resolve()
    
    if args.path:
        target_path = Path(args.path)
    else:
        # Try relative to script
        target_path = script_path.parent.parent / "CoE_RoI_R" / "localisation"
        if not target_path.exists():
             target_path = Path(".")

    print("=" * 60)
    print("Victoria 2 Localisation Line Ending Fixer")
    print("=" * 60)
    print(f"Target: {target_path}")
    if args.dry_run:
        print("MODE: DRY RUN (No changes will be made)")
    print()

    if not target_path.exists():
        print(f"ERROR: Path does not exist: {target_path}")
        return 1

    # Collect files
    if target_path.is_file():
        files = [target_path]
    else:
        files = sorted(target_path.glob("*.csv"))

    if not files:
        print("No CSV files found!")
        return 1

    print(f"Found {len(files)} CSV file(s)")
    print()

    # Process files
    results: List[Tuple[Path, bool, str]] = []
    fixed_count = 0
    skipped_count = 0
    error_count = 0

    for file_path in files:
        success, message = fix_file_line_endings(file_path, dry_run=args.dry_run, no_backup=args.no_backup)
        results.append((file_path, success, message))

        if success:
            if "Already correct" in message:
                skipped_count += 1
                status = "[OK SKIP]"
            else:
                fixed_count += 1
                status = "[OK FIXED]"
        else:
            error_count += 1
            status = "[ERROR]"

        print(f"[{status}] {file_path.name}")
        if message and "Already correct" not in message:
            print(f"       {message}")
        elif not success:
            print(f"       {message}")

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total files:      {len(files)}")
    print(f"Fixed:            {fixed_count}")
    print(f"Already correct:  {skipped_count}")
    print(f"Errors:           {error_count}")
    print()

    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
