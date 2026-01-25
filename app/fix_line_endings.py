#!/usr/bin/env python3
"""
Fix malformed line endings in Victoria 2 localisation CSV files.

The files have mixed CRLF and CR terminators which cause Victoria 2's
parser to interpret them as empty lines, resulting in label shifting.

This script normalizes all line endings to LF (Unix-style) which
git will convert to CRLF on Windows due to core.autocrlf=true.
"""

from pathlib import Path

def fix_line_endings(filepath: Path) -> int:
    """Fix line endings in a single file."""
    with open(filepath, 'rb') as f:
        content = f.read()

    original = content

    # Replace all line ending variants with LF:
    # 1. CRCRLF (\r\r\n) - the main problem
    # 2. CRLF (\r\n) - standard Windows
    # 3. CR (\r) - old Mac
    # 4. LF (\n) - Unix (keep as is)

    # First, remove extra CRs before CRLF
    content = content.replace(b'\r\r\n', b'\n')
    # Then convert remaining CRLF to LF
    content = content.replace(b'\r\n', b'\n')
    # Finally, convert any remaining standalone CR to LF
    content = content.replace(b'\r', b'\n')

    if content != original:
        with open(filepath, 'wb') as f:
            f.write(content)
        return 1
    return 0

def main():
    localisation_path = Path('CoE_RoI_R/localisation')

    print("=" * 80)
    print("FIXING MALFORMED LINE ENDINGS IN LOCALISATION FILES")
    print("=" * 80)
    print("\nProblem: Files have mixed CRLF/CR terminators that Victoria 2")
    print("         interprets as empty lines, causing label shifting.\n")

    fixed_count = 0
    checked_count = 0

    for filepath in sorted(localisation_path.glob('*.csv')):
        checked_count += 1
        if fix_line_endings(filepath):
            fixed_count += 1
            print(f"  Fixed: {filepath.name}")

    print("\n" + "=" * 80)
    print(f"COMPLETE: Fixed {fixed_count} of {checked_count} files")
    print("=" * 80)

    if fixed_count > 0:
        print("\nLine endings normalized to LF (Unix-style).")
        print("Git will convert to CRLF on Windows (core.autocrlf=true).")

if __name__ == '__main__':
    main()
