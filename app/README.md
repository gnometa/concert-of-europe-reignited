# CoE_RoI_R Localisation Tools

This directory contains Python utilities for managing Victoria 2 localisation files for the **Concert of Europe: Roar of Industry - Reignited** mod.

## Overview

Victoria 2 localisation files use a specific CSV format with Windows-1252 encoding and semicolon delimiters. These tools help maintain and validate these files.

## Available Tools

### 1. check_missing_localizations.py

**Purpose**: Analytical tool to detect missing localisations

Scans game files (events, decisions, modifiers) and cross-references them with localisation CSV files to identify missing entries.

**Usage**:
```bash
python app/check_missing_localizations.py [options]
```

**Options**:
- `--verbose`, `-v` - Show all missing entries with details
- `--fix` - Generate fix files with suggested entries
- `--output PATH` - Specify output path for reports

**What it does**:
- Parses event files for titles and descriptions
- Parses decision files for titles and descriptions
- Parses modifier files (event_modifiers.txt, triggered_modifiers.txt)
- Cross-references with all CSV files in localisation/
- Reports missing localisation keys
- Generates FIX_*.csv files with suggested entries

**Example**:
```bash
# Quick check for missing localisations
python app/check_missing_localizations.py

# Verbose output with all details
python app/check_missing_localizations.py --verbose

# Generate fix files
python app/check_missing_localizations.py --fix
```

---

### 2. fix-localisation.py

**Purpose**: Repair tool for malformed CSV files

Fixes CSV formatting issues, encoding problems, and column count mismatches in localisation files.

**Usage**:
```bash
python app/fix-localisation.py [options] [path]
```

**Options**:
- `--dry-run` - Preview changes without modifying files
- `--verbose`, `-v` - Show detailed output for each file
- `--json` - Output results in JSON format
- `path` - Path to localisation folder or specific file (default: CoE_RoI_R/localisation/)

**What it does**:
- Detects file encoding (UTF-8, UTF-8-BOM, CP1252)
- Converts files to Windows-1252 encoding
- Reads header to determine target column count
- Normalises all lines to match column count
- Ensures all lines end with `;x`
- Creates .bak backup files before modifying

**Example**:
```bash
# Preview changes without modifying files
python app/fix-localisation.py --dry-run

# Fix all localisation files
python app/fix-localisation.py

# Fix specific file with verbose output
python app/fix-localisation.py --verbose CoE_RoI_R/localisation/00_PDM_events.csv
```

---

## Workflow Recommendations

### Finding Missing Localisations

1. Run the checker tool:
   ```bash
   python app/check_missing_localizations.py --verbose
   ```

2. Review the generated `MISSING_LOCALIZATIONS_LIST.txt` in the mod directory

3. Add missing entries to the appropriate CSV files in `CoE_RoI_R/localisation/`

### Repairing Broken CSV Files

1. Always preview first:
   ```bash
   python app/fix-localisation.py --dry-run --verbose
   ```

2. If satisfied, run the fix:
   ```bash
   python app/fix-localisation.py
   ```

3. Check the .bak files if anything went wrong

### Complete Maintenance Workflow

```bash
# 1. Check for missing localisations
python app/check_missing_localizations.py --verbose > localisation_report.txt

# 2. Add missing entries manually to CSV files
# (Edit CoE_RoI_R/localisation/*.csv)

# 3. Fix any CSV formatting issues
python app/fix-localisation.py --dry-run
python app/fix-localisation.py

# 4. Verify the fixes
python app/check_missing_localizations.py
```

---

## File Format Reference

### Victoria 2 CSV Structure

```
KEY;English;French;German;;Spanish;;;;;;;;;x,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
```

**Components**:
- **Column 1**: Localisation key (e.g., `EVTNAME12345`, `desc_modifier_name`)
- **Column 2-15**: Translations (English, French, German, [Reserved], Spanish, etc.)
- **Column 16**: Must be `x` (end marker)
- **Trailing commas**: Events require 53 trailing commas, modifiers require 2

**Encoding**: Windows-1252 (ANSI) - NOT UTF-8

**Delimiter**: Semicolon (`;`)

---

## Troubleshooting

### "UnicodeEncodeError" when running checker

**Cause**: Console encoding issues on Windows

**Solution**: The tool now handles this automatically with safe_console_string(). If issues persist, redirect output to a file:
```bash
python app/check_missing_localizations.py > report.txt 2>&1
```

### "FileNotFoundError: land_units.txt"

**Cause**: Missing optional game file

**Solution**: This is normal. The tool handles missing files gracefully.

### CSV files appear corrupted in text editor

**Cause**: File opened with wrong encoding

**Solution**: Open with Windows-1252 encoding, not UTF-8

### Special characters (ü, ö, é) appear as garbage

**Cause**: Encoding mismatch

**Solution**: Run fix-localisation.py to convert to proper Windows-1252

---

## Tool Comparison

| Feature | check_missing_localizations.py | fix-localisation.py |
|---------|-------------------------------|---------------------|
| **Primary Purpose** | Find missing entries | Fix broken CSV files |
| **Input** | Game files + CSV files | CSV files only |
| **Output** | Reports + FIX files | Repaired CSV files |
| **Modifies Files** | No (read-only) | Yes (with .bak backup) |
| **Encoding Detection** | Multi-format | UTF-8/CP1252 |
| **Encoding Output** | N/A | Windows-1252 |
| **Column Handling** | Analysis only | Normalises columns |
| **Backup Files** | No | Yes (.bak) |

---

## Version History

### check_missing_localizations.py
- **v2.1** (2026): Enhanced encoding handling, false positive reduction
- **v2.0** (2026): Initial comprehensive checker

### fix-localisation.py
- **v2** (2026): Adaptive column detection, improved encoding handling
- **v1** (2025): Initial CSV repair tool

---

## Requirements

- Python 3.6 or higher
- Optional: `chardet` package for better encoding detection
  ```bash
  pip install chardet
  ```

---

## Support

For issues or questions about these tools, please refer to the main project documentation or create an issue in the project repository.

---

**CoE_RoI_R Mod Development Team**
