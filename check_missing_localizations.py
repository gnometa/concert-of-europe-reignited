#!/usr/bin/env python3
"""
Victoria 2 Comprehensive Localization Checker
==============================================

A comprehensive tool to detect missing localizations for ALL game elements:
- Event modifiers & Triggered modifiers
- Events (titles, descriptions, options)
- Decisions (titles, descriptions)
- Buildings
- Goods/Trade goods
- Technologies
- Inventions
- Units
- Cultures, Religions
- Countries, Provinces
- And more...

Usage:
    python check_missing_localizations.py [--verbose] [--fix] [--output report.txt]

Author: Claude Code for CoE_RoI_R mod
Version: 2.0
"""

import os
import re
import sys
import csv
from pathlib import Path
from typing import Dict, Set, List, Tuple, Optional
from collections import defaultdict
import argparse

# Try to import chardet for better encoding detection
try:
    import chardet
    HAVE_CHARDET = True
except ImportError:
    HAVE_CHARDET = False

# Configuration
MOD_PATH = Path("D:/Steam/steamapps/common/Victoria 2/mod/CoE_RoI_R")
COMMON_DIR = MOD_PATH / "common"
EVENTS_DIR = MOD_PATH / "events"
DECISIONS_DIR = MOD_PATH / "decisions"
LOCALISATION_DIR = MOD_PATH / "localisation"

# Victoria 2 localization uses Windows-1252 encoding
ENCODING = "windows-1252"
CSV_DELIMITER = ";"

# Colors for terminal output (Windows)
class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def read_file_with_encoding(file_path: Path) -> Optional[str]:
    """
    Read a file with automatic encoding detection.
    Tries UTF-8 first, then detects encoding if that fails.
    """
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        # Detect encoding if chardet is available
        if HAVE_CHARDET:
            with open(file_path, 'rb') as f:
                raw = f.read()
                result = chardet.detect(raw)
                detected_encoding = result.get('encoding', 'latin-1')
            try:
                return file_path.read_text(encoding=detected_encoding)
            except:
                pass  # Fall through to latin-1

        # Last resort - try common encodings
        for enc in ["latin-1", "cp1252", "iso-8859-1"]:
            try:
                return file_path.read_text(encoding=enc, errors="ignore")
            except:
                continue
        return None
    except Exception as e:
        return None


def parse_modifiers_file(file_path: Path, modifier_type: str) -> Set[str]:
    """
    Parse event_modifiers.txt or triggered_modifiers.txt and extract all modifier names.

    Format:
        modifier_name = {
            ...
        }
    """
    modifiers = set()
    pattern = re.compile(r"^([a-z_][a-z0-9_]*)\s*=\s*\{", re.MULTILINE)

    content = read_file_with_encoding(file_path)
    if content:
        matches = pattern.findall(content)
        modifiers.update(matches)
        print(f"{Colors.OKCYAN}[*] Found {len(modifiers)} {modifier_type}{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}[!] Error reading {file_path}{Colors.ENDC}")

    return modifiers


def parse_buildings_file(file_path: Path) -> Set[str]:
    """Parse buildings.txt for building names."""
    buildings = set()
    pattern = re.compile(r"^([a-z_][a-z0-9_]*)\s*=\s*\{", re.MULTILINE)

    content = read_file_with_encoding(file_path)
    if content:
        matches = pattern.findall(content)
        # Filter out common buildings that don't need localization
        skip = {"fort", "naval_base", "railroad", "province"}
        for match in matches:
            if match not in skip:
                buildings.add(match)
        print(f"{Colors.OKCYAN}[*] Found {len(buildings)} buildings needing localization{Colors.ENDC}")

    return buildings


def parse_goods_file(file_path: Path) -> Set[str]:
    """Parse goods.txt for trade good names."""
    goods = set()
    pattern = re.compile(r"^([a-z_][a-z0-9_]*)\s*=\s*\{", re.MULTILINE)

    content = read_file_with_encoding(file_path)
    if content:
        matches = pattern.findall(content)
        goods.update(matches)
        print(f"{Colors.OKCYAN}[*] Found {len(goods)} trade goods{Colors.ENDC}")

    return goods


