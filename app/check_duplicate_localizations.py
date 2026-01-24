#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check for duplicate localisation keys across CSV files.

Victoria 2 loads localisation files in reverse lexicographic order (Z->A).
Later files override earlier ones for matching keys.
"""

import os
import sys
import argparse
from collections import defaultdict

def parse_csv_keys(filepath):
    """
    Parse a CSV file and extract all localisation keys.
    """
    keys = defaultdict(list)

    try:
        # Use Windows-1252 encoding standard for Vic2
        with open(filepath, 'r', encoding='windows-1252', errors='replace') as f:
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
        sys.stderr.write(f"Error parsing {filepath}: {e}\n")
        return {}

def check_duplicates_in_file(filepath):
    """
    Check for duplicate keys within a single file.
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
    parser = argparse.ArgumentParser(description="Check for duplicate localisation keys in Victoria 2 mod.")
    parser.add_argument("directory", nargs="?", help="Path to localisation directory (default: detects relative path)")
    args = parser.parse_args()

    # Determine directory
    localisation_dir = args.directory
    if not localisation_dir:
         # Try to find directory relative to script location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        potential_path = os.path.join(script_dir, "..", "CoE_RoI_R", "localisation")
        potential_path = os.path.abspath(potential_path)
        
        if os.path.exists(potential_path):
            localisation_dir = potential_path
        else:
            localisation_dir = "."

    if not os.path.exists(localisation_dir):
        sys.stderr.write(f"Error: Directory not found: {localisation_dir}\n")
        return 1

    sys.stdout.write("=" * 70 + "\n")
    sys.stdout.write("Victoria 2 Localisation Duplicate Checker\n")
    sys.stdout.write("=" * 70 + "\n")
    sys.stdout.write(f"Scanning directory: {localisation_dir}\n\n")

    csv_files = sorted([f for f in os.listdir(localisation_dir) if f.endswith('.csv')], reverse=True)

    if not csv_files:
        sys.stderr.write(f"Error: No CSV files found in {localisation_dir}\n")
        return 1

    sys.stdout.write("[1/2] Checking for duplicates WITHIN individual files...\n\n")

    # Check for duplicates within each file
    has_intra_file_duplicates = False
    
    for filename in csv_files:
        filepath = os.path.join(localisation_dir, filename)
        duplicates = check_duplicates_in_file(filepath)

        if duplicates:
            has_intra_file_duplicates = True
            sys.stdout.write(f"File: {filename}\n")

            for key, count, line_numbers in duplicates[:10]:  # Show first 10
                sys.stdout.write(f"  - '{key}' appears {count} times at lines: {line_numbers}\n")

            if len(duplicates) > 10:
                sys.stdout.write(f"  ... and {len(duplicates) - 10} more duplicates\n")

            sys.stdout.write("\n")

    if not has_intra_file_duplicates:
        sys.stdout.write("No duplicates found within individual files.\n\n")

    sys.stdout.write("[2/2] Checking for duplicates ACROSS multiple files...\n\n")

    # Check for duplicates across files
    all_duplicates = check_duplicates_across_files(localisation_dir)

    if all_duplicates:
        # Sort by number of occurrences
        sorted_duplicates = sorted(all_duplicates.items(), key=lambda x: len(x[1]), reverse=True)

        sys.stdout.write("Keys appearing in multiple files (later files override earlier):\n\n")

        # Show first 20 most common duplicates
        shown = 0
        for key, locations in sorted_duplicates:
            if shown >= 20:
                remaining = len(sorted_duplicates) - 20
                sys.stdout.write(f"... and {remaining} more keys with duplicates\n")
                break

            sys.stdout.write(f"Key: '{key}' ({len(locations)} occurrences)\n")

            # Group by file
            file_locations = defaultdict(list)
            for filename, line_num in locations:
                file_locations[filename].append(line_num)

            for filename in sorted(file_locations.keys(), reverse=True):
                lines = file_locations[filename]
                lines_str = f"lines {lines}" if len(lines) > 1 else f"line {lines[0]}"
                sys.stdout.write(f"  - {filename}: {lines_str}\n")

            sys.stdout.write("\n")
            shown += 1

    else:
        sys.stdout.write("No duplicate keys found across files.\n\n")

    sys.stdout.write("=" * 70 + "\n")
    sys.stdout.write("Summary\n")
    sys.stdout.write("=" * 70 + "\n\n")

    if has_intra_file_duplicates:
        sys.stdout.write("[!] CRITICAL: Found duplicates WITHIN files.\n")
        sys.stdout.write("    These can cause parsing issues and should be fixed immediately.\n")
    else:
        sys.stdout.write("[OK] No duplicates found within individual files.\n")

    if all_duplicates:
        sys.stdout.write(f"\n[INFO] Found {len(all_duplicates)} duplicate keys ACROSS files.\n")
    else:
        sys.stdout.write("\n[OK] No duplicate keys found across files.\n")

    sys.stdout.write("\n")

    if has_intra_file_duplicates:
        return 1  # Return error code for critical issues
    return 0

if __name__ == '__main__':
    sys.exit(main())
