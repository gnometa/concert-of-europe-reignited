#!/usr/bin/env python3
"""
Victoria 2 CSV Structure Fixer
==============================

Forces all CSV files to match Victoria 2's exact column structure:
- Columns 1-14: Content (key, translations, etc.)
- Column 15: x (terminator)
- Columns 16-19: Empty

This is the ONLY format Victoria 2 accepts.
"""

import sys
from pathlib import Path


def fix_csv_file(file_path: Path) -> bool:
    """Fix a single CSV file to exact Victoria 2 format."""
    try:
        # Read as binary to preserve encoding
        with open(file_path, 'rb') as f:
            content = f.read()

        # Decode (try cp1252 first, then utf-8)
        try:
            text = content.decode('cp1252')
        except UnicodeDecodeError:
            text = content.decode('utf-8', errors='replace')

        lines = text.split('\n')
        fixed_lines = []

        for line in lines:
            if not line.strip():
                # Keep empty lines
                fixed_lines.append('')
                continue

            # Split by semicolon
            parts = line.rstrip('\r\n').split(';')

            # Remove any existing 'x' terminators from the content
            # We'll enforce our own structure
            clean_parts = []
            for part in parts:
                if part.strip() == 'x':
                    # Skip 'x' values - they're terminators in wrong places
                    if not clean_parts:
                        # But keep 'x' if it's the first column (unlikely but possible)
                        clean_parts.append(part)
                    # Otherwise skip it
                else:
                    clean_parts.append(part)

            # Enforce exact structure: 14 content columns, then 'x', then 4 empty columns
            # Take first 14 columns (or pad if fewer)
            if len(clean_parts) >= 14:
                new_parts = clean_parts[:14]
            else:
                new_parts = clean_parts[:]
                while len(new_parts) < 14:
                    new_parts.append('')

            # Column 15 MUST be 'x'
            new_parts.append('x')

            # Columns 16-19 must be empty
            while len(new_parts) < 19:
                new_parts.append('')

            fixed_lines.append(';'.join(new_parts))

        # Re-encode with Victoria 2 line endings (\r\r\n)
        fixed_content = '\r\r\n'.join(fixed_lines)

        # Ensure file ends with line ending
        if not fixed_content.endswith('\r\r\n'):
            fixed_content += '\r\r\n'

        # Write back
        with open(file_path, 'wb') as f:
            f.write(fixed_content.encode('cp1252', errors='replace'))

        return True

    except Exception as e:
        print(f"  ERROR processing {file_path.name}: {e}")
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
    print("Victoria 2 CSV Structure Fixer")
    print("=" * 60)
    print(f"Target: {target_path}")
    print()

    if not target_path.exists():
        print(f"ERROR: Path not found: {target_path}")
        return 1

    # Collect CSV files
    if target_path.is_file():
        files = [target_path]
    else:
        files = sorted(target_path.glob("*.csv"))

    if not files:
        print("No CSV files found!")
        return 1

    print(f"Processing {len(files)} file(s)...")
    print()

    fixed = 0
    for file_path in files:
        if fix_csv_file(file_path):
            print(f"  [OK] {file_path.name}")
            fixed += 1
        else:
            print(f"  [FAIL] {file_path.name}")

    print()
    print(f"Done! Fixed {fixed} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
