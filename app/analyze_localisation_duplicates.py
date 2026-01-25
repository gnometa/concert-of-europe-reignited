#!/usr/bin/env python3
"""
Localisation Duplicate Analysis Tool for Victoria 2 Mods

Analyzes CSV files in the localisation folder to identify:
1. Duplicate keys within the same file
2. Duplicate keys across multiple files
3. Format compliance issues (column count, line endings)

Victoria 2 loads localisation files in reverse lexicographic order (Z→A, 9→0).
Later files override earlier ones for matching keys.
"""

import csv
import os
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple


class LocalisationAnalyser:
    """Analyzes Victoria 2 localisation CSV files for duplicates and issues."""

    # Expected column structure for Victoria 2 CSV
    EXPECTED_COLUMNS = 14

    def __init__(self, localisation_path: str):
        """Initialize the analyser with the path to localisation folder.

        Args:
            localisation_path: Path to the localisation folder
        """
        self.localisation_path = Path(localisation_path)
        self.file_data: Dict[str, List[Tuple[str, List[str], int]]] = {}
        # Keys to files mapping: key -> list of (filename, line_number, english_text)
        self.key_to_files: Dict[str, List[Tuple[str, int, str]]] = defaultdict(list)

    def load_file(self, filepath: Path) -> List[Tuple[str, List[str], int]]:
        """Load a CSV file and return parsed data.

        Args:
            filepath: Path to the CSV file

        Returns:
            List of tuples: (key, columns, line_number)
        """
        data = []
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                reader = csv.reader(f, delimiter=';')
                for line_num, row in enumerate(reader, start=1):
                    if not row:  # Skip empty rows
                        continue
                    if len(row) >= 1:
                        key = row[0].strip()
                        if key:  # Only process rows with a key
                            data.append((key, row, line_num))
        except Exception as e:
            print(f"  Error reading {filepath.name}: {e}", file=sys.stderr)

        return data

    def analyze_all_files(self) -> None:
        """Load and analyze all CSV files in the localisation folder."""
        csv_files = sorted(self.localisation_path.glob('*.csv'), reverse=True)
        print(f"Found {len(csv_files)} CSV files\n")

        for filepath in csv_files:
            print(f"Loading: {filepath.name} ", end='', flush=True)
            data = self.load_file(filepath)
            self.file_data[filepath.name] = data
            print(f"({len(data)} keys)", flush=True)

            # Build cross-file index
            for key, columns, line_num in data:
                english_text = columns[1] if len(columns) > 1 else ""
                self.key_to_files[key].append((filepath.name, line_num, english_text))

    def find_intra_file_duplicates(self) -> Dict[str, List[Tuple[str, int, int, str, str]]]:
        """Find duplicate keys within each individual file.

        Returns:
            Dict mapping filename to list of (key, first_line, duplicate_line, first_text, duplicate_text)
        """
        intra_file_dupes: Dict[str, List[Tuple[str, int, int, str, str]]] = {}

        for filename, data in self.file_data.items():
            key_positions: Dict[str, List[Tuple[int, str]]] = defaultdict(list)

            for key, columns, line_num in data:
                english_text = columns[1] if len(columns) > 1 else ""
                key_positions[key].append((line_num, english_text))

            # Find keys with multiple occurrences
            dupes = []
            for key, positions in key_positions.items():
                if len(positions) > 1:
                    first_line, first_text = positions[0]
                    for dup_line, dup_text in positions[1:]:
                        dupes.append((key, first_line, dup_line, first_text, dup_text))

            if dupes:
                intra_file_dupes[filename] = sorted(dupes, key=lambda x: x[0])

        return intra_file_dupes

    def find_inter_file_duplicates(self) -> List[Tuple[str, List[Tuple[str, int, str]]]]:
        """Find duplicate keys that appear across multiple files.

        Returns:
            List of (key, [(filename, line_number, english_text), ...]) sorted by key
        """
        inter_file_dupes = []

        for key, locations in self.key_to_files.items():
            if len(locations) > 1:
                # Get unique files
                unique_files = {}
                for filename, line_num, text in locations:
                    if filename not in unique_files:
                        unique_files[filename] = (line_num, text)
                if len(unique_files) > 1:
                    # Sort by filename (reverse lexicographic load order)
                    sorted_locations = [
                        (fn, unique_files[fn][0], unique_files[fn][1])
                        for fn in sorted(unique_files.keys(), reverse=True)
                    ]
                    inter_file_dupes.append((key, sorted_locations))

        return sorted(inter_file_dupes, key=lambda x: x[0])

    def check_format_compliance(self) -> Dict[str, List[Tuple[int, str, str]]]:
        """Check for CSV format compliance issues.

        Returns:
            Dict mapping filename to list of (line_number, issue_type, details)
        """
        issues: Dict[str, List[Tuple[int, str, str]]] = defaultdict(list)

        for filename, data in self.file_data.items():
            for key, columns, line_num in data:
                # Check column count
                if len(columns) != self.EXPECTED_COLUMNS:
                    issues[filename].append((
                        line_num,
                        'column_mismatch',
                        f'Expected {self.EXPECTED_COLUMNS} columns, got {len(columns)}'
                    ))

                # Check for empty key
                if not key.strip():
                    issues[filename].append((
                        line_num,
                        'empty_key',
                        'Key is empty or whitespace only'
                    ))

                # Check for missing end marker (column 14 should be 'x')
                if len(columns) >= 14 and columns[13].strip() != 'x':
                    issues[filename].append((
                        line_num,
                        'missing_end_marker',
                        f'End marker should be "x", got "{columns[13]}"'
                    ))

        return dict(issues)

    def get_file_load_order(self) -> List[str]:
        """Return files in load order (last loaded = highest priority).

        Victoria 2 loads in reverse lexicographic order (Z→A, 9→0).
        Files at the end of this list override earlier files.

        Returns:
            List of filenames in load order
        """
        return sorted(self.file_data.keys(), reverse=True)

    def print_summary(self) -> None:
        """Print analysis summary."""
        total_keys = sum(len(data) for data in self.file_data.values())
        unique_keys = len(self.key_to_files)

        print("\n" + "=" * 70)
        print("LOCALISATION ANALYSIS SUMMARY")
        print("=" * 70)
        print(f"Total files:        {len(self.file_data)}")
        print(f"Total entries:      {total_keys:,}")
        print(f"Unique keys:        {unique_keys:,}")
        print(f"Duplicated entries: {total_keys - unique_keys:,}")

        intra_dupes = self.find_intra_file_duplicates()
        inter_dupes = self.find_inter_file_duplicates()

        intra_count = sum(len(dupes) for dupes in intra_dupes.values())
        inter_count = len(inter_dupes)

        print(f"\nDuplicate issues:")
        print(f"  Within files:     {intra_count:,} occurrences in {len(intra_dupes)} files")
        print(f"  Across files:     {inter_count:,} keys in {len(inter_dupes)} files")


