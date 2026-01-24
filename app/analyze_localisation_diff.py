#!/usr/bin/env python3
"""
Comprehensive Localisation Analysis Tool for Victoria 2 Mods
Compares CoE_RoI_R (problematic) against CoE_RoI (working reference)
"""

import os
import csv
import chardet
from collections import defaultdict
from pathlib import Path

# Folder paths
R_FOLDER = r'D:\Steam\steamapps\common\Victoria 2\mod\CoE_RoI_R\localisation'
O_FOLDER = r'D:\Steam\steamapps\common\Victoria 2\mod\CoE_RoI\localisation'

# Expected columns for Victoria 2 localisation
EXPECTED_COLUMNS = 14

def detect_encoding(file_path):
    """Detect file encoding using chardet"""
    try:
        with open(file_path, 'rb') as f:
            raw = f.read(10000)  # Read first 10KB
            result = chardet.detect(raw)
            return result['encoding'], result['confidence']
    except Exception as e:
        return f"Error: {e}", 0

def analyze_csv_structure(file_path):
    """
    Analyze CSV structure and return detailed diagnostics.
    Returns dict with: line_count, empty_lines, column_issues, encoding_issues
    """
    results = {
        'line_count': 0,
        'empty_lines': [],
        'column_issues': [],  # Lines with wrong column count
        'encoding': None,
        'line_endings': None,
        'has_bom': False,
        'sample_issues': []
    }

    # Detect encoding
    encoding, confidence = detect_encoding(file_path)
    results['encoding'] = f"{encoding} ({confidence:.2%})"

    try:
        # Read with detected encoding
        with open(file_path, 'r', encoding=encoding or 'utf-8', errors='replace') as f:
            raw_content = f.read()

        # Check for BOM
        if raw_content.startswith('\ufeff'):
            results['has_bom'] = True

        # Detect line endings
        if '\r\n' in raw_content:
            results['line_endings'] = 'CRLF (Windows)'
        elif '\n' in raw_content:
            results['line_endings'] = 'LF (Unix)'
        elif '\r' in raw_content:
            results['line_endings'] = 'CR (Mac Classic)'

        lines = raw_content.splitlines()
        results['line_count'] = len(lines)

        # Analyze each line
        for idx, line in enumerate(lines, start=1):
            # Skip empty lines but track them
            if not line.strip():
                results['empty_lines'].append(idx)
                continue

            # Count semicolons (columns = semicolons + 1)
            semicolon_count = line.count(';')
            column_count = semicolon_count + 1

            # Check column count
            if column_count != EXPECTED_COLUMNS:
                issue = {
                    'line': idx,
                    'columns': column_count,
                    'expected': EXPECTED_COLUMNS,
                    'preview': line[:80] + '...' if len(line) > 80 else line
                }
                results['column_issues'].append(issue)

    except Exception as e:
        results['error'] = str(e)

    return results

def compare_files(r_file, o_file):
    """Compare two CSV files and identify differences"""
    comparison = {
        'r_only_keys': [],
        'o_only_keys': [],
        'different_values': [],
        'encoding_mismatch': False,
        'structure_diff': []
    }

    try:
        # Read both files
        r_data = {}
        o_data = {}

        def read_csv_data(file_path, data_dict):
            enc, _ = detect_encoding(file_path)
            with open(file_path, 'r', encoding=enc or 'utf-8', errors='replace') as f:
                reader = csv.reader(f, delimiter=';')
                for row in reader:
                    if row and row[0]:  # Has key
                        data_dict[row[0]] = row

        read_csv_data(r_file, r_data)
        read_csv_data(o_file, o_data)

        # Find differences
        r_keys = set(r_data.keys())
        o_keys = set(o_data.keys())

        comparison['r_only_keys'] = sorted(r_keys - o_keys)
        comparison['o_only_keys'] = sorted(o_keys - r_keys)

        # Check value differences for common keys
        for key in r_keys & o_keys:
            if r_data[key] != o_data[key]:
                comparison['different_values'].append({
                    'key': key,
                    'r_value': r_data[key][1] if len(r_data[key]) > 1 else '',
                    'o_value': o_data[key][1] if len(o_data[key]) > 1 else ''
                })

    except Exception as e:
        comparison['error'] = str(e)

    return comparison

