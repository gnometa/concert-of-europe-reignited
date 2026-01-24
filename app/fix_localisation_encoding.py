#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix localisation encoding issues for Victoria 2 mod CoE_RoI_R.

Victoria 2 requires Windows-1252 (ANSI) encoding, not UTF-8.
This script converts UTF-8 files to Windows-1252 and normalizes line endings.
"""

import os
import sys

def convert_utf8_to_ansi(input_file, output_file=None):
    """
    Convert a UTF-8 encoded CSV file to Windows-1252 (ANSI) encoding.

    Args:
        input_file: Path to the input UTF-8 file
        output_file: Path to the output ANSI file (defaults to overwriting input)

    Returns:
        True if successful, False otherwise
    """
    if output_file is None:
        output_file = input_file

    try:
        # Read as UTF-8
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove any BOM if present
        if content.startswith('\ufeff'):
            content = content[1:]

        # Normalize line endings to CRLF
        content = content.replace('\r\n', '\n')  # First normalize to LF
        content = content.replace('\n', '\r\n')   # Then convert to CRLF

        # Write as Windows-1252
        with open(output_file, 'w', encoding='windows-1252', newline='') as f:
            f.write(content)

        sys.stdout.write("[OK] Converted: {0} -> Windows-1252 (ANSI)\n".format(input_file))
        return True

    except UnicodeEncodeError as e:
        sys.stdout.write("[X] Encoding error in {0}: {1}\n".format(input_file, str(e)))
        sys.stdout.write("  Character position: {0}\n".format(e.start))
        try:
            problem_text = e.object[e.start:e.end].encode('ascii', 'replace').decode('ascii')
            sys.stdout.write("  Problematic text: {0}\n".format(repr(problem_text)))
        except:
            pass
        try:
            context = e.object[max(0, e.start-20):e.start+20].encode('ascii', 'replace').decode('ascii')
            sys.stdout.write("  Context: {0}\n".format(repr(context)))
        except:
            pass
        print()
        print(f"  This file contains characters that cannot be converted to Windows-1252.")
        print(f"  Common issues: Japanese text, emojis, or special Unicode characters.")
        print(f"  Solution: Edit the file to remove or replace these characters.")
        return False
    except Exception as e:
        print(f"✗ Error processing {input_file}: {e}")
        return False

def fix_line_endings(input_file, output_file=None):
    """
    Normalize line endings in a CSV file to CRLF (Windows standard).

    Args:
        input_file: Path to the input file
        output_file: Path to the output file (defaults to overwriting input)

    Returns:
        True if successful, False otherwise
    """
    if output_file is None:
        output_file = input_file

    try:
        # Read in binary mode to detect line endings
        with open(input_file, 'rb') as f:
            content = f.read()

        # Normalize line endings
        # Replace any CRLF with LF first
        content = content.replace(b'\r\n', b'\n')
        # Then replace all LF with CRLF
        content = content.replace(b'\n', b'\r\n')

        # Write back
        with open(output_file, 'wb') as f:
            f.write(content)

        sys.stdout.write("[OK] Normalized line endings: {0}\n".format(input_file))
        return True

    except Exception as e:
        sys.stdout.write("[X] Error processing {0}: {1}\n".format(input_file, str(e)))
        return False

def main():
    """Main entry point for the script."""
    localisation_dir = r"D:\Steam\steamapps\common\Victoria 2\mod\CoE_RoI_R\localisation"

    if not os.path.exists(localisation_dir):
        sys.stdout.write("[X] Directory not found: {0}\n".format(localisation_dir))
        return 1

    sys.stdout.write("=" * 70 + "\n")
    sys.stdout.write("Victoria 2 Localisation Encoding Fix Tool\n")
    sys.stdout.write("=" * 70 + "\n")
    sys.stdout.write("\n")

    # Files that need encoding conversion (UTF-8 -> Windows-1252)
    encoding_fixes = [
        "0000_economic_rework.csv",
    ]

    # Files that need line ending normalization
    line_ending_fixes = [
        "text.csv",
    ]

    success_count = 0
    total_count = len(encoding_fixes) + len(line_ending_fixes)

    # Process encoding fixes
    if encoding_fixes:
        sys.stdout.write("[1/2] Converting UTF-8 files to Windows-1252 (ANSI)...\n")
        sys.stdout.write("\n")

        for filename in encoding_fixes:
            filepath = os.path.join(localisation_dir, filename)

            if not os.path.exists(filepath):
                sys.stdout.write("[X] File not found: {0}\n".format(filename))
                continue

            # Create backup
            backup_path = filepath + '.utf8.backup'
            try:
                with open(filepath, 'rb') as src, open(backup_path, 'wb') as dst:
                    dst.write(src.read())
                sys.stdout.write("  Created backup: {0}\n".format(os.path.basename(backup_path)))
            except:
                sys.stdout.write("  Warning: Could not create backup for {0}\n".format(filename))

            if convert_utf8_to_ansi(filepath):
                success_count += 1

        sys.stdout.write("\n")

    # Process line ending fixes
    if line_ending_fixes:
        sys.stdout.write("[2/2] Normalizing line endings to CRLF...\n")
        sys.stdout.write("\n")

        for filename in line_ending_fixes:
            filepath = os.path.join(localisation_dir, filename)

            if not os.path.exists(filepath):
                sys.stdout.write("[X] File not found: {0}\n".format(filename))
                continue

            # Create backup
            backup_path = filepath + '.lf.backup'
            try:
                with open(filepath, 'rb') as src, open(backup_path, 'wb') as dst:
                    dst.write(src.read())
                sys.stdout.write("  Created backup: {0}\n".format(os.path.basename(backup_path)))
            except:
                sys.stdout.write("  Warning: Could not create backup for {0}\n".format(filename))

            if fix_line_endings(filepath):
                success_count += 1

        sys.stdout.write("\n")

    sys.stdout.write("=" * 70 + "\n")
    sys.stdout.write("Summary: {0}/{1} files processed successfully\n".format(success_count, total_count))
    sys.stdout.write("=" * 70 + "\n")

    if success_count == total_count:
        sys.stdout.write("\n")
        sys.stdout.write("[OK] All fixes applied successfully!\n")
        sys.stdout.write("\n")
        sys.stdout.write("Note: Backup files were created with extensions:\n")
        sys.stdout.write("  - .utf8.backup (for encoding conversions)\n")
        sys.stdout.write("  - .lf.backup (for line ending normalizations)\n")
        sys.stdout.write("\n")
        sys.stdout.write("If you encounter any issues, you can restore from these backups.\n")
        return 0
    else:
        sys.stdout.write("\n")
        sys.stdout.write("[!] Some fixes failed. Please review the errors above.\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
