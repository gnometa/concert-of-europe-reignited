#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix localisation encoding issues for Victoria 2 mod CoE_RoI_R.

Victoria 2 requires Windows-1252 (ANSI) encoding, not UTF-8.
This script converts UTF-8 files to Windows-1252 and normalizes line endings.
"""

import os
import sys
import argparse
import shutil
from datetime import datetime

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

        sys.stdout.write(f"[OK] Converted: {os.path.basename(input_file)} -> Windows-1252 (ANSI)\n")
        return True

    except UnicodeEncodeError as e:
        sys.stdout.write(f"[X] Encoding error in {os.path.basename(input_file)}: {e}\n")
        sys.stdout.write(f"  Character position: {e.start}\n")
        try:
            problem_text = e.object[e.start:e.end].encode('ascii', 'replace').decode('ascii')
            sys.stdout.write(f"  Problematic text: {repr(problem_text)}\n")
        except:
            pass
        try:
            context = e.object[max(0, e.start-20):e.start+20].encode('ascii', 'replace').decode('ascii')
            sys.stdout.write(f"  Context: {repr(context)}\n")
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

        sys.stdout.write(f"[OK] Normalized line endings: {os.path.basename(input_file)}\n")
        return True

    except Exception as e:
        sys.stdout.write(f"[X] Error processing {input_file}: {e}\n")
        return False

def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Fix localisation encoding issues for Victoria 2.")
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
        sys.stdout.write(f"[X] Directory not found: {localisation_dir}\n")
        return 1

    sys.stdout.write("=" * 70 + "\n")
    sys.stdout.write("Victoria 2 Localisation Encoding Fix Tool\n")
    sys.stdout.write("=" * 70 + "\n")
    sys.stdout.write(f"Target: {localisation_dir}\n\n")

    # Files that need encoding conversion (UTF-8 -> Windows-1252)
    # These are specific known problematic files; we could expand this to scan all later
    encoding_fixes = [
        "0000_economic_rework.csv",
    ]

    # Files that need line ending normalization
    line_ending_fixes = [
        "text.csv",
    ]

    success_count = 0
    total_count = 0
    
    # Check if files exist before counting
    actual_encoding_fixes = [f for f in encoding_fixes if os.path.exists(os.path.join(localisation_dir, f))]
    actual_line_fixes = [f for f in line_ending_fixes if os.path.exists(os.path.join(localisation_dir, f))]
    
    total_count = len(actual_encoding_fixes) + len(actual_line_fixes)
    
    if total_count == 0:
        sys.stdout.write("No known problematic files found in target directory.\n")
        return 0

    # Process encoding fixes
    if actual_encoding_fixes:
        sys.stdout.write("[1/2] Converting UTF-8 files to Windows-1252 (ANSI)...\n\n")

        for filename in actual_encoding_fixes:
            filepath = os.path.join(localisation_dir, filename)

            # Create backup
            backup_path = filepath + '.utf8.backup'
            try:
                shutil.copy2(filepath, backup_path)
                sys.stdout.write(f"  Created backup: {os.path.basename(backup_path)}\n")
            except:
                sys.stdout.write(f"  Warning: Could not create backup for {filename}\n")

            if convert_utf8_to_ansi(filepath):
                success_count += 1
        sys.stdout.write("\n")

    # Process line ending fixes
    if actual_line_fixes:
        sys.stdout.write("[2/2] Normalizing line endings to CRLF...\n\n")

        for filename in actual_line_fixes:
            filepath = os.path.join(localisation_dir, filename)

            # Create backup
            backup_path = filepath + '.lf.backup'
            try:
                shutil.copy2(filepath, backup_path)
                sys.stdout.write(f"  Created backup: {os.path.basename(backup_path)}\n")
            except:
                sys.stdout.write(f"  Warning: Could not create backup for {filename}\n")

            if fix_line_endings(filepath):
                success_count += 1
        sys.stdout.write("\n")

    sys.stdout.write("=" * 70 + "\n")
    sys.stdout.write(f"Summary: {success_count}/{total_count} files processed successfully\n")
    sys.stdout.write("=" * 70 + "\n")

    if success_count == total_count:
        sys.stdout.write("\n[OK] All fixes applied successfully!\n\n")
        sys.stdout.write("Note: Backup files were created with extensions:\n")
        sys.stdout.write("  - .utf8.backup (for encoding conversions)\n")
        sys.stdout.write("  - .lf.backup (for line ending normalizations)\n\n")
        sys.stdout.write("If you encounter any issues, you can restore from these backups.\n")
        return 0
    else:
        sys.stdout.write("\n[!] Some fixes failed. Please review the errors above.\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