def safe_print(text: str, max_len: int = 50) -> str:
    """Safely print text by encoding problematic characters."""
    if not text:
        return ""
    # Replace problematic characters
    clean_text = text.encode('ascii', errors='replace').decode('ascii')
    return clean_text[:max_len]


def print_intra_file_duplicates(analyser: LocalisationAnalyser) -> None:
    """Print duplicate keys found within individual files."""
    dupes = analyser.find_intra_file_duplicates()

    if not dupes:
        print("\n[OK] No duplicate keys found within individual files")
        return

    print("\n" + "=" * 70)
    print("DUPLICATE KEYS WITHIN FILES")
    print("=" * 70)
    print("Note: Later occurrences override earlier ones in the same file\n")

    for filename, file_dupes in sorted(dupes.items()):
        print(f"\n{filename} ({len(file_dupes)} duplicates):")
        for key, first_line, dup_line, first_text, dup_text in file_dupes[:10]:
            print(f"  Key: {key}")
            print(f"    First:  line {first_line}: {safe_print(first_text)}...")
            print(f"    Duplicate: line {dup_line}: {safe_print(dup_text)}...")
        if len(file_dupes) > 10:
            print(f"  ... and {len(file_dupes) - 10} more")


def print_inter_file_duplicates(analyser: LocalisationAnalyser, limit: int = 50) -> None:
    """Print duplicate keys found across multiple files."""
    dupes = analyser.find_inter_file_duplicates()

    if not dupes:
        print("\n[OK] No duplicate keys found across files")
        return

    print("\n" + "=" * 70)
    print("DUPLICATE KEYS ACROSS FILES")
    print("=" * 70)
    print("Note: Files load in reverse lexicographic order (Z->A, 9->0)")
    print("      Last file in each group overrides earlier files\n")

    for key, locations in dupes[:limit]:
        print(f"\nKey: {key}")
        for filename, line_num, text in locations:
            marker = "<- OVERRIDES" if filename == locations[0][0] else ""
            print(f"  {filename:40s} line {line_num:6d} {marker}")
            if text:
                print(f"    {safe_print(text, 60)}...")

    if len(dupes) > limit:
        print(f"\n... and {len(dupes) - limit} more duplicate keys across files")


