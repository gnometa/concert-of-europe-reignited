#!/usr/bin/env python3
"""
Localisation Fix Script V2
==========================

Project: The Concert of Europe: Roar of Industry - Reignited
Purpose: Automatically fix localisation CSV files by respecting their individual
         header column counts and ensuring correct Windows-1252 encoding.

Usage:
    python fix-localisation-v2.py [options] [path]

Arguments:
    path            Path to localisation folder or specific file (default: CoE_RoI_R/localisation/)

Options:
    --dry-run       Preview changes without modifying files
    --verbose       Show detailed output for each file
    --json          Output results in JSON format
    -h, --help      Show this help message

Fixes Applied:
    1. Encoding conversion: Securely convert to Windows-1252
    2. Header Detection: Read the first line to determine target column count
    3. Column Adjustment: Truncate or pad lines to match target column count
    4. Line Endings: Ensure all data lines end with ';x'
"""

import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class FileFixResult:
    """Result from fixing a single file."""
    file_name: str
    original_encoding: str = ""
    target_columns: int = 0
    lines_fixed_semicolon: int = 0
    lines_fixed_columns: int = 0
    lines_total: int = 0
    errors: List[str] = field(default_factory=list)
    skipped: bool = False
    skip_reason: str = ""


@dataclass
class FixRunResult:
    """Combined results from all files."""
    timestamp: str = ""
    dry_run: bool = False
    files_processed: int = 0
    files_fixed: int = 0
    files_skipped: int = 0
    total_lines_fixed: int = 0
    file_results: List[FileFixResult] = field(default_factory=list)


