# V2LocKit (Victoria 2 Localisation Toolkit)

A collection of Python scripts to help manage, validate, and fix localisation files for Victoria 2 mods.

## Features

*   **Duplicate Detection**: Find and remove duplicate keys (which cause dead code).
*   **Encoding Fixer**: Convert UTF-8 files to Windows-1252 (required by Vic2) and fix line endings.
*   **Structure Fixer**: Ensure correct 19-column CSV format.
*   **Missing Key Finder**: Scan event/decision/etc files to find missing localisation keys.
*   **Safety**: All fixer scripts now support `--dry-run` and create backups by default.

## Usage

Scripts are designed to be run from the command line. They will attempt to auto-detect the mod location if run from the `app` directory, or you can specify paths.

### 1. Fix Duplicates
Removes duplicate keys from `text.csv` or other files.
```bash
python fix_text_csv_duplicates.py [path/to/file.csv]
```

### 2. Fix Newstext Duplicates
Specific fixer for `newstext_3_01.csv` duplicates.
```bash
python fix_newstext_duplicates.py [path/to/file.csv]
```

### 3. Check for Cross-File Duplicates
Checks if the same key exists in multiple files (later files override earlier ones).
```bash
python check_duplicate_localizations.py [path/to/localisation/dir]
```

### 4. Find Missing Localisations
The big scanner! Checks your events, decisions, etc., and tells you what keys are missing.
```bash
python check_missing_localizations.py [path/to/mod/root]
```

### 5. Fix Encoding & Line Endings
Converts file to Windows-1252 and CRCRLF line endings.
```bash
python fix_localisation_encoding.py [path/to/localisation/dir]
python fix-line-endings.py [path/to/file_or_dir]
```

### 6. Fix CSV Structure
Ensures files have exactly 19 columns (required for Vic2).
```bash
python fix-csv-structure.py [path/to/file_or_dir]
python fix-column-count.py [path/to/file_or_dir]
```

## Safety Options
Most fixer scripts support:
*   `--dry-run`: See what would happen without changing files.
*   `--no-backup`: Disable automatic backup creation (use with caution!).

## Requirements
*   Python 3.6+
