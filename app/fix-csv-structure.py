#!/usr/bin/env python3
"""
Victoria 2 CSV Structure Fixer
==============================

Forces all CSV files to match Victoria 2's exact column structure.
"""

import sys
import argparse
import shutil
from pathlib import Path
from datetime import datetime


def fix_csv_file(file_path: Path, dry_run=False, no_backup=False) -> bool:
    """Fix a single CSV file to exact Victoria 2 format."""
    try:
        # Read as binary to preserve encoding
        with open(file_path, 'rb') as f:
            content = f.read()

        # Decode (try cp1252 first, then utf-8)
        try:
            text = content.decode('cp1252')
        except UnicodeDecodeError:
            text = content.decode('utf-8', errors='replace')

        lines = text.split('\n')
        fixed_lines = []
        
        # Check if change matches current state to avoid needless writes could be done,
        # but exact byte matching on decoded/re-encoded text is tricky.
        # So we reconstruct and see.

        for line in lines:
            if not line.strip():
                fixed_lines.append('')
                continue

            parts = line.rstrip('\r\n').split(';')
            clean_parts = []
            for part in parts:
                if part.strip() == 'x':
                    if not clean_parts:
                        clean_parts.append(part)
                else:
                    clean_parts.append(part)

            if len(clean_parts) >= 14:
                new_parts = clean_parts[:14]
            else:
                new_parts = clean_parts[:]
                while len(new_parts) < 14:
                    new_parts.append('')

            new_parts.append('x')
            while len(new_parts) < 19:
                new_parts.append('')

            fixed_lines.append(';'.join(new_parts))

        fixed_content = '\r\r\n'.join(fixed_lines)
        if not fixed_content.endswith('\r\r\n'):
            fixed_content += '\r\r\n'

        fixed_bytes = fixed_content.encode('cp1252', errors='replace')
        
        # Simple check if anything effectively changed
        if fixed_bytes == content:
             return True # No changes needed

        if dry_run:
            print(f"  [DRY RUN] Would fix {file_path.name}")
            return True

        # Backup
        if not no_backup:
            backup_path = file_path.with_suffix(file_path.suffix + '.bak_' + datetime.now().strftime('%Y%m%d_%H%M%S'))
            try:
                shutil.copy2(file_path, backup_path)
            except Exception as e:
                print(f"  [WARN] Backup failed: {e}")

        # Write back
        with open(file_path, 'wb') as f:
            f.write(fixed_bytes)

        return True

    except Exception as e:
        print(f"  ERROR processing {file_path.name}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Fix V2 CSV structure.")
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
    print("Victoria 2 CSV Structure Fixer")
    print("=" * 60)
    print(f"Target: {target_path}")
    if args.dry_run:
        print("MODE: DRY RUN")
    print()

    if not target_path.exists():
        print(f"ERROR: Path not found: {target_path}")
        return 1

    if target_path.is_file():
        files = [target_path]
    else:
        files = sorted(target_path.glob("*.csv"))

    if not files:
        print("No CSV files found!")
        return 1

    print(f"Processing {len(files)} file(s)...")
    print()

    fixed = 0
    for file_path in files:
        if fix_csv_file(file_path, dry_run=args.dry_run, no_backup=args.no_backup):
            print(f"  [OK] {file_path.name}")
            fixed += 1
        else:
            print(f"  [FAIL] {file_path.name}")

    print()
    print(f"Done! Processed {fixed} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