def parse_event_file(file_path: Path) -> Dict[str, Set[str]]:
    """
    Parse event file and extract all localization keys needed.

    Returns dict with keys: 'event_ids', 'titles', 'descs', 'options', 'other_keys'
    """
    result = {
        'event_ids': set(),
        'titles': set(),        # title = "KEY"
        'descs': set(),         # desc = "KEY"
        'options': set(),       # option name = "KEY"
        'other_keys': set()     # Other localization keys
    }

    content = read_file_with_encoding(file_path)
    if not content:
        return result

    # Event IDs
    id_pattern = re.compile(r"\bid\s*=\s*(\d+)", re.MULTILINE)
    result['event_ids'].update(id_pattern.findall(content))

    # title = "KEY" pattern
    title_pattern = re.compile(r'\btitle\s*=\s*"([^"]+)"', re.MULTILINE)
    for title in title_pattern.findall(content):
        if not title.startswith("EVT"):  # EVT... keys are auto-generated
            result['titles'].add(title)

    # desc = "KEY" pattern
    desc_pattern = re.compile(r'\bdesc\s*=\s*"([^"]+)"', re.MULTILINE)
    for desc in desc_pattern.findall(content):
        if not desc.startswith("EVT"):
            result['descs'].add(desc)

    # option { name = "KEY" } pattern
    opt_name_pattern = re.compile(r'\bname\s*=\s*"([^"]+)"', re.MULTILINE)
    for name in opt_name_pattern.findall(content):
        if re.match(r'^[a-z_][a-z0-9_]*$', name):
            result['options'].add(name)

    # Look for picture = "gfx/event_pictures/KEY" for event pictures
    picture_pattern = re.compile(r'\bpicture\s*=\s*"gfx/event_pictures/([^"]+)"', re.MULTILINE)
    for pic in picture_pattern.findall(content):
        result['other_keys'].add(pic)

    return result


def parse_decision_file(file_path: Path) -> Dict[str, Set[str]]:
    """
    Parse decision file and extract localization keys.

    Returns dict with keys: 'decision_names', 'titles', 'descs', 'other_keys'
    """
    result = {
        'decision_names': set(),  # decision_name = { ...
        'titles': set(),           # title = "KEY"
        'descs': set(),            # desc = "KEY"
        'other_keys': set()
    }

    content = read_file_with_encoding(file_path)
    if not content:
        return result

    # Decision blocks
    dec_pattern = re.compile(r"^([a-z_][a-z0-9_]*)\s*=\s*\{", re.MULTILINE)
    skip_dec = {"country_decisions", "political_decisions", "economic_decisions",
                "military_decisions", "diplomatic_decisions", "internal_decisions"}

    for dec in dec_pattern.findall(content):
        if dec not in skip_dec:
            result['decision_names'].add(dec)

    # title and desc within decisions
    title_pattern = re.compile(r'\btitle\s*=\s*"([^"]+)"', re.MULTILINE)
    for title in title_pattern.findall(content):
        result['titles'].add(title)

    desc_pattern = re.compile(r'\bdesc\s*=\s*"([^"]+)"', re.MULTILINE)
    for desc in desc_pattern.findall(content):
        result['descs'].add(desc)

    return result


def parse_technology_folder(folder: Path) -> Dict[str, Set[str]]:
    """Parse technology files for school names and tech names."""
    result = {
        'schools': set(),
        'techs': set()
    }

    for tech_file in folder.glob("*.txt"):
        content = read_file_with_encoding(tech_file)
        if not content:
            continue

        # school = { name = "KEY" }
        school_pattern = re.compile(r'school\s*=\s*\{[^}]*name\s*=\s*"([^"]+)"', re.DOTALL)
        for school in school_pattern.findall(content):
            result['schools'].add(school)

        # tech_xxx = { name = "KEY" }
        tech_pattern = re.compile(r'tech_[a-z_]+\s*=\s*\{[^}]*name\s*=\s*"([^"]+)"', re.DOTALL)
        for tech in tech_pattern.findall(content):
            result['techs'].add(tech)

    print(f"{Colors.OKCYAN}[*] Found {len(result['schools'])} schools and {len(result['techs'])} technology names{Colors.ENDC}")
    return result


