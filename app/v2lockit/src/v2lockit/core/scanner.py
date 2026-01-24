"""
V2LocKit Scanner Module
=======================

Scans Victoria 2 game files to find localisation keys that need translations:
- Event files (titles, descriptions, options)
- Decision files (titles, descriptions)
- Modifier files (event_modifiers.txt, triggered_modifiers.txt)
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set, Tuple
import re


@dataclass
class ScanResult:
    """Results from scanning game files for localisation keys."""
    event_keys: Set[str] = field(default_factory=set)
    decision_keys: Set[str] = field(default_factory=set)
    modifier_keys: Set[str] = field(default_factory=set)
    
    @property
    def all_keys(self) -> Set[str]:
        return self.event_keys | self.decision_keys | self.modifier_keys
    
    @property
    def total_keys(self) -> int:
        return len(self.all_keys)


@dataclass
class MissingKey:
    """A localisation key that is missing."""
    key: str
    source_file: Path
    category: str  # 'event', 'decision', 'modifier'
    
    def __str__(self) -> str:
        return f"{self.key} ({self.category}, from {self.source_file.name})"


@dataclass
class MissingKeysReport:
    """Report of all missing localisation keys."""
    missing_keys: List[MissingKey] = field(default_factory=list)
    
    @property
    def by_category(self) -> Dict[str, List[MissingKey]]:
        result: Dict[str, List[MissingKey]] = {}
        for key in self.missing_keys:
            if key.category not in result:
                result[key.category] = []
            result[key.category].append(key)
        return result
    
    @property
    def total_missing(self) -> int:
        return len(self.missing_keys)


class Scanner:
    """
    Scans Victoria 2 game files to find localisation keys.
    
    Looks for:
    - Events: title = EVTNAME*, desc = EVTDESC*, option = { name = ... }
    - Decisions: title = ..., desc = ...
    - Modifiers: modifier_name = { ... }
    """
    
    # Patterns for key extraction
    EVENT_TITLE_PATTERN = re.compile(r'title\s*=\s*"?([A-Za-z0-9_]+)"?')
    EVENT_DESC_PATTERN = re.compile(r'desc\s*=\s*"?([A-Za-z0-9_]+)"?')
    OPTION_NAME_PATTERN = re.compile(r'name\s*=\s*"?([A-Za-z0-9_]+)"?')
    MODIFIER_PATTERN = re.compile(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*\{', re.MULTILINE)
    
    def __init__(self, mod_path: Path):
        """Initialize scanner with mod root path."""
        self.mod_path = mod_path
        self.events_path = mod_path / "events"
        self.decisions_path = mod_path / "decisions"
        self.common_path = mod_path / "common"
    
    def _read_file_safe(self, file_path: Path) -> str:
        """Read file with encoding fallback."""
        for encoding in ['utf-8', 'cp1252', 'latin1']:
            try:
                return file_path.read_text(encoding=encoding)
            except UnicodeDecodeError:
                continue
        return ""
    
    def _is_localisation_key(self, text: str) -> bool:
        """
        Determine if text looks like a localisation key vs inline text.
        
        Keys are typically:
        - UPPERCASE or MixedCase identifiers
        - Start with EVT, EVTNAME, EVTDESC, etc.
        - Don't contain spaces
        - Don't start with quotes containing spaces
        """
        if not text:
            return False
        
        # If it contains spaces, it's probably inline text
        if ' ' in text:
            return False
        
        # Common key prefixes
        key_prefixes = ['EVT', 'MODIFIER', 'DECISION', 'desc_', 'title_', 'option_']
        if any(text.upper().startswith(p.upper()) for p in key_prefixes):
            return True
        
        # All caps is likely a key
        if text.isupper() and len(text) > 3:
            return True
        
        # Contains underscore, likely a key
        if '_' in text and text.replace('_', '').isalnum():
            return True
        
        return False
    
    def scan_events(self) -> Set[str]:
        """Scan event files for localisation keys."""
        keys: Set[str] = set()
        
        if not self.events_path.exists():
            return keys
        
        for event_file in self.events_path.glob("*.txt"):
            content = self._read_file_safe(event_file)
            
            # Extract titles
            for match in self.EVENT_TITLE_PATTERN.finditer(content):
                key = match.group(1)
                if self._is_localisation_key(key):
                    keys.add(key)
            
            # Extract descriptions
            for match in self.EVENT_DESC_PATTERN.finditer(content):
                key = match.group(1)
                if self._is_localisation_key(key):
                    keys.add(key)
            
            # Extract option names
            for match in self.OPTION_NAME_PATTERN.finditer(content):
                key = match.group(1)
                if self._is_localisation_key(key):
                    keys.add(key)
        
        return keys
    
    def scan_decisions(self) -> Set[str]:
        """Scan decision files for localisation keys."""
        keys: Set[str] = set()
        
        if not self.decisions_path.exists():
            return keys
        
        for decision_file in self.decisions_path.glob("*.txt"):
            content = self._read_file_safe(decision_file)
            
            # Use same patterns for decisions
            for match in self.EVENT_TITLE_PATTERN.finditer(content):
                key = match.group(1)
                if self._is_localisation_key(key):
                    keys.add(key)
            
            for match in self.EVENT_DESC_PATTERN.finditer(content):
                key = match.group(1)
                if self._is_localisation_key(key):
                    keys.add(key)
        
        return keys
    
    def scan_modifiers(self) -> Set[str]:
        """Scan modifier files for localisation keys."""
        keys: Set[str] = set()
        
        modifier_files = [
            self.common_path / "event_modifiers.txt",
            self.common_path / "triggered_modifiers.txt",
            self.common_path / "static_modifiers.txt",
        ]
        
        for mod_file in modifier_files:
            if not mod_file.exists():
                continue
            
            content = self._read_file_safe(mod_file)
            
            for match in self.MODIFIER_PATTERN.finditer(content):
                modifier_name = match.group(1)
                # Skip common non-localisation patterns
                if modifier_name in ['icon', 'duration', 'trigger', 'effect']:
                    continue
                keys.add(modifier_name)
        
        return keys
    
    def scan_all(self) -> ScanResult:
        """Scan all game files and return found keys."""
        return ScanResult(
            event_keys=self.scan_events(),
            decision_keys=self.scan_decisions(),
            modifier_keys=self.scan_modifiers()
        )
    
    def find_missing(self, existing_keys: Set[str]) -> MissingKeysReport:
        """
        Find keys that are used in game files but not in localisation.
        
        Args:
            existing_keys: Set of keys already defined in localisation CSVs
        
        Returns:
            Report of missing keys
        """
        report = MissingKeysReport()
        
        # Scan events
        for key in self.scan_events():
            if key not in existing_keys:
                # Try to find which file it came from
                source = self._find_key_source(key, self.events_path)
                report.missing_keys.append(MissingKey(
                    key=key,
                    source_file=source or self.events_path,
                    category='event'
                ))
        
        # Scan decisions
        for key in self.scan_decisions():
            if key not in existing_keys:
                source = self._find_key_source(key, self.decisions_path)
                report.missing_keys.append(MissingKey(
                    key=key,
                    source_file=source or self.decisions_path,
                    category='decision'
                ))
        
        # Scan modifiers
        for key in self.scan_modifiers():
            if key not in existing_keys:
                report.missing_keys.append(MissingKey(
                    key=key,
                    source_file=self.common_path,
                    category='modifier'
                ))
        
        return report
    
    def _find_key_source(self, key: str, search_path: Path) -> Path | None:
        """Find which file contains a specific key."""
        if not search_path.exists():
            return None
        
        for txt_file in search_path.glob("*.txt"):
            content = self._read_file_safe(txt_file)
            if key in content:
                return txt_file
        
        return None
    
    def generate_summary(self, report: MissingKeysReport) -> str:
        """Generate a human-readable summary of missing keys."""
        lines = [
            "# Missing Localisation Keys",
            "",
            f"**Total Missing**: {report.total_missing}",
            "",
        ]
        
        if report.total_missing == 0:
            lines.append("✅ All keys have localisation entries!")
        else:
            by_cat = report.by_category
            
            for category, keys in sorted(by_cat.items()):
                lines.append(f"## {category.title()}s ({len(keys)} missing)")
                lines.append("")
                for missing in keys[:20]:  # Limit output
                    lines.append(f"- `{missing.key}` — from {missing.source_file.name}")
                if len(keys) > 20:
                    lines.append(f"- ... and {len(keys) - 20} more")
                lines.append("")
        
        return "\n".join(lines)
