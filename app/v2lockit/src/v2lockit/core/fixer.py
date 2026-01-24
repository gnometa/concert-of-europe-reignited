"""
V2LocKit Fixer Module
=====================

Repairs Victoria 2 localisation CSV files:
- Converts encoding to Windows-1252
- Normalizes column count to 19
- Fixes line endings to \\r\\r\\n
- Removes empty lines
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
import shutil
from datetime import datetime


@dataclass
class FixResult:
    """Result of fixing a single file."""
    file_path: Path
    success: bool = True
    backup_path: Optional[Path] = None
    changes_made: List[str] = field(default_factory=list)
    error: Optional[str] = None
    
    @property
    def was_modified(self) -> bool:
        return len(self.changes_made) > 0


@dataclass
class FixReport:
    """Report for all fix operations."""
    results: List[FixResult] = field(default_factory=list)
    dry_run: bool = False
    
    @property
    def files_fixed(self) -> int:
        return sum(1 for r in self.results if r.was_modified and r.success)
    
    @property
    def files_failed(self) -> int:
        return sum(1 for r in self.results if not r.success)


class Fixer:
    """
    Fixes Victoria 2 localisation files to proper format.
    
    Target format:
    - Encoding: Windows-1252
    - Columns: 19
    - Line endings: \\r\\r\\n
    """
    
    TARGET_COLUMNS = 19
    LINE_ENDING = '\r\r\n'
    
    def __init__(self, create_backup: bool = True, dry_run: bool = False):
        self.create_backup = create_backup
        self.dry_run = dry_run
    
    def _backup_file(self, file_path: Path) -> Path:
        """Create a backup of the file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = file_path.with_suffix(f".{timestamp}.bak")
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def _detect_encoding(self, content: bytes) -> str:
        """Detect encoding of raw bytes."""
        if content.startswith(b'\xef\xbb\xbf'):
            return 'utf-8-bom'
        
        try:
            content.decode('utf-8')
            return 'utf-8'
        except UnicodeDecodeError:
            pass
        
        return 'cp1252'
    
    def _fix_line(self, line: str) -> str:
        """Fix a single line to proper format."""
        parts = line.split(';')
        
        # Ensure exactly TARGET_COLUMNS columns
        if len(parts) < self.TARGET_COLUMNS:
            # Pad with empty strings
            while len(parts) < 14:
                parts.append('')
            # Ensure column 15 is 'x'
            if len(parts) < 15:
                parts.append('x')
            elif parts[14].strip() != 'x':
                parts[14] = 'x'
            # Pad remaining columns
            while len(parts) < self.TARGET_COLUMNS:
                parts.append('')
        elif len(parts) > self.TARGET_COLUMNS:
            # Truncate but preserve key and important columns
            new_parts = parts[:14]
            new_parts.append('x')
            while len(new_parts) < self.TARGET_COLUMNS:
                new_parts.append('')
            parts = new_parts
        
        # Ensure column 15 is 'x'
        if len(parts) >= 15 and parts[14].strip() != 'x':
            parts[14] = 'x'
        
        return ';'.join(parts)
    
    def fix_file(self, file_path: Path) -> FixResult:
        """Fix a single localisation file."""
        result = FixResult(file_path=file_path)
        
        try:
            # Read raw content
            with open(file_path, 'rb') as f:
                raw_content = f.read()
            
            original_encoding = self._detect_encoding(raw_content)
            
            # Decode content
            if original_encoding == 'utf-8-bom':
                text = raw_content[3:].decode('utf-8')
                result.changes_made.append("Removed UTF-8 BOM")
            elif original_encoding == 'utf-8':
                text = raw_content.decode('utf-8')
            else:
                text = raw_content.decode('cp1252', errors='replace')
            
            if original_encoding != 'cp1252':
                result.changes_made.append(f"Converted encoding from {original_encoding} to cp1252")
            
            # Normalize line endings for processing
            text = text.replace('\r\r\n', '\n').replace('\r\n', '\n').replace('\r', '\n')
            lines = text.split('\n')
            
            fixed_lines = []
            empty_lines_removed = 0
            columns_fixed = 0
            
            for i, line in enumerate(lines):
                # Skip empty lines (except preserve one at end)
                if not line.strip():
                    if i < len(lines) - 1:  # Not the last line
                        empty_lines_removed += 1
                        continue
                    else:
                        continue  # Skip trailing empty line
                
                # Fix column count
                parts = line.split(';')
                original_col_count = len(parts)
                
                fixed_line = self._fix_line(line)
                
                if len(parts) != self.TARGET_COLUMNS:
                    columns_fixed += 1
                
                fixed_lines.append(fixed_line)
            
            if empty_lines_removed > 0:
                result.changes_made.append(f"Removed {empty_lines_removed} empty line(s)")
            
            if columns_fixed > 0:
                result.changes_made.append(f"Fixed column count on {columns_fixed} line(s)")
            
            # Check if line endings need fixing
            if b'\r\r\n' not in raw_content and b'\n' in raw_content:
                result.changes_made.append("Fixed line endings to \\r\\r\\n")
            
            # Only write if changes were made
            if result.changes_made and not self.dry_run:
                # Create backup
                if self.create_backup:
                    result.backup_path = self._backup_file(file_path)
                
                # Write fixed content
                fixed_content = self.LINE_ENDING.join(fixed_lines)
                if not fixed_content.endswith(self.LINE_ENDING):
                    fixed_content += self.LINE_ENDING
                
                with open(file_path, 'wb') as f:
                    f.write(fixed_content.encode('cp1252', errors='replace'))
            
        except Exception as e:
            result.success = False
            result.error = str(e)
        
        return result
    
    def fix_directory(self, dir_path: Path) -> FixReport:
        """Fix all CSV files in a directory."""
        report = FixReport(dry_run=self.dry_run)
        
        csv_files = sorted(dir_path.glob("*.csv"))
        
        for csv_file in csv_files:
            result = self.fix_file(csv_file)
            report.results.append(result)
        
        return report
    
    def generate_summary(self, report: FixReport) -> str:
        """Generate a human-readable summary of the fix report."""
        mode = "[DRY RUN] " if report.dry_run else ""
        lines = [
            f"# {mode}V2LocKit Fix Report",
            "",
            f"**Files Processed**: {len(report.results)}",
            f"**Files Fixed**: {report.files_fixed}",
            f"**Files Failed**: {report.files_failed}",
            "",
        ]
        
        if report.files_fixed == 0 and report.files_failed == 0:
            lines.append("✅ All files already correct!")
        else:
            if report.files_fixed > 0:
                lines.append("## Changes Made")
                lines.append("")
                
                for result in report.results:
                    if result.was_modified:
                        lines.append(f"### {result.file_path.name}")
                        for change in result.changes_made:
                            lines.append(f"- ✓ {change}")
                        if result.backup_path:
                            lines.append(f"- 📁 Backup: {result.backup_path.name}")
                        lines.append("")
            
            if report.files_failed > 0:
                lines.append("## Errors")
                lines.append("")
                for result in report.results:
                    if not result.success:
                        lines.append(f"- ❌ {result.file_path.name}: {result.error}")
        
        return "\n".join(lines)