def generate_report():
    """Generate comprehensive analysis report"""
    print("=" * 80)
    print("VICTORIA 2 LOCALISATION ANALYSIS REPORT")
    print("=" * 80)
    print(f"\nComparing:")
    print(f"  PROBLEMATIC: {R_FOLDER}")
    print(f"  WORKING REF: {O_FOLDER}")
    print()

    # Get all CSV files
    r_files = sorted([f for f in os.listdir(R_FOLDER) if f.endswith('.csv')])
    o_files = sorted([f for f in os.listdir(O_FOLDER) if f.endswith('.csv)')])

    all_files = sorted(set(r_files) | set(o_files))

    # Summary statistics
    total_issues = defaultdict(int)
    problematic_files = []

    print("-" * 80)
    print("STRUCTURAL ANALYSIS")
    print("-" * 80)
    print()

    for filename in all_files:
        r_path = os.path.join(R_FOLDER, filename)
        o_path = os.path.join(O_FOLDER, filename)

        r_exists = os.path.exists(r_path)
        o_exists = os.path.exists(o_path)

        print(f"\n{'='*70}")
        print(f"FILE: {filename}")
        print(f"{'='*70}")

        # File existence
        if r_exists:
            print(f"  [R] EXISTS: Yes")
        else:
            print(f"  [R] EXISTS: No - MISSING IN PROBLEMATIC FOLDER!")
            total_issues['missing_in_r'] += 1

        if o_exists:
            print(f"  [O] EXISTS: Yes")
        else:
            print(f"  [O] EXISTS: No - ONLY IN PROBLEMATIC FOLDER!")
            total_issues['only_in_r'] += 1

        # Analyze R file if it exists
        if r_exists:
            r_analysis = analyze_csv_structure(r_path)

            print(f"\n  [R] ENCODING: {r_analysis['encoding']}")
            print(f"  [R] LINE ENDINGS: {r_analysis['line_endings']}")
            print(f"  [R] HAS BOM: {'YES !!!' if r_analysis['has_bom'] else 'No'}")
            print(f"  [R] TOTAL LINES: {r_analysis['line_count']}")

            if r_analysis['empty_lines']:
                print(f"  [R] EMPTY LINES: {len(r_analysis['empty_lines'])} !!! CRITICAL ISSUE")
                total_issues['empty_lines'] += len(r_analysis['empty_lines'])
                if len(r_analysis['empty_lines']) <= 10:
                    print(f"      Lines: {r_analysis['empty_lines']}")
                else:
                    print(f"      Lines: {r_analysis['empty_lines'][:5]} ... (and {len(r_analysis['empty_lines']) - 5} more)")

            if r_analysis['column_issues']:
                print(f"  [R] COLUMN ISSUES: {len(r_analysis['column_issues'])} !!! CRITICAL ISSUE")
                total_issues['column_issues'] += len(r_analysis['column_issues'])
                for issue in r_analysis['column_issues'][:5]:
                    print(f"      Line {issue['line']}: {issue['columns']} cols (expected {issue['expected']})")
                if len(r_analysis['column_issues']) > 5:
                    print(f"      ... and {len(r_analysis['column_issues']) - 5} more")

            # Track problematic files
            if r_analysis['empty_lines'] or r_analysis['column_issues']:
                problematic_files.append({
                    'file': filename,
                    'empty_lines': len(r_analysis['empty_lines']),
                    'column_issues': len(r_analysis['column_issues']),
                    'encoding': r_analysis['encoding']
                })

        # Compare files if both exist
        if r_exists and o_exists:
            print(f"\n  --- CONTENT COMPARISON ---")
            comparison = compare_files(r_path, o_path)

            if comparison.get('error'):
                print(f"  Comparison Error: {comparison['error']}")
            else:
                if comparison['r_only_keys']:
                    print(f"  Keys only in [R]: {len(comparison['r_only_keys'])}")
                    total_issues['r_only_keys'] += len(comparison['r_only_keys'])

                if comparison['o_only_keys']:
                    print(f"  Keys only in [O]: {len(comparison['o_only_keys'])}")
                    total_issues['o_only_keys'] += len(comparison['o_only_keys'])

                if comparison['different_values']:
                    print(f"  Different values: {len(comparison['different_values'])}")
                    total_issues['different_values'] += len(comparison['different_values'])

    # Summary section
    print("\n" + "=" * 80)
    print("SUMMARY OF CRITICAL ISSUES")
    print("=" * 80)
    print()

    for issue_type, count in sorted(total_issues.items(), key=lambda x: -x[1]):
        if count > 0:
            print(f"  {issue_type.upper().replace('_', ' ')}: {count}")

    print()
    print("-" * 80)
    print("MOST PROBLEMATIC FILES (requiring immediate attention)")
    print("-" * 80)
    print()

    # Sort by severity (empty_lines + column_issues)
    problematic_files.sort(key=lambda x: -(x['empty_lines'] + x['column_issues']))

    for pf in problematic_files[:20]:
        severity_score = pf['empty_lines'] + pf['column_issues']
        print(f"  [{severity_score} issues] {pf['file']}")
        print(f"      Empty lines: {pf['empty_lines']} | Column issues: {pf['column_issues']}")

    print()
    print("=" * 80)
    print("RECOMMENDATIONS")
    print("=" * 80)
    print()
    print("1. EMPTY LINES - Remove all empty lines from CSV files")
    print("   Empty lines cause Victoria 2's parser to shift ALL subsequent localisations!")
    print()
    print("2. COLUMN COUNT - Ensure every line has exactly 14 semicolon-separated fields")
    print("   Format: KEY;Eng;Fr;De;;Es;;;;;;;;x;")
    print()
    print("3. ENCODING - Use Windows-1252 (ANSI) encoding, NOT UTF-8")
    print("   Convert UTF-8 files to ANSI using a text editor")
    print()
    print("4. LINE ENDINGS - Use CRLF (Windows) line endings")
    print()
    print("5. Consider using the fix scripts in app/ folder:")
    print("   - fix-line-endings.py")
    print("   - fix-column-count.py")
    print("   - fix-csv-structure.py")
    print()

if __name__ == '__main__':
    generate_report()
