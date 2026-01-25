#!/usr/bin/env python3
"""
Bulk remove duplicate keys from a CSV file.

This script reads a list of keys from a file and removes all matching entries
from the target CSV file.
"""

import sys
from pathlib import Path

def bulk_remove_keys(filepath: Path, keys_to_remove: set) -> int:
    """Remove specified keys from a CSV file.

    Args:
        filepath: Path to the CSV file
        keys_to_remove: Set of keys to remove

    Returns:
        Number of keys removed
    """
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()

    removed_count = 0
    new_lines = []

    for line in lines:
        # Check if this line contains a key to remove
        should_remove = False
        line_key = line.split(';')[0].strip() if line and ';' in line else ''

        if line_key and line_key in keys_to_remove:
            should_remove = True
            removed_count += 1
            # Add comment instead of deleting
            new_lines.append(f"# {line_key} removed - overridden by higher priority file\n")

        if not should_remove:
            new_lines.append(line)

    with open(filepath, 'w', encoding='utf-8', errors='replace') as f:
        f.writelines(new_lines)

    return removed_count

def main():
    if len(sys.argv) < 2:
        print("Usage: bulk_remove_duplicates.py <filepath> <keys_file>")
        print("  filepath: Path to the CSV file to clean")
        print("  keys_file: File containing comma-separated list of keys to remove")
        sys.exit(1)

    filepath = Path(sys.argv[1])
    keys_file = Path(sys.argv[2])

    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    if not keys_file.exists():
        print(f"Error: Keys file not found: {keys_file}")
        sys.exit(1)

    # Read keys from file
    with open(keys_file, 'r', encoding='utf-8') as f:
        content = f.read()
        keys_to_remove = set(key.strip() for key in content.split(','))

    print(f"Removing {len(keys_to_remove)} keys from {filepath}...")
    removed = bulk_remove_keys(filepath, keys_to_remove)
    print(f"Removed {removed} key(s) from {filepath}")

if __name__ == '__main__':
    main()
