#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remove duplicate localisation keys from newstext_3_01.csv.

This file has:
- 7 FAKE_UNKNOWN entries with different content (only first is used)
- 6 RESEARCH_NEWS_* entries duplicated (lines 103-108 duplicate lines 61-66)
"""

import os
import sys
import shutil
from datetime import datetime

def fix_newstext_duplicates(filepath):
    """
    Remove duplicate keys from newstext_3_01.csv.

    Args:
        filepath: Path to newstext_3_01.csv
    """
    # Create backup
    backup_path = filepath + '.dup_backup_' + datetime.now().strftime('%Y%m%d_%H%M%S')
    shutil.copy2(filepath, backup_path)
    sys.stdout.write("Created backup: {0}\n".format(os.path.basename(backup_path)))

    # Lines to remove (1-indexed)
    lines_to_remove = set([
        # FAKE_UNKNOWN duplicates (keep line 123, remove 124-129)
        124, 125, 126, 127, 128, 129,
        # RESEARCH_NEWS duplicates (keep lines 61-66, remove 103-108)
        103, 104, 105, 106, 107, 108,
    ])

    kept_lines = []
    removed_count = 0

    sys.stdout.write("\nProcessing file...\n")

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line_num, line in enumerate(f, 1):
            if line_num in lines_to_remove:
                # Extract key for reporting
                if ';' in line:
                    key = line.split(';', 1)[0].strip()
                    sys.stdout.write("  Removing duplicate '{0}' at line {1}\n".format(key, line_num))
                removed_count += 1
            else:
                kept_lines.append(line)

    # Write cleaned file
    with open(filepath, 'w', encoding='utf-8', errors='replace') as f:
        f.writelines(kept_lines)

    sys.stdout.write("\n")
    sys.stdout.write("=" * 70 + "\n")
    sys.stdout.write("Results\n")
    sys.stdout.write("=" * 70 + "\n")
    sys.stdout.write("Removed {0} duplicate entries.\n".format(removed_count))
    sys.stdout.write("\nBackup saved at: {0}\n".format(backup_path))

    return removed_count

def main():
    """Main entry point."""
    newstext_path = r"D:\Steam\steamapps\common\Victoria 2\mod\CoE_RoI_R\localisation\newstext_3_01.csv"

    if not os.path.exists(newstext_path):
        sys.stderr.write("Error: File not found: {0}\n".format(newstext_path))
        return 1

    sys.stdout.write("=" * 70 + "\n")
    sys.stdout.write("newstext_3_01.csv Duplicate Fixer\n")
    sys.stdout.write("=" * 70 + "\n")
    sys.stdout.write("\n")

    removed = fix_newstext_duplicates(newstext_path)

    sys.stdout.write("\n")
    if removed > 0:
        sys.stdout.write("Successfully removed {0} duplicate entries.\n".format(removed))
    else:
        sys.stdout.write("No duplicates found.\n")

    return 0

if __name__ == '__main__':
    sys.exit(main())
