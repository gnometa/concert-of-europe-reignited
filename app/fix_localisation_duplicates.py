#!/usr/bin/env python3
"""
Localisation Duplicate Fixer for Victoria 2 Mods

Automatically fixes duplicate localisation keys:
1. Removes within-file duplicates (keeps first occurrence)
2. Removes comment key duplicates across files
3. Generates reports for manual review

For cross-file value conflicts, creates a report for manual resolution.
"""

import argparse
import csv
import os
import sys
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional


def safe_print(text: str, max_len: int = 60) -> str:
    """Safely print text by encoding problematic characters."""
    if not text:
        return ""
    # Replace problematic characters
    clean_text = text.encode('ascii', errors='replace').decode('ascii')
    return clean_text[:max_len]


class LocalisationFixer:
    """Fixes duplicate localisation keys in Victoria 2 CSV files."""

    EXPECTED_COLUMNS = 14

    def __init__(self, localisation_path: str, dry_run: bool = False):
        """Initialize the fixer.

        Args:
            localisation_path: Path to localisation folder
            dry_run: If True, don't modify files, just report
        """
        self.localisation_path = Path(localisation_path)
        self.dry_run = dry_run
        self.file_data: Dict[str, List[Tuple[str, List[str], int]]] = {}
        self.key_to_files: Dict[str, List[Tuple[str, int, str]]] = defaultdict(list)

    def load_file(self, filepath: Path) -> List[Tuple[str, List[str], int]]:
        """Load a CSV file and return parsed data."""
        data = []
        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                reader = csv.reader(f, delimiter=';')
                for line_num, row in enumerate(reader, start=1):
                    if not row:
                        continue
                    if len(row) >= 1:
                        key = row[0].strip()
                        if key:
                            data.append((key, row, line_num))
        except Exception as e:
            print(f"  Error reading {filepath.name}: {e}", file=sys.stderr)

        return data

    def analyze_all_files(self) -> None:
        """Load and analyze all CSV files."""
        csv_files = sorted(self.localisation_path.glob('*.csv'), reverse=True)
        print(f"Found {len(csv_files)} CSV files\n")

        for filepath in csv_files:
            print(f"Loading: {filepath.name} ", end='', flush=True)
            data = self.load_file(filepath)
            self.file_data[filepath.name] = data

            for key, columns, line_num in data:
                english_text = columns[1] if len(columns) > 1 else ""
                self.key_to_files[key].append((filepath.name, line_num, english_text))

            print(f"({len(data)} keys)", flush=True)

    def fix_within_file_duplicates(self, filename: str) -> Tuple[List[Tuple[int, str]], List[str]]:
        """Remove duplicate keys within a single file.

        Args:
            filename: Name of file to fix

        Returns:
            (removed_lines, warning_messages)
        """
        if filename not in self.file_data:
            return [], []

        data = self.file_data[filename]
        seen_keys: Dict[str, int] = {}  # key -> index in data list
        indices_to_remove: Set[int] = set()
        warnings: List[str] = []

        # Find duplicates (keep first occurrence)
        for data_idx, (key, columns, line_num) in enumerate(data):
            if key in seen_keys:
                indices_to_remove.add(data_idx)
                first_idx = seen_keys[key]
                first_key, first_columns, first_line = data[first_idx]
                first_text = first_columns[1] if len(first_columns) > 1 else ""
                dup_text = columns[1] if len(columns) > 1 else ""

                if first_text != dup_text:
                    warnings.append(
                        f"Line {line_num}: Key '{safe_print(key)}' has different value than line {first_line}"
                        f"  First:  {safe_print(first_text)}..."
                        f"  Duplicate: {safe_print(dup_text)}..."
                    )
            else:
                seen_keys[key] = data_idx

        removed = [(line_num, columns[1] if len(columns) > 1 else "")
                   for data_idx, (key, columns, line_num) in enumerate(data)
                   if data_idx in indices_to_remove]

        return removed, warnings

    def fix_file_format(self, filename: str) -> Tuple[List[Tuple[int, str, str]], List[str]]:
        """Fix format issues in a CSV file.

        Args:
            filename: Name of file to fix

        Returns:
            (fixes_applied, warning_messages)
        """
        if filename not in self.file_data:
            return [], []

        data = self.file_data[filename]
        fixes: List[Tuple[int, str, str]] = []  # (line_num, issue, fix_description)
        warnings: List[str] = []

        for key, columns, line_num in data:
            # Check for column count issues
            if len(columns) > self.EXPECTED_COLUMNS:
                fixes.append((
                    line_num,
                    f"column_count_{len(columns)}",
                    f"Truncate from {len(columns)} to {self.EXPECTED_COLUMNS} columns"
                ))
            elif len(columns) < self.EXPECTED_COLUMNS:
                # Pad with empty fields
                fixes.append((
                    line_num,
                    f"column_count_{len(columns)}",
                    f"Pad from {len(columns)} to {self.EXPECTED_COLUMNS} columns"
                ))

            # Check for trailing commas/extra data
            if len(columns) > self.EXPECTED_COLUMNS and columns[self.EXPECTED_COLUMNS - 1] != 'x':
                fixes.append((
                    line_num,
                    "trailing_data",
                    f"Remove extra data after column {self.EXPECTED_COLUMNS}"
                ))

        return fixes, warnings

    def apply_file_fixes(self, filename: str,
                        lines_to_remove: Set[int],
                        format_fixes: List[Tuple[int, str, str]]) -> bool:
        """Apply fixes to a file.

        Args:
            filename: Name of file to fix
            lines_to_remove: Set of line numbers to remove
            format_fixes: List of format fixes to apply

        Returns:
            True if successful, False otherwise
        """
        filepath = self.localisation_path / filename

        if self.dry_run:
            print(f"  [DRY RUN] Would fix: {filename}")
            return True

        # Read original file
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()

        # Apply fixes
        fixed_lines = []
        for i, line in enumerate(lines, start=1):
            if i in lines_to_remove:
                continue

            # Apply format fixes
            for line_num, issue, desc in format_fixes:
                if line_num == i:
                    # Parse and fix the line
                    parts = line.rstrip('\n\r').split(';')
                    if len(parts) > self.EXPECTED_COLUMNS:
                        # Truncate
                        parts = parts[:self.EXPECTED_COLUMNS]
                    elif len(parts) < self.EXPECTED_COLUMNS:
                        # Pad
                        parts += [''] * (self.EXPECTED_COLUMNS - len(parts))

                    # Ensure end marker
                    if len(parts) >= self.EXPECTED_COLUMNS:
                        parts[self.EXPECTED_COLUMNS - 1] = 'x'

                    line = ';'.join(parts) + '\n'

            fixed_lines.append(line)

        # Write back
        with open(filepath, 'w', encoding='utf-8', errors='replace') as f:
            f.writelines(fixed_lines)

        return True

    def get_comment_key_duplicates(self) -> List[Tuple[str, List[Tuple[str, int]]]]:
        """Find comment key duplicates across files.

        Returns:
            List of (key, [(filename, line_num), ...])
        """
        comment_keys = [k for k in self.key_to_files.keys()
                       if k.startswith('#') or k.strip() == '']

        duplicates = []
        for key in comment_keys:
            if len(self.key_to_files[key]) > 1:
                # Group by filename
                file_locations: Dict[str, int] = {}
                for filename, line_num, _ in self.key_to_files[key]:
                    if filename not in file_locations:
                        file_locations[filename] = line_num
                duplicates.append((key, sorted(
                    [(fn, file_locations[fn]) for fn in file_locations.keys()],
                    key=lambda x: x[0], reverse=True
                )))

        return sorted(duplicates, key=lambda x: x[0])

    def generate_cross_file_report(self) -> str:
        """Generate a report of cross-file duplicates that need manual review.

        Returns:
            Report text
        """
        report_lines = ["# Cross-File Duplicate Report\n"]
        report_lines.append("Generated by localisation duplicate fixer\n")

        # Group duplicates by file pairs
        file_pair_dupes: Dict[Tuple[str, str], List[Tuple[str, str, str]]] = defaultdict(list)

        for key, locations in self.key_to_files.items():
            if len(locations) > 1:
                # Sort by filename (priority order)
                sorted_locations = sorted(locations, key=lambda x: x[0], reverse=True)

                # Check if values differ
                highest_file, highest_line, highest_value = sorted_locations[0]
                all_same = all(loc[2] == highest_value for loc in sorted_locations)

                if not all_same:
                    for i in range(1, len(sorted_locations)):
                        other_file, other_line, other_value = sorted_locations[i]
                        pair_key = tuple(sorted([highest_file, other_file], reverse=True))
                        file_pair_dupes[pair_key].append((key, highest_value, other_value))

        # Generate report by file pair
        for (file1, file2), dupes in sorted(file_pair_dupes.items()):
            report_lines.append(f"\n## {file1} vs {file2}\n")
            report_lines.append(f"{len(dupes)} conflicting keys\n\n")

            for key, val1, val2 in dupes[:20]:  # Limit to 20 per pair
                report_lines.append(f"### {key}\n")
                report_lines.append(f"- **{file1}**: {val1[:80]}...\n")
                report_lines.append(f"- **{file2}**: {val2[:80]}...\n")

            if len(dupes) > 20:
                report_lines.append(f"\n... and {len(dupes) - 20} more\n")

        return '\n'.join(report_lines)


