#!/usr/bin/env python3
"""
Complete recursive cleanup of cross-file duplicates.
Iteratively removes ALL dead code until no duplicates remain.
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path

def load_all_keys(localisation_path: Path):
    """Load all keys from all files with their priority."""
    files_with_priority = []
    for filepath in sorted(localisation_path.glob('*.csv'), reverse=True):
        files_with_priority.append(filepath)

    # Load all keys: filename -> {key: (line_num, full_row)}
    file_keys = {}
    for filepath in files_with_priority:
        keys = {}
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.reader(f, delimiter=';')
            for line_num, row in enumerate(reader, 1):
                if not row or not row[0]:
                    continue
                key = row[0].strip()
                if key and not key.startswith('#'):
                    keys[key] = (line_num, row)
        file_keys[filepath.name] = keys

    return files_with_priority, file_keys

def find_all_dead_keys(files_with_priority, file_keys):
    """Find ALL keys in lower-priority files that exist in higher-priority files."""
    dead_keys = defaultdict(set)  # filename -> set of keys to remove

    for i, lower_filepath in enumerate(files_with_priority):
        lower_file = lower_filepath.name
        if lower_file not in file_keys:
            continue

        # Check all higher priority files
        for higher_filepath in files_with_priority[:i]:
            higher_file = higher_filepath.name
            if higher_file not in file_keys:
                continue

            # Find keys in lower file that exist in higher file
            for key in file_keys[lower_file].keys():
                if key in file_keys[higher_file]:
                    dead_keys[lower_file].add(key)
                    break  # Found in a higher file, mark for removal

    return dead_keys

def remove_keys_from_file(filepath: Path, keys_to_remove: set) -> int:
    """Remove specified keys from a CSV file."""
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()

    removed_count = 0
    new_lines = []

    for line in lines:
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
    localisation_path = Path('D:\\Steam\\steamapps\\common\\Victoria 2\\mod\\CoE_RoI_R\\localisation')

    print("=" * 80)
    print("COMPLETE RECURSIVE CLEANUP OF CROSS-FILE DUPLICATES")
    print("=" * 80)

    iteration = 0
    total_removed = 0

    while True:
        iteration += 1
        print(f"\n--- Iteration {iteration} ---")

        files_with_priority, file_keys = load_all_keys(localisation_path)
        dead_keys = find_all_dead_keys(files_with_priority, file_keys)

        if not dead_keys:
            print("\nNo more duplicates to remove!")
            break

        total_dead = sum(len(keys) for keys in dead_keys.values())
        print(f"Found {total_dead} dead keys in {len(dead_keys)} files")

        # Remove all dead keys
        iter_removed = 0
        for filename, keys in sorted(dead_keys.items()):
            filepath = localisation_path / filename
            removed = remove_keys_from_file(filepath, keys)
            iter_removed += removed
            if removed > 0:
                print(f"  {filename}: removed {removed} keys")

        total_removed += iter_removed
        print(f"Iteration {iteration} removed: {iter_removed} keys")

        if iter_removed == 0:
            print("\nNo keys removed in this iteration - cleanup complete!")
            break

    print("\n" + "=" * 80)
    print(f"CLEANUP COMPLETE - Total keys removed: {total_removed}")
    print("=" * 80)

    # Final verification
    print("\nRunning final verification...")
    files_with_priority, file_keys = load_all_keys(localisation_path)
    dead_keys = find_all_dead_keys(files_with_priority, file_keys)

    if dead_keys:
        total_remaining = sum(len(keys) for keys in dead_keys.values())
        print(f"WARNING: {total_remaining} duplicates still remain!")
        for filename, keys in sorted(dead_keys.items()):
            print(f"  {filename}: {len(keys)} keys")
    else:
        print("SUCCESS: Zero cross-file duplicates remaining!")

if __name__ == '__main__':
    main()
