#!/usr/bin/env python3
"""
Victoria 2 Localisation Column Count Fixer
============================================

Fixes CSV files to match Victoria 2's exact 19-column format.
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import Tuple, List

TARGET_COLUMNS = 19

def fix_file_column_count(file_path: Path, dry_run=False, no_backup=False) -> Tuple[bool, str]:
    """
    Fix column count in a single CSV file.

    Args:
        file_path: Path to the CSV file
        dry_run: Simulate only
        no_backup: Skip backup creation

    Returns:
        Tuple of (success, message)
    """
    try:
        # Read file with binary to preserve exact line endings
        with open(file_path, 'rb') as f:
            content = f.read()

        original_size = len(content)

        # Decode for processing (handle both cp1252 and utf-8)
        try:
            text = content.decode('cp1252')
        except UnicodeDecodeError:
            text = content.decode('utf-8', errors='replace')

        lines = text.split('\n')

        # Preserve the exact line ending from the file (simple heuristic)
        line_ending = b'\r\r\n'
        for line in lines[:10]:
            if line.strip():
                idx = content.find(line.encode('cp1252', errors='replace'))
                if idx >= 0:
                    remaining = content[idx + len(line):]
                    if remaining.startswith(b'\r\r\n'):
                        line_ending = b'\r\r\n'
                    elif remaining.startswith(b'\r\n'):
                        line_ending = b'\r\n'
                    elif remaining.startswith(b'\n'):
                        line_ending = b'\n'
                    break

        fixed_lines = []
        changed = False

        for i, line in enumerate(lines):
            if not line.strip():
                fixed_lines.append(line)
                continue

            parts = line.rstrip('\r\n').split(';')

            if len(parts) == TARGET_COLUMNS:
                fixed_lines.append(line.rstrip('\r\n'))
                continue

            changed = True
            
            # Fix strategy
            if len(parts) >= 14:
                new_parts = parts[:14]
            else:
                new_parts = parts[:]
                while len(new_parts) < 14:
                    new_parts.append('')

            new_parts.append('x')
            while len(new_parts) < TARGET_COLUMNS:
                new_parts.append('')

            fixed_lines.append(';'.join(new_parts))

        if not changed:
            return True, f"Already correct ({len(lines)} lines, {TARGET_COLUMNS} cols)"

        # Re-encode
        fixed_content = line_ending.decode('latin1').join(fixed_lines)
        fixed_bytes = fixed_content.encode('cp1252', errors='replace')

        if not fixed_bytes.endswith(line_ending):
             fixed_bytes += line_ending

        new_size = len(fixed_bytes)

        if dry_run:
             return True, f"[DRY RUN] Would fix: {original_size} -> {new_size} bytes"

        # Backup
        if not no_backup:
            backup_path = file_path.with_suffix(file_path.suffix + '.bak_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
            try:
                shutil.copy2(file_path, backup_path)
            except Exception as e:
                return False, f"Backup failed: {e}"

        # Write fixed content
        with open(file_path, 'wb') as f:
            f.write(fixed_bytes)

        msg = f"Fixed: lines={len(lines)} ({original_size}->{new_size} bytes)"
        if not no_backup:
            msg += " (Backup created)"
            
        return True, msg

    except Exception as e:
        return False, f"Error: {e}"


def main():
    parser = argparse.ArgumentParser(description="Fix V2 CSV column counts.")
    parser.add_argument("path", nargs="?", help="Target file or directory")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without changes")
    parser.add_argument("--no-backup", action="store_true", help="Skip backup creation")
    args = parser.parse_args()

    script_path = Path(__file__).resolve()
    
    if args.path:
        target_path = Path(args.path)
    else:
        target_path = script_path.parent.parent / "CoE_RoI_R" / "localisation"
        if not target_path.exists():
             target_path = Path(".")

    print("=" * 60)
    print("Victoria 2 Localisation Column Count Fixer")
    print("=" * 60)
    print(f"Target: {target_path}")
    if args.dry_run:
        print("MODE: DRY RUN")
    print()

    if not target_path.exists():
        print(f"ERROR: Path does not exist: {target_path}")
        return 1

    if target_path.is_file():
        files = [target_path]
    else:
        files = sorted(target_path.glob("*.csv"))

    if not files:
        print("No CSV files found!")
        return 1

    print(f"Found {len(files)} CSV file(s)")
    print()

    results: List[Tuple[Path, bool, str]] = []
    fixed_count = 0
    skipped_count = 0
    error_count = 0

    for file_path in files:
        success, message = fix_file_column_count(file_path, dry_run=args.dry_run, no_backup=args.no_backup)
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
