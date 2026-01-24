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
from datetime import datetime

def fix_text_csv_duplicates(filepath):
    """
    Remove duplicate keys from text.csv, keeping only the first occurrence.

    Args:
        filepath: Path to text.csv
    """
    # Create backup
    backup_path = filepath + '.dup_backup_' + datetime.now().strftime('%Y%m%d_%H%M%S')
    shutil.copy2(filepath, backup_path)
    sys.stdout.write("Created backup: {0}\n".format(os.path.basename(backup_path)))

    seen_keys = set()
    kept_lines = []
    removed_count = 0
    lines_with_content = []  # Track line numbers with actual content

    sys.stdout.write("\nProcessing file...\n")

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line_num, line in enumerate(f, 1):
            original_line = line
            line = line.strip()

            # Always preserve empty lines and comments for file structure
            if not line or line.startswith('#'):
                kept_lines.append(original_line)
                continue

            # Extract key
            if ';' in line:
                key = line.split(';', 1)[0].strip()

                if key in seen_keys:
                    # This is a duplicate - skip it
                    sys.stdout.write("  Removing duplicate '{0}' at line {1}\n".format(key, line_num))
                    removed_count += 1
                else:
                    # First occurrence - keep it
                    seen_keys.add(key)
                    kept_lines.append(original_line)
                    lines_with_content.append(line_num)
            else:
                # Line without semicolon - keep as-is
                kept_lines.append(original_line)

    # Write cleaned file
    with open(filepath, 'w', encoding='utf-8', errors='replace') as f:
        f.writelines(kept_lines)

    sys.stdout.write("\n")
    sys.stdout.write("=" * 70 + "\n")
    sys.stdout.write("Results\n")
    sys.stdout.write("=" * 70 + "\n")
    sys.stdout.write("Original lines: {0}\n".format(line_num))
    sys.stdout.write("Removed duplicates: {0}\n".format(removed_count))
    sys.stdout.write("Final line count: {0}\n".format(len(kept_lines)))
    sys.stdout.write("Unique keys: {0}\n".format(len(seen_keys)))
    sys.stdout.write("\nBackup saved at: {0}\n".format(backup_path))

    return removed_count

def main():
    """Main entry point."""
    text_csv_path = r"D:\Steam\steamapps\common\Victoria 2\mod\CoE_RoI_R\localisation\text.csv"

    if not os.path.exists(text_csv_path):
        sys.stderr.write("Error: File not found: {0}\n".format(text_csv_path))
        return 1

    sys.stdout.write("=" * 70 + "\n")
    sys.stdout.write("text.csv Duplicate Fixer\n")
    sys.stdout.write("=" * 70 + "\n")
    sys.stdout.write("\n")

    removed = fix_text_csv_duplicates(text_csv_path)

    sys.stdout.write("\n")
    if removed > 0:
        sys.stdout.write("Successfully removed {0} duplicate entries.\n".format(removed))
    else:
        sys.stdout.write("No duplicates found.\n")

    return 0

if __name__ == '__main__':
    sys.exit(main())
