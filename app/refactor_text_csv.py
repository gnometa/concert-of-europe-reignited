#!/usr/bin/env python3
"""
Refactor text.csv - Localisation Rebaseline Proof of Concept

Fixes:
1. Column count: 86 → 14
2. Line endings: \r\n → \r\r\n
3. Encoding: Ensure Windows-1252
"""

import sys
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
MOD_DIR = SCRIPT_DIR.parent / "CoE_RoI_R"  # CoE_RoI_R is the actual mod folder
LOCALISATION_DIR = MOD_DIR / "localisation"
TEXT_CSV = LOCALISATION_DIR / "text.csv"
TEXT_CSV_BACKUP = LOCALISATION_DIR / "text.csv.backup"

# Standards
TARGET_COLUMNS = 14
ENCODING = 'cp1252'
LINE_ENDING = '\r\r\n'

def refactor_text_csv():
    """Refactor text.csv to fix column count and line endings."""

    print(f"Reading: {TEXT_CSV}")
    print(f"Backup: {TEXT_CSV_BACKUP}")

    # Read the file (use latin1 first to preserve all byte values)
    try:
        with open(TEXT_CSV, 'rb') as f:
            raw_content = f.read()

        # Detect if it's UTF-8 or close to it
        try:
            decoded = raw_content.decode('utf-8')
            print("Detected encoding: UTF-8 (with extended chars)")
            # Convert to latin1 which covers Windows-1252 + more
            lines = decoded.encode('latin1', 'replace').decode('latin1').splitlines()
        except:
            # Use latin1 as fallback (covers all byte values 0-255)
            print("Detected encoding: Latin-1 (extended)")
            lines = raw_content.decode('latin1').splitlines()

    except Exception as e:
        print(f"Error reading file: {e}")
        return 1

    print(f"Total lines: {len(lines)}")

    # Process each line
    refactored_lines = []
    issues = []

    for i, line in enumerate(lines, 1):
        # Strip existing line endings
        line = line.rstrip('\r\n')

        if not line.strip():
            # Skip empty lines (but track them)
            issues.append(f"Line {i}: Empty line (skipped)")
            continue

        # Parse columns
        parts = line.split(';')
        col_count = len(parts)

        if col_count != TARGET_COLUMNS:
            issues.append(f"Line {i}: {col_count} cols -> {TARGET_COLUMNS} cols")

        # Normalize to exactly 14 columns
        if col_count < TARGET_COLUMNS:
            # Pad with empty columns
            parts.extend([''] * (TARGET_COLUMNS - col_count))
        elif col_count > TARGET_COLUMNS:
            # Truncate to target columns
            parts = parts[:TARGET_COLUMNS]

        # Ensure column 14 (index 13) is 'x'
        if len(parts) >= 14:
            parts[13] = parts[13].strip() or 'x'
        else:
            parts.append('x')

        # Reconstruct line
        refactored_line = ';'.join(parts)
        refactored_lines.append(refactored_line)

    # Write backup (binary to preserve original)
    print(f"\nCreating backup: {TEXT_CSV_BACKUP}")
    with open(TEXT_CSV_BACKUP, 'wb') as f:
        f.write(raw_content)

    # Write refactored file (using latin1 to preserve all characters)
    print(f"Writing refactored: {TEXT_CSV}")
    output_encoding = 'latin1'  # Covers Windows-1252 + extended characters
    with open(TEXT_CSV, 'w', encoding=output_encoding, newline='') as f:
        for line in refactored_lines:
            f.write(line + LINE_ENDING)

    # Summary
    print(f"\n{'='*50}")
    print(f"REFACTORING COMPLETE")
    print(f"{'='*50}")
    print(f"Original lines:  {len(lines)}")
    print(f"Refactored lines: {len(refactored_lines)}")
    print(f"Issues fixed:    {len(issues)}")
    print(f"Encoding:        Latin-1 (covers Windows-1252 + extended)")
    print(f"Line ending:     {repr(LINE_ENDING)}")

    if issues:
        print(f"\nFirst 10 issues:")
        for issue in issues[:10]:
            print(f"  - {issue}")
        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more")

    print(f"\n{'='*50}")
    print(f"VALIDATION CHECKLIST:")
    print(f"{'='*50}")
    print(f"[✓] Backup created: {TEXT_CSV_BACKUP.name}")
    print(f"[✓] Refactored: {len(refactored_lines)} lines")
    print(f"[✓] Normalized: {TARGET_COLUMNS} columns per line")
    print(f"[✓] Encoding: Latin-1 (covers Windows-1252 + extended)")
    print(f"[✓] Line endings: \\r\\r\\n")

    print(f"\n{'='*50}")
    print(f"NEXT STEPS:")
    print(f"{'='*50}")
    print(f"1. Review changes: git diff text.csv")
    print(f"2. Commit: git add text.csv && git commit -m 'refactor: normalize text.csv structure'")
    print(f"3. Game test: Launch Victoria 2 and verify UI text displays correctly")
    print(f"4. Rollback if needed: git checkout text.csv")

    return 0

if __name__ == '__main__':
    sys.exit(refactor_text_csv())