def print_format_issues(analyser: LocalisationAnalyser) -> None:
    """Print CSV format compliance issues."""
    issues = analyser.check_format_compliance()

    if not issues:
        print("\n[OK] No format compliance issues found")
        return

    print("\n" + "=" * 70)
    print("FORMAT COMPLIANCE ISSUES")
    print("=" * 70)

    for filename, file_issues in sorted(issues.items()):
        print(f"\n{filename} ({len(file_issues)} issues):")
        for line_num, issue_type, details in file_issues[:20]:
            print(f"  Line {line_num:6d} [{issue_type:20s}]: {details}")
        if len(file_issues) > 20:
            print(f"  ... and {len(file_issues) - 20} more issues")


def print_load_order(analyser: LocalisationAnalyser) -> None:
    """Print file load order."""
    order = analyser.get_file_load_order()

    print("\n" + "=" * 70)
    print("FILE LOAD ORDER (highest priority at bottom)")
    print("=" * 70)

    for i, filename in enumerate(order, 1):
        priority = "LOW"
        if filename.startswith('000'):
            priority = "HIGHEST"
        elif filename.startswith('00'):
            priority = "HIGH"
        print(f"{i:3d}. [{priority:8s}] {filename}")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Analyze Victoria 2 localisation files for duplicates and issues'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='D:\\Steam\\steamapps\\common\\Victoria 2\\mod\\CoE_RoI_R\\localisation',
        help='Path to localisation folder'
    )
    parser.add_argument(
        '--intra',
        action='store_true',
        help='Show only within-file duplicates'
    )
    parser.add_argument(
        '--inter',
        action='store_true',
        help='Show only cross-file duplicates'
    )
    parser.add_argument(
        '--format',
        action='store_true',
        help='Show only format issues'
    )
    parser.add_argument(
        '--order',
        action='store_true',
        help='Show only file load order'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=50,
        help='Limit output for cross-file duplicates (default: 50)'
    )

    args = parser.parse_args()

    if not os.path.isdir(args.path):
        print(f"Error: Path not found: {args.path}", file=sys.stderr)
        sys.exit(1)

    print(f"Analyzing localisation files in: {args.path}")
    print("This may take a moment for large folders...\n")

    analyser = LocalisationAnalyser(args.path)
    analyser.analyze_all_files()
    analyser.print_summary()

    # Show requested sections or all if none specified
    show_all = not (args.intra or args.inter or args.format or args.order)

    if show_all or args.intra:
        print_intra_file_duplicates(analyser)

    if show_all or args.inter:
        print_inter_file_duplicates(analyser, limit=args.limit)

    if show_all or args.format:
        print_format_issues(analyser)

    if show_all or args.order:
        print_load_order(analyser)


if __name__ == '__main__':
    main()
