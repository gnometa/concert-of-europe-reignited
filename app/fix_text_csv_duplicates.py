#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remove duplicate localisation keys from text.csv.

Victoria 2 uses the first occurrence of a key, so later duplicates are dead code.
This script removes duplicates while preserving file structure.
"""

import os
import sys
import shutil
import argparse
from datetime import datetime

def fix_text_csv_duplicates(filepath, dry_run=False, no_backup=False):
    """
    Remove duplicate keys from text.csv, keeping only the first occurrence.

    Args:
        filepath: Path to text.csv
        dry_run: If True, don't modify the file
        no_backup: If True, don't create a backup
    """
    sys.stdout.write(f"Processing: {filepath}\n")
    
    if not os.path.exists(filepath):
        sys.stderr.write(f"Error: File not found: {filepath}\n")
        return 0

    seen_keys = set()
    kept_lines = []
    removed_count = 0
    
    # Read file with Windows-1252 encoding (standard for Vic2)
    # Use newline='' to preserve original line endings during read
    try:
        with open(filepath, 'r', encoding='windows-1252', errors='strict', newline='') as f:
            for line_num, line in enumerate(f, 1):
                original_line = line
                stripped = line.strip()

                # Always preserve empty lines and comments for file structure
                if not stripped or stripped.startswith('#'):
                    kept_lines.append(original_line)
                    continue

                # Extract key
                if ';' in stripped:
                    key = stripped.split(';', 1)[0].strip()

                    if key in seen_keys:
                        # This is a duplicate - skip it
                        sys.stdout.write(f"  Removing duplicate '{key}' at line {line_num}\n")
                        removed_count += 1
                    else:
                        # First occurrence - keep it
                        seen_keys.add(key)
                        kept_lines.append(original_line)
                else:
                    # Line without semicolon - keep as-is
                    kept_lines.append(original_line)
                    
    except UnicodeDecodeError as e:
        sys.stderr.write(f"Error reading file {filepath}: {e}\n")
        sys.stderr.write("File might contain characters not supported by Windows-1252 encoding.\n")
        return 0
    except Exception as e:
        sys.stderr.write(f"Error processing {filepath}: {e}\n")
        return 0

    sys.stdout.write("\nResults:\n")
    sys.stdout.write(f"Removed duplicates: {removed_count}\n")
    sys.stdout.write(f"Final line count: {len(kept_lines)}\n")
    sys.stdout.write(f"Unique keys: {len(seen_keys)}\n")

    if removed_count > 0:
        if dry_run:
            sys.stdout.write("[DRY RUN] No changes written to disk.\n")
        else:
            # Create backup
            if not no_backup:
                backup_path = filepath + '.dup_backup_' + datetime.now().strftime('%Y%m%d_%H%M%S')
                try:
                    shutil.copy2(filepath, backup_path)
                    sys.stdout.write(f"Created backup: {os.path.basename(backup_path)}\n")
                except Exception as e:
                    sys.stderr.write(f"Warning: Failed to create backup: {e}\n")

            # Write cleaned file
            try:
                with open(filepath, 'w', encoding='windows-1252', newline='') as f:
                    f.writelines(kept_lines)
                sys.stdout.write(f"Successfully wrote cleaned file to {filepath}\n")
            except Exception as e:
                sys.stderr.write(f"Error writing file: {e}\n")
                return 0

    return removed_count

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Remove duplicate localisation keys from CSV files.")
    parser.add_argument("file", nargs="?", help="Path to the CSV file to process (default: looks for text.csv in relative path)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate changes without modifying files")
    parser.add_argument("--no-backup", action="store_true", help="Skip creating a backup file")
    
    args = parser.parse_args()
    
    # Default path logic
    target_file = args.file
    if not target_file:
        # Try to find text.csv relative to script location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Assuming script is in mod/app/ and text.csv is in mod/CoE_RoI_R/localisation/
        # Adjust up two levels to mod folder, then down to localisation
        potential_path = os.path.join(script_dir, "..", "CoE_RoI_R", "localisation", "text.csv")
        potential_path = os.path.abspath(potential_path)
        
        if os.path.exists(potential_path):
            target_file = potential_path
        else:
            # Fallback to current directory
            target_file = "text.csv"
            
    sys.stdout.write("=" * 70 + "\n")
    sys.stdout.write("CSV Duplicate Fixer\n")
    sys.stdout.write("=" * 70 + "\n")

    fix_text_csv_duplicates(target_file, dry_run=args.dry_run, no_backup=args.no_backup)

    return 0

if __name__ == '__main__':
    sys.exit(main())