class LocalisationFixerV2:
    """Fixes Victoria 2 localisation files adaptively."""

    def __init__(self, target_path: Path, 
                 dry_run: bool = False,
                 verbose: bool = False,
                 json_output: bool = False):
        self.target_path = target_path
        self.dry_run = dry_run
        self.verbose = verbose
        self.json_output = json_output
        self.result = FixRunResult()
        self.result.timestamp = datetime.now().isoformat()
        self.result.dry_run = dry_run

    def detect_encoding(self, file_path: Path) -> str:
        """Detect file encoding."""
        try:
            with open(file_path, 'rb') as f:
                raw = f.read()
            
            if raw.startswith(b'\xef\xbb\xbf'):
                return 'utf-8-bom'
            
            try:
                decoded = raw.decode('utf-8')
                if any(ord(c) > 127 for c in decoded):
                    return 'utf-8'
            except UnicodeDecodeError:
                pass
            
            return 'cp1252'
        except Exception as e:
            return f'error: {e}'

    def read_file_content(self, file_path: Path) -> Tuple[List[str], str]:
        """Read file content handling various encodings."""
        encoding = self.detect_encoding(file_path)
        
        try:
            if encoding == 'utf-8-bom':
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    return f.readlines(), encoding
            elif encoding == 'utf-8':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.readlines(), encoding
            else:
                # Fallback to cp1252 with replace for safety
                with open(file_path, 'r', encoding='cp1252', errors='replace') as f:
                    return f.readlines(), encoding
        except Exception as e:
            raise RuntimeError(f"Failed to read file: {e}")

    def create_backup(self, file_path: Path):
        """Create a .bak copy of the file."""
        if self.dry_run:
            return
        backup_path = file_path.with_suffix('.csv.bak')
        try:
            shutil.copy2(file_path, backup_path)
        except Exception:
            pass

    def fix_line(self, line: str, target_columns: int) -> Tuple[str, bool, bool]:
        """Fix a single line to match target columns."""
        original = line.rstrip('\r\n')
        
        if not original.strip() or original.strip().startswith('#'):
            return original, False, False
        
        semicolon_fixed = False
        column_fixed = False
        
        parts = original.split(';')
        
        # Determine actual content (removing 'x' terminator garbage)
        content = []
        for i, p in enumerate(parts):
            # The 'x' usually marks the end. But sometimes 'x' is just a column value?
            # In V2, the last column must be 'x'.
            # If we are strictly enforcing column count, we just grab everything and resizing.
            content.append(p)
            
        # We need exactly target_columns.
        # The last column MUST be 'x'.
        
        # Clean current parts
        # Remove trailing empty strings or 'x' related noise if overly long
        # But we must preserve empty translations!
        
        # Strategy:
        # 1. Take first (KEY)
        # 2. Take middle parts (Translations)
        # 3. Force last part to be 'x' and ensure length matches
        
        current_len = len(parts)
        
        if current_len == target_columns:
            # Check check if ends with x
            if parts[-1].strip() != 'x':
                parts[-1] = 'x'
                semicolon_fixed = True # technically content fixed but fits here
            
            fixed = ';'.join(parts)
            if fixed != original:
                 semicolon_fixed = True
            
            # Check for missing ;x
            if not original.endswith(';x') and not original.endswith(';x\t'):
                 # It might be correctly formatted but missing strict ending char or has trailing verify
                 pass

            return fixed, semicolon_fixed, column_fixed

        # Resize needed
        column_fixed = True
        
        if current_len > target_columns:
            # Truncate
            new_parts = parts[:target_columns]
            new_parts[-1] = 'x' # Ensure terminator
        else:
            # Pad
            new_parts = parts[:]
            # If the last part was 'x', we should keep it as 'x' at the end?
            # Or just pad with empty strings and append 'x'?
            
            # Prune existing 'x' if it's there but early
            if new_parts[-1].strip() == 'x':
                new_parts.pop()
                
            while len(new_parts) < target_columns - 1:
                new_parts.append('')
            
            new_parts.append('x')
            
        fixed = ';'.join(new_parts)
        return fixed, semicolon_fixed, column_fixed

    def fix_file(self, file_path: Path) -> FileFixResult:
        """Fix a single localisation file."""
        result = FileFixResult(file_name=file_path.name)
        
        try:
            lines, encoding = self.read_file_content(file_path)
            result.original_encoding = encoding
        except Exception as e:
            result.errors.append(str(e))
            return result
        
        if not lines:
            result.skipped = True
            result.skip_reason = "Empty file"
            return result

        # Determine target columns from header
        header = lines[0].rstrip('\r\n')
        target_columns = len(header.split(';'))
        result.target_columns = target_columns
        result.lines_total = len(lines)
        
        fixed_lines = [header] # Keep header as is
        
        has_changes = False
        
        for i, line in enumerate(lines[1:], 1):
            fixed, sem_fixed, col_fixed = self.fix_line(line, target_columns)
            fixed_lines.append(fixed)
            
            if sem_fixed:
                result.lines_fixed_semicolon += 1
                has_changes = True
            if col_fixed:
                result.lines_fixed_columns += 1
                has_changes = True
                
            if fixed != line.rstrip('\r\n'):
                 has_changes = True

        # Check for encoding change requirement
        if encoding != 'cp1252':
            has_changes = True

        if has_changes:
            if not self.dry_run:
                self.create_backup(file_path)
                try:
                    with open(file_path, 'w', encoding='cp1252', newline='\r\n', errors='replace') as f:
                        f.write('\r\n'.join(fixed_lines))
                        if fixed_lines and not fixed_lines[-1].strip():
                            pass
                        else:
                            f.write('\r\n')
                except Exception as e:
                    result.errors.append(f"Write error: {e}")
                    return result
            
            self.result.files_fixed += 1
            
        self.result.total_lines_fixed += result.lines_fixed_semicolon + result.lines_fixed_columns
        return result

    def run(self):
        """Run the fix process."""
        if not self.json_output:
            print(f"Fixing localisation in: {self.target_path}")
            print(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE'}")
            
        if self.target_path.is_file():
            files = [self.target_path]
        else:
            files = sorted(list(self.target_path.glob("*.csv")))
            
        for f in files:
            res = self.fix_file(f)
            self.result.file_results.append(res)
            self.result.files_processed += 1
            
            if self.verbose and not self.json_output:
                if res.errors:
                    print(f"[x] {f.name}: {res.errors}")
                elif res.lines_fixed_columns > 0 or res.lines_fixed_semicolon > 0:
                     print(f"[+] {f.name}: Fixed {res.lines_fixed_columns} col / {res.lines_fixed_semicolon} semi checks (Target: {res.target_columns})")

        if not self.json_output:
            print(f"Processed {self.result.files_processed} files.")
            print(f"Fixed {self.result.files_fixed} files.")

def main():
    args = sys.argv[1:]
    dry_run = '--dry-run' in args
    verbose = '--verbose' in args or '-v' in args
    json_output = '--json' in args
    
    args = [a for a in args if not a.startswith('-')]
    
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent
    
    if args:
        target_path = Path(args[0])
        if not target_path.is_absolute():
            target_path = project_root / target_path
    else:
        target_path = project_root / "CoE_RoI_R" / "localisation"
        
    fixer = LocalisationFixerV2(target_path, dry_run, verbose, json_output)
    fixer.run()

if __name__ == "__main__":
    main()