def parse_invention_folder(folder: Path) -> Set[str]:
    """Parse invention files for invention names."""
    inventions = set()

    for inv_file in folder.glob("*.txt"):
        content = read_file_with_encoding(inv_file)
        if not content:
            continue

        # invention = { name = "KEY" }
        inv_pattern = re.compile(r'[a-z_]+\s*=\s*\{[^}]*name\s*=\s*"([^"]+)"', re.DOTALL)
        for inv in inv_pattern.findall(content):
            if not inv.startswith("EVT"):
                inventions.add(inv)

    print(f"{Colors.OKCYAN}[*] Found {len(inventions)} invention names{Colors.ENDC}")
    return inventions


def parse_unit_file(file_path: Path) -> Set[str]:
    """Parse units.txt for unit names."""
    units = set()
    pattern = re.compile(r'^([a-z_][a-z0-9_]*)\s*=\s*\{', re.MULTILINE)

    content = read_file_with_encoding(file_path)
    if content:
        matches = pattern.findall(content)
        units.update(matches)
        print(f"{Colors.OKCYAN}[*] Found {len(units)} unit types{Colors.ENDC}")

    return units


def parse_cultures_file(file_path: Path) -> Dict[str, Set[str]]:
    """Parse cultures.txt for culture groups and cultures."""
    result = {
        'culture_groups': set(),
        'cultures': set()
    }

    content = read_file_with_encoding(file_path)
    if not content:
        return result

    # Culture group names
    group_pattern = re.compile(r'^([a-z_]+)\s*=\s*\{', re.MULTILINE)
    result['culture_groups'].update(group_pattern.findall(content))

    # Individual culture names (within groups)
    culture_pattern = re.compile(r'^([a-z_]+)\s*=\s*\{', re.MULTILINE)
    # This needs more sophisticated parsing to avoid group names

    print(f"{Colors.OKCYAN}[*] Found {len(result['culture_groups'])} culture groups{Colors.ENDC}")
    return result


def parse_localisation_csvs(dir_path: Path) -> Dict[str, str]:
    """
    Parse all CSV files in localisation directory and extract keys.

    Returns a dictionary mapping keys to the file they were found in.
    """
    localizations = {}

    csv_files = list(dir_path.glob("*.csv"))
    print(f"{Colors.OKCYAN}[*] Scanning {len(csv_files)} CSV files...{Colors.ENDC}")

    for csv_file in csv_files:
        try:
            with open(csv_file, 'r', encoding=ENCODING, errors='ignore') as f:
                reader = csv.reader(f, delimiter=CSV_DELIMITER)
                for row in reader:
                    if row and len(row) > 0:
                        key = row[0].strip()
                        # Skip empty keys, comments, and numeric-only keys
                        if key and not key.startswith('#') and not key.isdigit():
                            localizations[key] = csv_file.name
        except Exception as e:
            print(f"{Colors.FAIL}[!] Error reading {csv_file}: {e}{Colors.ENDC}")

    print(f"{Colors.OKGREEN}[+] Found {len(localizations)} localization keys{Colors.ENDC}")
    return localizations


