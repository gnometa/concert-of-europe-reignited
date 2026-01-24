"""
V2LocKit Validator Module
=========================

Validates Victoria 2 localisation CSV files for:
- Encoding (Windows-1252 required)
- Column count (19 columns expected)
- Line endings (\\r\\r\\n required)
- Empty lines
- Duplicate keys (same file and cross-file)
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import re


class Severity(Enum):
    """Issue severity levels."""
    ERROR = "error"      # Breaks game functionality
    WARNING = "warning"  # May cause issues
    INFO = "info"        # Cosmetic or best practice


class IssueType(Enum):
    """Types of validation issues."""
    ENCODING = "encoding"
    COLUMN_COUNT = "column_count"
    LINE_ENDING = "line_ending"
    EMPTY_LINE = "empty_line"
    DUPLICATE_KEY_SAME_FILE = "duplicate_key_same_file"
    DUPLICATE_KEY_CROSS_FILE = "duplicate_key_cross_file"
    MISSING_TERMINATOR = "missing_terminator"
    INVALID_KEY = "invalid_key"


@dataclass
class ValidationIssue:
    """A single validation issue."""
    file_path: Path
    issue_type: IssueType
    severity: Severity
    line_number: Optional[int] = None
    message: str = ""
    context: str = ""  # The problematic line/content
    suggestion: str = ""  # How to fix it
    
    def __str__(self) -> str:
        loc = f":{self.line_number}" if self.line_number else ""
        return f"[{self.severity.value.upper()}] {self.file_path.name}{loc}: {self.message}"


@dataclass
class FileValidationResult:
    """Validation result for a single file."""
    file_path: Path
    encoding_detected: str = ""
    line_count: int = 0
    column_count: int = 0
    issues: List[ValidationIssue] = field(default_factory=list)
    keys: Set[str] = field(default_factory=set)
    
    @property
    def is_valid(self) -> bool:
        return not any(i.severity == Severity.ERROR for i in self.issues)
    
    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.ERROR)
    
    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == Severity.WARNING)


@dataclass
class ValidationReport:
    """Complete validation report for all files."""
    file_results: List[FileValidationResult] = field(default_factory=list)
    cross_file_issues: List[ValidationIssue] = field(default_factory=list)
    
    @property
    def total_files(self) -> int:
        return len(self.file_results)
    
    @property
    def valid_files(self) -> int:
        return sum(1 for r in self.file_results if r.is_valid)
    
    @property
    def total_errors(self) -> int:
        count = sum(r.error_count for r in self.file_results)
        count += sum(1 for i in self.cross_file_issues if i.severity == Severity.ERROR)
        return count
    
    @property
    def total_warnings(self) -> int:
        count = sum(r.warning_count for r in self.file_results)
        count += sum(1 for i in self.cross_file_issues if i.severity == Severity.WARNING)
        return count


class Validator:
    """
    Validates Victoria 2 localisation files.
    
    Victoria 2 CSV Format Requirements:
    - Encoding: Windows-1252 (ANSI)
    - Columns: 19 total (key + 14 translations + x terminator + 3 empty)
    - Line endings: \\r\\r\\n (double carriage return + linefeed)
    - No empty lines within content
    """
    
    TARGET_COLUMNS = 19
    VALID_ENCODINGS = {'cp1252', 'windows-1252', 'latin1'}
    
    def __init__(self):
        self.all_keys: Dict[str, List[Tuple[Path, int]]] = {}  # key -> [(file, line), ...]
    
    def detect_encoding(self, file_path: Path) -> str:
        """Detect file encoding by reading BOM or content analysis."""
        try:
            with open(file_path, 'rb') as f:
                raw = f.read(1024)
            
            # Check for BOM
            if raw.startswith(b'\xef\xbb\xbf'):
                return 'utf-8-bom'
            if raw.startswith(b'\xff\xfe'):
                return 'utf-16-le'
            if raw.startswith(b'\xfe\xff'):
                return 'utf-16-be'
            
            # Try UTF-8
            try:
                raw.decode('utf-8')
                # Check for high bytes that would indicate cp1252
                if any(b > 127 for b in raw):
                    # Could be either, assume cp1252 for V2
                    return 'cp1252'
                return 'utf-8'
            except UnicodeDecodeError:
                pass
            
            # Default to cp1252 (V2 standard)
            return 'cp1252'
            
        except Exception:
            return 'unknown'
    
    def validate_file(self, file_path: Path) -> FileValidationResult:
        """Validate a single localisation CSV file."""
        result = FileValidationResult(file_path=file_path)
        
        # Detect encoding
        result.encoding_detected = self.detect_encoding(file_path)
        
        # Check encoding
        if result.encoding_detected not in self.VALID_ENCODINGS:
            result.issues.append(ValidationIssue(
                file_path=file_path,
                issue_type=IssueType.ENCODING,
                severity=Severity.WARNING,
                message=f"Non-standard encoding: {result.encoding_detected}",
                suggestion="Convert to Windows-1252 encoding"
            ))
        
        # Read file content
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
        except Exception as e:
            result.issues.append(ValidationIssue(
                file_path=file_path,
                issue_type=IssueType.ENCODING,
                severity=Severity.ERROR,
                message=f"Cannot read file: {e}"
            ))
            return result
        
        # Check line endings
        if b'\r\r\n' not in content and b'\n' in content:
            result.issues.append(ValidationIssue(
                file_path=file_path,
                issue_type=IssueType.LINE_ENDING,
                severity=Severity.ERROR,
                message="Missing double carriage return line endings (\\r\\r\\n)",
                suggestion="Run line ending fixer"
            ))
        
        # Decode for line-by-line analysis
        try:
            text = content.decode('cp1252')
        except UnicodeDecodeError:
            try:
                text = content.decode('utf-8')
            except UnicodeDecodeError:
                text = content.decode('latin1')
        
        lines = text.split('\n')
        result.line_count = len(lines)
        
        seen_keys_in_file: Dict[str, int] = {}  # key -> first line number
        
        for i, line in enumerate(lines, 1):
            line = line.rstrip('\r')
            
            # Skip empty lines but track them
            if not line.strip():
                if i > 1 and i < len(lines):  # Not first or last line
                    result.issues.append(ValidationIssue(
                        file_path=file_path,
                        issue_type=IssueType.EMPTY_LINE,
                        severity=Severity.WARNING,
                        line_number=i,
                        message="Empty line in middle of file",
                        suggestion="Remove empty line"
                    ))
                continue
            
            # Parse columns
            parts = line.split(';')
            col_count = len(parts)
            
            if result.column_count == 0:
                result.column_count = col_count
            
            # Check column count
            if col_count != self.TARGET_COLUMNS:
                result.issues.append(ValidationIssue(
                    file_path=file_path,
                    issue_type=IssueType.COLUMN_COUNT,
                    severity=Severity.ERROR,
                    line_number=i,
                    message=f"Column count {col_count}, expected {self.TARGET_COLUMNS}",
                    context=line[:80] + "..." if len(line) > 80 else line,
                    suggestion=f"Adjust to {self.TARGET_COLUMNS} columns"
                ))
            
            # Check terminator (column 15 should be 'x')
            if len(parts) >= 15 and parts[14].strip() != 'x':
                result.issues.append(ValidationIssue(
                    file_path=file_path,
                    issue_type=IssueType.MISSING_TERMINATOR,
                    severity=Severity.WARNING,
                    line_number=i,
                    message=f"Column 15 should be 'x', got '{parts[14].strip()}'",
                    suggestion="Set column 15 to 'x'"
                ))
            
            # Extract and track key
            key = parts[0].strip() if parts else ""
            if key and not key.startswith('#'):  # Skip comments
                result.keys.add(key)
                
                # Check for duplicates within same file
                if key in seen_keys_in_file:
                    result.issues.append(ValidationIssue(
                        file_path=file_path,
                        issue_type=IssueType.DUPLICATE_KEY_SAME_FILE,
                        severity=Severity.WARNING,
                        line_number=i,
                        message=f"Duplicate key '{key}' (first seen at line {seen_keys_in_file[key]})",
                        context=key,
                        suggestion="Remove duplicate entry"
                    ))
                else:
                    seen_keys_in_file[key] = i
                
                # Track for cross-file duplicate detection
                if key not in self.all_keys:
                    self.all_keys[key] = []
                self.all_keys[key].append((file_path, i))
        
        return result
    
    def validate_directory(self, dir_path: Path) -> ValidationReport:
        """Validate all CSV files in a directory."""
        report = ValidationReport()
        self.all_keys.clear()
        
        csv_files = sorted(dir_path.glob("*.csv"))
        
        for csv_file in csv_files:
            result = self.validate_file(csv_file)
            report.file_results.append(result)
        
        # Detect cross-file duplicates
        for key, locations in self.all_keys.items():
            if len(locations) > 1:
                # Check if they're in different files
                files = set(loc[0] for loc in locations)
                if len(files) > 1:
                    first_file, first_line = locations[0]
                    for other_file, other_line in locations[1:]:
                        if other_file != first_file:
                            report.cross_file_issues.append(ValidationIssue(
                                file_path=other_file,
                                issue_type=IssueType.DUPLICATE_KEY_CROSS_FILE,
                                severity=Severity.WARNING,
                                line_number=other_line,
                                message=f"Key '{key}' also defined in {first_file.name}:{first_line}",
                                context=key,
                                suggestion=f"Remove duplicate from either {first_file.name} or {other_file.name}"
                            ))
        
        return report
    
    def generate_summary(self, report: ValidationReport) -> str:
        """Generate a human-readable summary of the validation report."""
        lines = [
            "# V2LocKit Validation Report",
            "",
            f"**Files Scanned**: {report.total_files}",
            f"**Valid Files**: {report.valid_files}",
            f"**Total Errors**: {report.total_errors}",
            f"**Total Warnings**: {report.total_warnings}",
            "",
        ]
        
        if report.total_errors == 0 and report.total_warnings == 0:
            lines.append("✅ All files passed validation!")
        else:
            lines.append("## Issues by File")
            lines.append("")
            
            for result in report.file_results:
                if result.issues:
                    lines.append(f"### {result.file_path.name}")
                    for issue in result.issues:
                        icon = "❌" if issue.severity == Severity.ERROR else "⚠️"
                        lines.append(f"- {icon} Line {issue.line_number or '-'}: {issue.message}")
                    lines.append("")
            
            if report.cross_file_issues:
                lines.append("## Cross-File Duplicates")
                lines.append("")
                for issue in report.cross_file_issues:
                    lines.append(f"- ⚠️ {issue.file_path.name}:{issue.line_number}: {issue.message}")
        
        return "\n".join(lines)
