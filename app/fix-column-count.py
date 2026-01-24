#!/usr/bin/env python3
"""
Victoria 2 Localisation Column Count Fixer
============================================

Fixes CSV files to match Victoria 2's exact 19-column format.

Victoria 2 base game uses exactly 19 columns in CSV files. Many mod files have
extra columns (often 80+), which causes the parser to read across line boundaries,
resulting in:
- Buttons displaying wrong text
- Country names shifting
- General localisation chaos

The correct format is:
Column 1: Key
Column 2: English
Column 3: French
Column 4: German
Column 5: (Reserved/Empty)
Column 6: Spanish
Columns 7-14: (Reserved/Empty)
Column 15: x (terminator)
Columns 16-19: (Empty/Reserved)

Total: 19 columns

Usage:
    python fix-column-count.py [path]
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Tuple, List


TARGET_COLUMNS = 19


def fix_file_column_count(file_path: Path) -> Tuple[bool, str]:
    """
    Fix column count in a single CSV file.

    Args:
        file_path: Path to the CSV file

    Returns:
        Tuple of (success, message)
    """
    try:
        # Read file with binary to preserve exact line endings
        with open(file_path, 'rb') as f:
            content = f.read()

        original_size = len(content)

        # Decode for processing (handle both cp1252 and utf-8)
        try:
            text = content.decode('cp1252')
        except UnicodeDecodeError:
            text = content.decode('utf-8', errors='replace')

        lines = text.split('\n')

        # Preserve the exact line ending from the file
        # Detect line ending from first line that has content
        line_ending = b'\r\r\n'  # Default to Victoria 2 format
        for line in lines[:10]:
            if line.strip():
                # Check what line ending this line originally had
                idx = content.find(line.encode('cp1252', errors='replace'))
                if idx >= 0:
                    # Look ahead to see what follows
                    remaining = content[idx + len(line):]
                    if remaining.startswith(b'\r\r\n'):
                        line_ending = b'\r\r\n'
                    elif remaining.startswith(b'\r\n'):
                        line_ending = b'\r\n'
                    elif remaining.startswith(b'\n'):
                        line_ending = b'\n'
                    break

        fixed_lines = []
        changed = False

        for i, line in enumerate(lines):
            if not line.strip():
                # Preserve empty lines
                fixed_lines.append(line)
                continue

            # Split by semicolon
            parts = line.rstrip('\r\n').split(';')

            if len(parts) == TARGET_COLUMNS:
                # Already correct
                fixed_lines.append(line.rstrip('\r\n'))
                continue

            # Need to fix
            changed = True

            # Strategy: Take first 14 columns, force column 15 to 'x', empty 16-19
            # This ensures correct Victoria 2 format

            # Preserve first 14 columns (key + 9 translations + 4 reserved)
            if len(parts) >= 14:
                new_parts = parts[:14]
            else:
                new_parts = parts[:]
                while len(new_parts) < 14:
                    new_parts.append('')

            # Column 15 MUST be 'x'
            new_parts.append('x')

            # Columns 16-19 must be empty
            while len(new_parts) < TARGET_COLUMNS:
                new_parts.append('')

            fixed_lines.append(';'.join(new_parts))

        if not changed:
            return True, f"Already correct ({len(lines)} lines, {len(parts)} columns)"

        # Re-encode with proper line endings
        fixed_content = line_ending.decode('latin1').join(fixed_lines)
        fixed_bytes = fixed_content.encode('cp1252', errors='replace')

        # Ensure last line also has line ending
        if not fixed_bytes.endswith(line_ending):
            fixed_bytes += line_ending

        new_size = len(fixed_bytes)

        # Write fixed content
        with open(file_path, 'wb') as f:
            f.write(fixed_bytes)

        return True, f"Fixed: {len(lines)} lines, {len(parts)} -> {TARGET_COLUMNS} cols ({original_size} -> {new_size} bytes)"

    except Exception as e:
        return False, f"Error: {e}"


def verify_file(file_path: Path) -> bool:
    """Verify that a file has correct 19-column format."""
    try:
        with open(file_path, 'rb') as f:
            sample = f.read(10240)

        # Decode to check
        try:
            text = sample.decode('cp1252')
        except UnicodeDecodeError:
            text = sample.decode('utf-8', errors='replace')

        lines = text.split('\n')[:5]  # Check first 5 lines

        for line in lines:
            if not line.strip():
                continue
            parts = line.rstrip('\r\n').split(';')
            if len(parts) != TARGET_COLUMNS:
                return False

        return True

    except Exception:
        return False


def main():
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent

    if len(sys.argv) > 1:
        target_path = Path(sys.argv[1])
        if not target_path.is_absolute():
            target_path = project_root / target_path
    else:
        target_path = project_root / "CoE_RoI_R" / "localisation"

    print("=" * 60)
    print("Victoria 2 Localisation Column Count Fixer")
    print("=" * 60)
    print(f"Target: {target_path}")
    print(f"Target columns: {TARGET_COLUMNS}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    if not target_path.exists():
        print(f"ERROR: Path does not exist: {target_path}")
        return 1

    # Collect files
    if target_path.is_file():
        files = [target_path]
    else:
        files = sorted(target_path.glob("*.csv"))

    if not files:
        print("No CSV files found!")
        return 1

    print(f"Found {len(files)} CSV file(s)")
    print()

    # Process files
    results: List[Tuple[Path, bool, str]] = []
    fixed_count = 0
    skipped_count = 0
    error_count = 0

    for file_path in files:
        success, message = fix_file_column_count(file_path)
        results.append((file_path, success, message))

        if success:
            if "Already correct" in message:
                skipped_count += 1
                status = "[OK SKIP]"
            else:
                fixed_count += 1
                status = "[OK FIXED]"
        else:
            error_count += 1
            status = "[ERROR]"

        print(f"[{status}] {file_path.name}")
        if message and "Already correct" not in message:
            print(f"       {message}")
        elif not success:
            print(f"       {message}")

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total files:      {len(files)}")
    print(f"Fixed:            {fixed_count}")
    print(f"Already correct:  {skipped_count}")
    print(f"Errors:           {error_count}")
    print()

    # Verify fixed files
    if fixed_count > 0:
        print("Verifying fixed files...")
        all_verified = True
        for file_path, success, _ in results:
            if success and "Already correct" not in _:
                if verify_file(file_path):
                    print(f"  [OK] {file_path.name}")
                else:
                    print(f"  [FAIL] {file_path.name} - VERIFICATION FAILED!")
                    all_verified = False

        if all_verified:
            print()
            print("[OK] All fixed files verified successfully!")
        else:
            print()
            print("[FAIL] Some files failed verification. Please check manually.")

    print()
    print("Done!")

    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
