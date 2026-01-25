#!/usr/bin/env python3
"""
Find all keys in text.csv that are duplicated in other files.

This helps identify which entries should be removed from text.csv
since it has the lowest load priority.
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path

def find_text_csv_duplicates(localisation_path: str):
    """Find all keys in text.csv that exist in other files."""
    localisation_path = Path(localisation_path)

    # Load all files except text.csv
    file_data = {}
    for filepath in sorted(localisation_path.glob('*.csv'), reverse=True):
        if filepath.name == 'text.csv':
            continue
        data = []
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.reader(f, delimiter=';')
            for row in reader:
                if not row or not row[0]:
                    continue
                key = row[0].strip()
                if key and not key.startswith('#'):
                    data.append(key)
        file_data[filepath.name] = set(data)

    # Load text.csv
    text_keys = []
    with open(localisation_path / 'text.csv', 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            if not row or not row[0]:
                continue
            key = row[0].strip()
            if key and not key.startswith('#'):
                text_keys.append((key, row))

    # Find duplicates
    duplicates = []
    for key, row in text_keys:
        for filename, keys in file_data.items():
            if key in keys:
                duplicates.append((key, filename))
                break

    return duplicates

def main():
    localisation_path = 'D:\\Steam\\steamapps\\common\\Victoria 2\\mod\\CoE_RoI_R\\localisation'

    print("Finding text.csv duplicates...")
    duplicates = find_text_csv_duplicates(localisation_path)

    print(f"Found {len(duplicates)} duplicate keys in text.csv")
    print("\nKeys to remove from text.csv:")

    # Group by file for better organization
    by_file = defaultdict(list)
    for key, filename in duplicates:
        by_file[filename].append(key)

    for filename, keys in sorted(by_file.items()):
        print(f"\n{filename}: {len(keys)} keys")
        for key in sorted(keys[:10]):
            print(f"  {key}")
        if len(keys) > 10:
            print(f"  ... and {len(keys) - 10} more")

    # Output as comma-separated list for batch removal
    print("\n\nAll keys (comma-separated for batch removal):")
    all_keys = [key for key, _ in duplicates]
    print(','.join(sorted(all_keys)))

if __name__ == '__main__':
    main()
