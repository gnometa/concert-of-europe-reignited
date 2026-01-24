#!/usr/bin/env python3
"""
Victoria 2 Localisation Line Ending Fixer
==========================================

Fixes CSV files to use Victoria 2's required double carriage return line endings (\r\r\n).

Victoria 2 base game uses \r\r\n (CR+CR+LF) as line endings, not standard \r\n (CRLF).
Without the double carriage return, the CSV parser misaligns columns, causing:
- Country name shifting
- Buttons showing raw keys instead of translations
- General localisation failures

Usage:
    python fix-line-endings.py [path]

Arguments:
    path    Path to localisation folder or specific file
            (default: CoE_RoI_R/localisation/)
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Tuple, List


def fix_file_line_endings(file_path: Path) -> Tuple[bool, str]:
    """
    Fix line endings in a single CSV file.

    Converts:
    - \n (LF) → \r\r\n
    - \r\n (CRLF) → \r\r\n

    Args:
        file_path: Path to the CSV file

    Returns:
        Tuple of (success, message)
    """
    try:
        # Read file as binary to preserve exact content
        with open(file_path, 'rb') as f:
            content = f.read()

        original_size = len(content)

        # First, normalize any existing \r\n to single \n for consistent processing
        # This handles files that might have mixed line endings
        normalized = content.replace(b'\r\n', b'\n')

        # Now convert all \n to \r\r\n (double carriage return + line feed)
        fixed = normalized.replace(b'\n', b'\r\r\n')

        # Remove any accidental triple carriage returns that might have occurred
        fixed = fixed.replace(b'\r\r\r\n', b'\r\r\n')

        new_size = len(fixed)

        # Check if file actually needed fixing
        if fixed == content:
            return True, f"Already correct ({original_size} bytes)"

        # Write fixed content directly (no backup)
        with open(file_path, 'wb') as f:
            f.write(fixed)

        return True, f"Fixed: {original_size} -> {new_size} bytes"

    except Exception as e:
        return False, f"Error: {e}"


def verify_file(file_path: Path) -> bool:
    """
    Verify that a file has correct \r\r\n line endings.

    Args:
        file_path: Path to the CSV file

    Returns:
        True if line endings are correct
    """
    try:
        with open(file_path, 'rb') as f:
            # Read first 10KB to check line endings
            sample = f.read(10240)

        # Check for \r\r\n pattern
        if b'\r\r\n' in sample:
            return True
        return False

    except Exception:
        return False


def main():
    # Determine target path
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent

    if len(sys.argv) > 1:
        target_path = Path(sys.argv[1])
        if not target_path.is_absolute():
            target_path = project_root / target_path
    else:
        target_path = project_root / "CoE_RoI_R" / "localisation"

    print("=" * 60)
    print("Victoria 2 Localisation Line Ending Fixer")
    print("=" * 60)
    print(f"Target: {target_path}")
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
        success, message = fix_file_line_endings(file_path)
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

    # Verify a sample of fixed files
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
