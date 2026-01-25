#!/usr/bin/env python3
"""
Generate a clean report of remaining cross-file duplicates without Unicode issues.
"""

import csv
import sys
from collections import defaultdict
from pathlib import Path

def safe_print(text: str) -> str:
    """Convert text to ASCII-safe representation."""
    if not text:
        return ""
    return text.encode('ascii', errors='replace').decode('ascii')

def analyze_duplicates(localisation_path: str):
    """Analyze cross-file duplicates."""
    localisation_path = Path(localisation_path)

    # Build file priority map (reverse lexicographic = later = higher priority)
    files_with_priority = []
    for filepath in sorted(localisation_path.glob('*.csv'), reverse=True):
        files_with_priority.append((filepath.name, filepath))

    print(f"File Load Order (Highest to Lowest Priority):")
    print("=" * 60)
    for i, (name, _) in enumerate(files_with_priority[:20], 1):
        print(f"  {i:2d}. {name}")
    print(f"  ... and {len(files_with_priority) - 20} more files\n")

    # Load all keys by file
    file_keys = {}  # filename -> {key: (line_num, english_text)}
    for filename, filepath in files_with_priority:
        keys = {}
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.reader(f, delimiter=';')
            for line_num, row in enumerate(reader, 1):
                if not row or not row[0]:
                    continue
                key = row[0].strip()
                if key and not key.startswith('#'):
                    english = row[1] if len(row) > 1 else ""
                    keys[key] = (line_num, safe_print(english[:40]))
        file_keys[filename] = keys

    # Find cross-file duplicates (lower priority files with keys in higher priority files)
    duplicates = defaultdict(list)  # filename -> [(key, higher_file, line_num, text)]

    for i, (lower_file, _) in enumerate(files_with_priority):
        # Check all higher priority files
        for higher_file, _ in files_with_priority[:i]:
            for key, (line_num, text) in file_keys[lower_file].items():
                if key in file_keys[higher_file]:
                    duplicates[lower_file].append((key, higher_file, line_num, text))
                    break  # Only report once per key

    # Print report
    print("=" * 80)
    print("CROSS-FILE DUPLICATES BY FILE (Lower Priority Files)")
    print("=" * 80)
    print("\nFormat: KEY in [filename] overrides [lower_file]\n")

    total_duplicates = 0
    for filename in sorted(duplicates.keys()):
        dup_list = duplicates[filename]
        total_duplicates += len(dup_list)
        print(f"\n{filename}: {len(dup_list)} duplicate keys to remove")
        print("-" * 60)

        # Group by overriding file
        by_overrider = defaultdict(list)
        for key, overrider, line_num, text in dup_list:
            by_overrider[overrider].append((key, line_num, text))

        for overrider in sorted(by_overrider.keys()):
            keys = by_overrider[overrider]
            print(f"  Overridden by {overrider}: {len(keys)} keys")
            for key, line_num, text in sorted(keys)[:15]:
                print(f"    {key:40s} (line {line_num:5d}): {safe_print(text)}")
            if len(keys) > 15:
                print(f"    ... and {len(keys) - 15} more")

    print("\n" + "=" * 80)
    print(f"TOTAL CROSS-FILE DUPLICATES: {total_duplicates}")
    print("=" * 80)

    # Generate removal list
    print("\n" + "=" * 80)
    print("GENERATING REMOVAL LISTS FOR EACH FILE")
    print("=" * 80)

    for filename in sorted(duplicates.keys()):
        dup_list = duplicates[filename]
        keys_to_remove = [key for key, _, _, _ in dup_list]

        output_file = Path("app") / f"remove_{filename.replace('.csv', '')}_keys.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(','.join(sorted(keys_to_remove)))
        print(f"  Created: {output_file} ({len(keys_to_remove)} keys)")

if __name__ == '__main__':
    analyze_duplicates('D:\\Steam\\steamapps\\common\\Victoria 2\\mod\\CoE_RoI_R\\localisation')
