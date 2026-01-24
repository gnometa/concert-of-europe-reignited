#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check for duplicate localisation keys across CSV files.

Victoria 2 loads localisation files in reverse lexicographic order (Z->A).
Later files override earlier ones for matching keys. This script identifies:
1. Duplicate keys within the same file (error - causes parsing issues)
2. Duplicate keys across multiple files (warning - later overrides earlier)
"""

import os
import sys
from collections import defaultdict

def parse_csv_keys(filepath):
    """
    Parse a CSV file and extract all localisation keys.

    Args:
        filepath: Path to the CSV file

    Returns:
        Dictionary mapping keys to line numbers where they appear
    """
    keys = defaultdict(list)

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue

                # Extract key (first semicolon-separated field)
                if ';' in line:
                    key = line.split(';', 1)[0].strip()

                    # Skip empty keys
                    if key:
                        keys[key].append(line_num)

        return dict(keys)

    except Exception as e:
        sys.stderr.write("Error parsing {0}: {1}\n".format(filepath, str(e)))
        return {}

def check_duplicates_in_file(filepath):
    """
    Check for duplicate keys within a single file.

    Args:
        filepath: Path to the CSV file

    Returns:
        List of (key, count, line_numbers) tuples for duplicates found
    """
    keys = parse_csv_keys(filepath)
    duplicates = []

    for key, line_numbers in keys.items():
        if len(line_numbers) > 1:
            duplicates.append((key, len(line_numbers), line_numbers))

    return sorted(duplicates, key=lambda x: x[1], reverse=True)

def check_duplicates_across_files(directory):
    """
    Check for duplicate keys across all CSV files.

    Args:
        directory: Path to the localisation directory

    Returns:
        Dictionary mapping keys to list of (filename, line_number) tuples
    """
    csv_files = sorted([f for f in os.listdir(directory) if f.endswith('.csv')], reverse=True)
    all_keys = defaultdict(list)

    for filename in csv_files:
        filepath = os.path.join(directory, filename)
        keys = parse_csv_keys(filepath)

        for key, line_numbers in keys.items():
            for line_num in line_numbers:
                all_keys[key].append((filename, line_num))

    # Filter to only duplicates
    duplicates = {k: v for k, v in all_keys.items() if len(v) > 1}

    return duplicates

def main():
    """Main entry point for the duplicate checker."""
    localisation_dir = r"D:\Steam\steamapps\common\Victoria 2\mod\CoE_RoI_R\localisation"

    if not os.path.exists(localisation_dir):
        sys.stderr.write("Error: Directory not found: {0}\n".format(localisation_dir))
        return 1

    sys.stdout.write("=" * 70 + "\n")
    sys.stdout.write("Victoria 2 Localisation Duplicate Checker\n")
    sys.stdout.write("=" * 70 + "\n")
    sys.stdout.write("\n")

    csv_files = sorted([f for f in os.listdir(localisation_dir) if f.endswith('.csv')], reverse=True)

    if not csv_files:
        sys.stderr.write("Error: No CSV files found in {0}\n".format(localisation_dir))
        return 1

    sys.stdout.write("[1/2] Checking for duplicates WITHIN individual files...\n")
    sys.stdout.write("\n")

    # Check for duplicates within each file
    has_intra_file_duplicates = False
    duplicate_count = 0

    for filename in csv_files:
        filepath = os.path.join(localisation_dir, filename)
        duplicates = check_duplicates_in_file(filepath)

        if duplicates:
            has_intra_file_duplicates = True
            sys.stdout.write("File: {0}\n".format(filename))

            for key, count, line_numbers in duplicates[:10]:  # Show first 10
                sys.stdout.write("  - '{0}' appears {1} times at lines: {2}\n".format(
                    key, count, line_numbers
                ))
                duplicate_count += count - 1

            if len(duplicates) > 10:
                sys.stdout.write("  ... and {0} more duplicates\n".format(len(duplicates) - 10))

            sys.stdout.write("\n")

    if not has_intra_file_duplicates:
        sys.stdout.write("No duplicates found within individual files.\n")
        sys.stdout.write("\n")

    sys.stdout.write("[2/2] Checking for duplicates ACROSS multiple files...\n")
    sys.stdout.write("\n")

    # Check for duplicates across files
    all_duplicates = check_duplicates_across_files(localisation_dir)

    if all_duplicates:
        # Sort by number of occurrences
        sorted_duplicates = sorted(all_duplicates.items(), key=lambda x: len(x[1]), reverse=True)

        sys.stdout.write("Keys appearing in multiple files (later files override earlier):\n")
        sys.stdout.write("\n")

        # Show first 20 most common duplicates
        shown = 0
        for key, locations in sorted_duplicates:
            if shown >= 20:
                remaining = len(sorted_duplicates) - 20
                sys.stdout.write("... and {0} more keys with duplicates\n".format(remaining))
                break

            sys.stdout.write("Key: '{0}' ({1} occurrences)\n".format(key, len(locations)))

            # Group by file
            file_locations = defaultdict(list)
            for filename, line_num in locations:
                file_locations[filename].append(line_num)

            for filename in sorted(file_locations.keys(), reverse=True):
                lines = file_locations[filename]
                if len(lines) == 1:
                    sys.stdout.write("  - {0}: line {1}\n".format(filename, lines[0]))
                else:
                    sys.stdout.write("  - {0}: lines {1}\n".format(filename, lines))

            sys.stdout.write("\n")
            shown += 1

        # Identify problematic cases (same key with different translations)
        sys.stdout.write("\n")
        sys.stdout.write("Checking for conflicting translations...\n")
        sys.stdout.write("\n")

        conflicts_found = False
        for key, locations in sorted_duplicates[:50]:  # Check first 50
            translations = {}

            for filename, line_num in locations:
                filepath = os.path.join(localisation_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        for i, line in enumerate(f, 1):
                            if i == line_num:
                                # Extract translation (second field)
                                parts = line.strip().split(';')
                                if len(parts) >= 2:
                                    translation = parts[1].strip()
                                    if translation:
                                        translations[filename] = translation
                                break
                except:
                    pass

            # Check if translations differ
            unique_translations = set(translations.values())
            if len(unique_translations) > 1:
                conflicts_found = True
                sys.stdout.write("CONFLICT: Key '{0}' has different translations:\n".format(key))
                for filename, translation in translations.items():
                    sys.stdout.write("  - {0}: \"{1}\"\n".format(filename, translation[:50]))
                sys.stdout.write("\n")

        if not conflicts_found:
            sys.stdout.write("No conflicting translations found (all duplicates have identical text).\n")
            sys.stdout.write("\n")

    else:
        sys.stdout.write("No duplicate keys found across files.\n")
        sys.stdout.write("\n")

    sys.stdout.write("=" * 70 + "\n")
    sys.stdout.write("Summary\n")
    sys.stdout.write("=" * 70 + "\n")
    sys.stdout.write("\n")

    if has_intra_file_duplicates:
        sys.stdout.write("[!] CRITICAL: Found duplicates WITHIN files.\n")
        sys.stdout.write("    These can cause parsing issues and should be fixed immediately.\n")
    else:
        sys.stdout.write("[OK] No duplicates found within individual files.\n")

    sys.stdout.write("\n")

    if all_duplicates:
        sys.stdout.write("[INFO] Found {0} duplicate keys ACROSS files.\n".format(len(all_duplicates)))
        sys.stdout.write("    Victoria 2 uses the LAST occurrence (lexicographic order Z->A).\n")
        sys.stdout.write("    Ensure intentional overrides use proper file naming (00_ prefix).\n")
    else:
        sys.stdout.write("[OK] No duplicate keys found across files.\n")

    sys.stdout.write("\n")

    if has_intra_file_duplicates:
        return 1  # Return error code for critical issues
    return 0

if __name__ == '__main__':
    sys.exit(main())