def main():
    parser = argparse.ArgumentParser(
        description='Fix duplicate localisation keys in Victoria 2 CSV files'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='D:\\Steam\\steamapps\\common\\Victoria 2\\mod\\CoE_RoI_R\\localisation',
        help='Path to localisation folder'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be changed without modifying files'
    )
    parser.add_argument(
        '--fix-within',
        action='store_true',
        help='Fix within-file duplicates'
    )
    parser.add_argument(
        '--fix-format',
        action='store_true',
        help='Fix format issues (column counts, end markers)'
    )
    parser.add_argument(
        '--fix-comments',
        action='store_true',
        help='Remove duplicate comment keys (highest priority only)'
    )
    parser.add_argument(
        '--report',
        action='store_true',
        help='Generate cross-file duplicate report'
    )
    parser.add_argument(
        '--output',
        default='localisation_duplicate_report.md',
        help='Output file for report (default: localisation_duplicate_report.md)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Apply all automatic fixes'
    )

    args = parser.parse_args()

    if not os.path.isdir(args.path):
        print(f"Error: Path not found: {args.path}", file=sys.stderr)
        sys.exit(1)

    print("=" * 70)
    print("LOCALISATION DUPLICATE FIXER")
    print("=" * 70)

    if args.dry_run:
        print("DRY RUN MODE - No files will be modified\n")

    fixer = LocalisationFixer(args.path, dry_run=args.dry_run)
    fixer.analyze_all_files()

    if args.report or args.all:
        print("\nGenerating cross-file duplicate report...")
        report = fixer.generate_cross_file_report()
        report_path = Path(args.output)

        if not args.dry_run:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Report saved to: {report_path}")
        else:
            print("[DRY RUN] Would save report to:", report_path)

    if args.fix_within or args.all:
        print("\n" + "=" * 70)
        print("FIXING WITHIN-FILE DUPLICATES")
        print("=" * 70)

        for filename in sorted(fixer.file_data.keys()):
            removed, warnings = fixer.fix_within_file_duplicates(filename)

            if removed:
                print(f"\n{filename}: {len(removed)} duplicate(s) removed")
                for line_num, text in removed[:5]:
                    print(f"  Line {line_num}: {safe_print(text)}...")
                if len(removed) > 5:
                    print(f"  ... and {len(removed) - 5} more")

            if warnings:
                print(f"\n{filename}: {len(warnings)} warning(s)")
                for warning in warnings:
                    print(f"  {safe_print(warning, 200)}")

            if not args.dry_run and (removed or warnings):
                fixer.apply_file_fixes(filename, set(line for line, _ in removed), [])

    if args.fix_format or args.all:
        print("\n" + "=" * 70)
        print("FIXING FORMAT ISSUES")
        print("=" * 70)

        for filename in sorted(fixer.file_data.keys()):
            fixes, warnings = fixer.fix_file_format(filename)

            if fixes:
                print(f"\n{filename}: {len(fixes)} format fix(es)")
                for line_num, issue, desc in fixes[:10]:
                    print(f"  Line {line_num}: {desc}")
                if len(fixes) > 10:
                    print(f"  ... and {len(fixes) - 10} more")

            if not args.dry_run and fixes:
                fixer.apply_file_fixes(filename, set(), fixes)

    if args.fix_comments or args.all:
        print("\n" + "=" * 70)
        print("DUPLICATE COMMENT KEYS (manual review recommended)")
        print("=" * 70)

        comment_dupes = fixer.get_comment_key_duplicates()
        for key, locations in comment_dupes[:20]:
            print(f"\nKey: {key}")
            for filename, line_num in locations:
                marker = "<- KEEP" if filename == locations[0][0] else "<- REMOVE"
                print(f"  {filename:40s} line {line_num:6d} {marker}")

        if len(comment_dupes) > 20:
            print(f"\n... and {len(comment_dupes) - 20} more comment key duplicates")

    print("\n" + "=" * 70)
    print("COMPLETE")
    print("=" * 70)

    if args.dry_run:
        print("\nDry run complete. No files were modified.")
        print("Re-run without --dry-run to apply fixes.")


if __name__ == '__main__':
    main()