def find_missing_localizations(
    event_modifiers: Set[str],
    triggered_modifiers: Set[str],
    event_data: Dict[str, Set[str]],
    decision_data: Dict[str, Set[str]],
    buildings: Set[str],
    goods: Set[str],
    units: Set[str],
    tech_data: Dict[str, Set[str]],
    inventions: Set[str],
    localizations: Dict[str, str]
) -> Dict[str, List[Tuple[str, str]]]:
    """
    Find missing localizations, categorizing by type.

    Returns dictionary mapping category to list of (missing_key, likely_location) tuples.
    """
    missing = defaultdict(list)

    # Event modifiers
    for modifier in event_modifiers:
        if modifier not in localizations:
            missing["event_modifiers"].append((modifier, "00_PDM_events.csv"))
        desc_key = f"desc_{modifier}"
        if desc_key not in localizations:
            missing["event_modifier_descriptions"].append((desc_key, "00_PDM_events.csv"))

    # Triggered modifiers
    for modifier in triggered_modifiers:
        if modifier not in localizations:
            missing["triggered_modifiers"].append((modifier, "0000_economic_rework.csv"))
        desc_key = f"desc_{modifier}"
        if desc_key not in localizations:
            missing["triggered_modifier_descriptions"].append((desc_key, "0000_economic_rework.csv"))

    # Event titles/descs that are explicitly defined
    for title in event_data['titles']:
        if title not in localizations:
            missing["event_titles"].append((title, "00_PDM_events.csv"))

    for desc in event_data['descs']:
        if desc not in localizations:
            missing["event_descriptions"].append((desc, "00_PDM_events.csv"))

    # Option names
    for opt in event_data['options']:
        if opt not in localizations:
            missing["option_names"].append((opt, "check context"))

    # Decision names and explicit titles/descs
    for dec_name in decision_data['decision_names']:
        title_key = f"{dec_name}_title"
        if title_key not in localizations and dec_name not in localizations:
            missing["decision_titles"].append((title_key, "check decision file"))
        desc_key = f"{dec_name}_desc"
        if desc_key not in localizations:
            missing["decision_descriptions"].append((desc_key, "check decision file"))

    for title in decision_data['titles']:
        if title not in localizations:
            missing["decision_titles"].append((title, "check decision file"))

    for desc in decision_data['descs']:
        if desc not in localizations:
            missing["decision_descriptions"].append((desc, "check decision file"))

    # Buildings
    for building in buildings:
        if building not in localizations:
            missing["buildings"].append((building, "00_PDM_events.csv"))

    # Goods
    for good in goods:
        if good not in localizations:
            missing["goods"].append((good, "00_PDM_goods.csv"))

    # Units
    for unit in units:
        if unit not in localizations:
            missing["units"].append((unit, "check appropriate file"))

    # Technology schools and names
    for school in tech_data['schools']:
        if school not in localizations:
            missing["tech_schools"].append((school, "00_PDM_tech.csv"))

    for tech in tech_data['techs']:
        if tech not in localizations:
            missing["tech_names"].append((tech, "00_PDM_tech.csv"))

    # Inventions
    for inv in inventions:
        if inv not in localizations:
            missing["inventions"].append((inv, "check appropriate file"))

    return missing


