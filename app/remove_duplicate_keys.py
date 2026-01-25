#!/usr/bin/env python3
"""
Batch remove duplicate keys from a localisation file.

This script removes specified keys from a CSV file, replacing them with comments.
"""

import sys
from pathlib import Path

def remove_keys_from_file(filepath: Path, keys_to_remove: list) -> int:
    """Remove specified keys from a CSV file.

    Args:
        filepath: Path to the CSV file
        keys_to_remove: List of keys to remove

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
        for key in keys_to_remove:
            if line.startswith(f"{key};"):
                should_remove = True
                removed_count += 1
                new_lines.append(f"# {key} removed - overridden by higher priority file\n")
                break

        if not should_remove:
            new_lines.append(line)

    with open(filepath, 'w', encoding='utf-8', errors='replace') as f:
        f.writelines(new_lines)

    return removed_count

def main():
    if len(sys.argv) < 3:
        print("Usage: remove_duplicate_keys.py <filepath> <key1> <key2> ...")
        sys.exit(1)

    filepath = Path(sys.argv[1])
    keys_to_remove = sys.argv[2:]

    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    removed = remove_keys_from_file(filepath, keys_to_remove)
    print(f"Removed {removed} key(s) from {filepath}")

if __name__ == '__main__':
    main()