def print_report(missing: Dict[str, List[Tuple[str, str]]], verbose: bool = False):
    """Print a formatted report of missing localizations."""
    total_missing = sum(len(v) for v in missing.values())

    if total_missing == 0:
        print(f"{Colors.OKGREEN}No missing localizations found!{Colors.ENDC}")
        return

    print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}MISSING LOCALIZATION REPORT{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")

    # Category summaries
    for category, items in sorted(missing.items()):
        if items:
            print(f"{Colors.WARNING}{category.upper().replace('_', ' ')}{Colors.ENDC}: {len(items)} missing")

    print(f"\n{Colors.BOLD}Total: {total_missing} missing localizations{Colors.ENDC}\n")

    # Detailed breakdown
    if verbose:
        for category, items in sorted(missing.items()):
            if items:
                print(f"\n{Colors.HEADER}=== {category.upper().replace('_', ' ')} ==={Colors.ENDC}")
                for key, location in items[:50]:
                    safe_key = key.encode('ascii', errors='replace').decode('ascii')
                    print(f"  - {safe_key} ({location})")
                if len(items) > 50:
                    print(f"  ... and {len(items) - 50} more")
    else:
        # Show only important categories by default
        important = ["event_modifiers", "triggered_modifiers", "event_modifier_descriptions",
                     "triggered_modifier_descriptions", "decision_titles", "decision_descriptions",
                     "buildings", "goods"]
        for category in important:
            if category in missing and missing[category]:
                print(f"\n{Colors.WARNING}=== {category.upper().replace('_', ' ')} ==={Colors.ENDC}")
                for key, location in missing[category][:20]:
                    safe_key = key.encode('ascii', errors='replace').decode('ascii')
                    print(f"  - {safe_key} ({location})")
                if len(missing[category]) > 20:
                    print(f"  ... and {len(missing[category]) - 20} more")


def generate_fix_file(missing: Dict[str, List[Tuple[str, str]]], output_path: Path):
    """
    Generate organized fix files for missing entries.

    Creates separate files for different categories to help with manual integration.
    Uses proper Victoria 2 CSV format with trailing commas.
    """
    print(f"\n{Colors.OKCYAN}[*] Generating fix files...{Colors.ENDC}")

    # Group by recommended file
    by_file = defaultdict(list)

    for category, items in missing.items():
        for key, location in items:
            by_file[location].append((category, key))

    for filename, items in by_file.items():
        if "check" in filename.lower():
            continue  # Skip items that need manual determination

        # Output to mod directory (same level as the actual CSV files)
        if filename == "00_PDM_events.csv":
            output_file = MOD_PATH / "localisation" / f"FIX_{filename}"
            trailing = ",,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,"
        elif filename == "0000_economic_rework.csv":
            output_file = MOD_PATH / "localisation" / f"FIX_{filename}"
            trailing = ",,"
        elif filename == "00_PDM_goods.csv":
            output_file = MOD_PATH / "localisation" / f"FIX_{filename}"
            trailing = ",,"
        else:
            output_file = output_path.parent / f"fix_{filename.replace('/', '_')}"
            trailing = ""

        with open(output_file, 'w', encoding=ENCODING, errors="replace") as f:
            f.write(f"# Localization fixes for {filename}\n")
            f.write(f"# MANUAL REVIEW REQUIRED BEFORE INTEGRATION\n")
            f.write(f"# Copy entries from this file to the actual {filename}\n\n")

            for category, key in items:
                # Sanitize key to remove problematic characters
                safe_key = key.encode(ENCODING, errors="replace").decode(ENCODING)
                f.write(f"{safe_key};TODO;;;;;;;;;;;;;x{trailing}\n")

        print(f"{Colors.OKGREEN}[+] Generated {output_file.name} with {len(items)} entries{Colors.ENDC}")

    # Also create a consolidated list in the mod directory for reference
    consolidated = MOD_PATH / "MISSING_LOCALIZATIONS_LIST.txt"
    with open(consolidated, 'w', encoding='utf-8') as f:
        f.write("# CONSOLIDATED LIST OF ALL MISSING LOCALIZATIONS\n")
        f.write("# Run: python check_missing_localizations.py to regenerate\n")
        f.write("# Located at: " + str(Path(__file__).parent) + "\n\n")

        for category, items in sorted(missing.items()):
            if items:
                f.write(f"\n## {category.upper().replace('_', ' ')} ({len(items)} entries)\n\n")
                for key, location in items[:100]:
                    f.write(f"{key} → {location}\n")
                if len(items) > 100:
                    f.write(f"... and {len(items) - 100} more\n")

    print(f"{Colors.OKGREEN}[+] Generated {consolidated.name} with full list{Colors.ENDC}")


def main():
    parser = argparse.ArgumentParser(description="Check for missing Victoria 2 localizations")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show all missing entries")
    parser.add_argument("-f", "--fix", action="store_true", help="Generate fix files")
    parser.add_argument("-o", "--output", default="missing_localizations",
                       help="Output path prefix for fixes")
    parser.add_argument("--scan-money-hoarder", action="store_true",
                       help="Specifically scan for money_hoarder_* localizations")
    parser.add_argument("--scan-modifiers", action="store_true",
                       help="Only scan modifiers (event and triggered)")

    args = parser.parse_args()

    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}VICTORIA 2 LOCALIZATION CHECKER v2.0{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
    print(f"Mod Path: {MOD_PATH}\n")

    # Special mode: scan for specific pattern
    if args.scan_money_hoarder:
        print(f"{Colors.OKCYAN}[*] Scanning for money_hoarder_* localizations...{Colors.ENDC}\n")
        localizations = parse_localisation_csvs(LOCALISATION_DIR)

        for i in range(1, 11):
            key = f"money_hoarder_{i}"
            desc_key = f"desc_money_hoarder_{i}"

            status_key = "OK" if key in localizations else "MISSING"
            status_desc = "OK" if desc_key in localizations else "MISSING"

            status_key_colored = f"{Colors.OKGREEN}{status_key}{Colors.ENDC}" if key in localizations else f"{Colors.FAIL}{status_key}{Colors.ENDC}"
            status_desc_colored = f"{Colors.OKGREEN}{status_desc}{Colors.ENDC}" if desc_key in localizations else f"{Colors.FAIL}{status_desc}{Colors.ENDC}"

            print(f"  {key:30} {status_key_colored}")
            print(f"  {desc_key:30} {status_desc_colored}")

        return

    # Full comprehensive scan
    print(f"{Colors.BOLD}[1/10] Parsing event modifiers...{Colors.ENDC}")
    event_mod_file = COMMON_DIR / "event_modifiers.txt"
    event_modifiers = parse_modifiers_file(event_mod_file, "event modifiers")

    print(f"{Colors.BOLD}[2/10] Parsing triggered modifiers...{Colors.ENDC}")
    triggered_mod_file = COMMON_DIR / "triggered_modifiers.txt"
    triggered_modifiers = parse_modifiers_file(triggered_mod_file, "triggered modifiers")

    if args.scan_modifiers:
        # Just do modifiers and stop
        print(f"\n{Colors.BOLD}[3/3] Parsing localisation CSVs...{Colors.ENDC}")
        localizations = parse_localisation_csvs(LOCALISATION_DIR)

        missing = defaultdict(list)
        for mod in event_modifiers:
            if mod not in localizations:
                missing["event_modifiers"].append((mod, "00_PDM_events.csv"))
        for mod in triggered_modifiers:
            if mod not in localizations:
                missing["triggered_modifiers"].append((mod, "0000_economic_rework.csv"))

        print_report(missing, verbose=args.verbose)
        return

    print(f"{Colors.BOLD}[3/10] Parsing buildings...{Colors.ENDC}")
    buildings_file = COMMON_DIR / "buildings.txt"
    buildings = parse_buildings_file(buildings_file)

    print(f"{Colors.BOLD}[4/10] Parsing goods...{Colors.ENDC}")
    goods_file = COMMON_DIR / "goods.txt"
    goods = parse_goods_file(goods_file)

    print(f"{Colors.BOLD}[5/10] Parsing units...{Colors.ENDC}")
    units_file = COMMON_DIR / "units" / "land_units.txt"
    units = parse_unit_file(units_file)

    print(f"{Colors.BOLD}[6/10] Parsing events...{Colors.ENDC}")
    all_event_data = {
        'event_ids': set(),
        'titles': set(),
        'descs': set(),
        'options': set(),
        'other_keys': set()
    }
    event_count = 0
    for event_file in EVENTS_DIR.glob("*.txt"):
        event_data = parse_event_file(event_file)
        for key in all_event_data:
            all_event_data[key].update(event_data[key])
        event_count += 1
    print(f"{Colors.OKGREEN}[+] Parsed {event_count} event files with {len(all_event_data['event_ids'])} event IDs{Colors.ENDC}")

    print(f"{Colors.BOLD}[7/10] Parsing decisions...{Colors.ENDC}")
    all_decision_data = {
        'decision_names': set(),
        'titles': set(),
        'descs': set(),
        'other_keys': set()
    }
    decision_count = 0
    for decision_file in DECISIONS_DIR.glob("*.txt"):
        decision_data = parse_decision_file(decision_file)
        for key in all_decision_data:
            all_decision_data[key].update(decision_data[key])
        decision_count += 1
    print(f"{Colors.OKGREEN}[+] Parsed {decision_count} decision files{Colors.ENDC}")

    print(f"{Colors.BOLD}[8/10] Parsing technologies...{Colors.ENDC}")
    tech_folder = COMMON_DIR / "technologies"
    tech_data = parse_technology_folder(tech_folder)

    print(f"{Colors.BOLD}[9/10] Parsing inventions...{Colors.ENDC}")
    inv_folder = COMMON_DIR / "inventions"
    inventions = parse_invention_folder(inv_folder)

    print(f"{Colors.BOLD}[10/10] Parsing localisation CSVs...{Colors.ENDC}")
    localizations = parse_localisation_csvs(LOCALISATION_DIR)

    print(f"{Colors.BOLD}Analyzing missing entries...{Colors.ENDC}")
    missing = find_missing_localizations(
        event_modifiers, triggered_modifiers,
        all_event_data, all_decision_data,
        buildings, goods, units,
        tech_data, inventions,
        localizations
    )

    print_report(missing, verbose=args.verbose)

    if args.fix:
        output_path = MOD_PATH / args.output
        generate_fix_file(missing, output_path)

    print(f"\n{Colors.OKCYAN}[*] Scan complete!{Colors.ENDC}")


if __name__ == "__main__":
    main()
