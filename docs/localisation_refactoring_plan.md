# Localisation Refactoring Plan

**Mod**: CoE_RoI_R (Concert of Europe: Roar of Industry - Reignited)
**Date**: 2025-01-25
**Status**: Planning Complete

---

## Overview

Refactor the localisation system from 61 scattered CSV files to 12 logically organized files, fixing encoding issues, adding missing keys, and establishing maintainable structure.

**Goals**:
- Performance optimization (fewer files = faster loading)
- Maintainability (logical file organization)
- Bug fixing (encoding, missing keys, structural issues)
- Documentation & structure (clear standards)

---

## Current State

| Metric | Value |
|--------|-------|
| CSV Files | 61 |
| Total Keys | 34,039 |
| Missing Keys | 448 (1.3%) |
| Column Standard | 14 (correct) |
| Encoding Issues | Present (mojibake in FR/DE) |

### Critical Issues

1. **text.csv Line 1**: Empty row with 86 comma fields - causes localisation shifting
2. **Encoding**: UTF-8 bytes interpreted as Windows-1252 (corrupted accents)
3. **Missing Localisations**: 363 modifier descriptions, 73 triggered modifiers
4. **Validator Bug**: `TARGET_COLUMNS = 19` should be `14`

---

## Target Structure (12 Files)

```
localisation/
├── 00_base_core.csv              # Countries, governments, ideologies
├── 00_base_ui.csv                # UI: ledger, budget, interface
├── 00_base_tech.csv              # Technologies, inventions
├── 00_base_goods.csv             # Trade goods
├── 00_base_units.csv             # Military units, ships
├── 01_event_modifiers.csv        # ALL event modifiers + desc_*
├── 01_triggered_modifiers.csv    # ALL triggered modifiers + desc_*
├── 02_events_vanilla.csv         # Vanilla events (100-99999)
├── 02_events_custom.csv          # Custom events (100000+)
├── 03_decisions.csv              # ALL decisions + _title + _desc
├── 04_news.csv                   # Newspaper events
└── 05_overrides.csv              # Final mod-specific overrides
```

**Load Order**: Files load in reverse lexicographic order (00_ first, 05_ last)

---

## Implementation Phases

### Phase 1: Foundation (30 min)

| Task | Description | Git Strategy |
|------|-------------|--------------|
| 1.1 | Fix `validator.py:116` - change `TARGET_COLUMNS = 19` to `14` | Commit: `fix: correct validator column count to 14` |
| 1.2 | Scan for cross-file duplicate keys | Document findings in git commit |
| 1.3 | Generate baseline validation report | Commit: `docs: add baseline localisation validation` |

### Phase 2: Stabilization (2-4 hours)

| Task | Description | Git Strategy |
|------|-------------|--------------|
| 2.1 | Fix `text.csv` line 1 empty row bug | Commit: `fix: remove malformed empty line from text.csv` |
| 2.2 | Convert all CSVs to Windows-1252, fix line endings (\r\r\n) | Commit: `fix: normalize encoding to Windows-1252` |
| 2.3 | Add 448 missing localisations (manual review required) | Multiple commits per category |

### Phase 3: Consolidation (4-6 hours)

| Task | Description | Git Strategy |
|------|-------------|--------------|
| 3.1 | Create 12 new CSV files with headers | Branch: `refactor/localisation-consolidate` |
| 3.2 | Merge content from 61 files into 12 files | Atomic commit per target file |
| 3.3 | Validate consolidated system | Commit: `refactor: merge localisation to 12 files` |

### Phase 4: Completion (1-2 hours)

| Task | Description | Git Strategy |
|------|-------------|--------------|
| 4.1 | Game test - verify no "KEY" strings in UI | Document test results |
| 4.2 | Create `LOCALISATION.md` documentation | Commit: `docs: add localisation reference guide` |
| 4.3 | Move original files to `localisation_archive/` | Commit: `refactor: archive legacy localisation files` |

---

## File Mapping (Merge Strategy)

| Target File | Source Files | Key Types |
|-------------|--------------|-----------|
| 00_base_core.csv | 00_PDM_countries.csv, CountriesGVG.csv, new_political_parties.csv | TAG, TAG_ADJ, governments |
| 00_base_ui.csv | text.csv (UI only) | LEDGER_*, BUDGET_* |
| 00_base_tech.csv | 00_PDM_tech.csv | Tech names, inventions |
| 00_base_goods.csv | 00_PDM_goods.csv + 4 missing | Trade goods |
| 00_base_units.csv | 00_PDM_wargoals.csv | Unit types |
| 01_event_modifiers.csv | All event files + 363 desc_ | MODIFIER, desc_MODIFIER |
| 01_triggered_modifiers.csv | 0000_economic_rework.csv + 73 desc_ | Triggered modifiers |
| 02_events_vanilla.csv | 00_PDM_events.csv, beta*.csv, 1.*.csv | EVT 100-99999 |
| 02_events_custom.csv | 000_persia_events.csv, VIP_events.csv | EVT 100000+ |
| 03_decisions.csv | 00_PDM_political.csv, VIP_decisions.csv | decision_* |
| 04_news.csv | event_news.csv, 00_PDM_news.csv | News events |
| 05_overrides.csv | 00_FIX_*.csv (fixes only) | Override keys |

---

## Validation Checklist

- [ ] All files have exactly 14 columns
- [ ] Column 15 contains `x` terminator
- [ ] All files use Windows-1252 encoding
- [ ] All files use `\r\r\n` line endings
- [ ] No duplicate keys within files
- [ ] Total key count = 34,487 (34,039 + 448 new)
- [ ] Zero missing keys in `check_missing_localizations.py`
- [ ] Game loads without errors
- [ ] No "KEY" strings visible in UI

---

## Tools

| Tool | Purpose | Location |
|------|---------|----------|
| V2LocKit GUI | Validation, fixing | `app/v2lockit/` |
| check_missing_localizations.py | Find missing keys | `app/` |
| fix_localisation_encoding.py | Fix encoding | `app/` |
| fix-csv-structure.py | Fix column count | `app/` |

---

## Rollback Strategy

```bash
# If consolidation fails, revert to pre-refactor state
git checkout main
git branch -D refactor/localisation-consolidate

# To restore archived files
mv localisation_archive/* localisation/
```

---

## Key Standards

| Attribute | Standard |
|-----------|----------|
| Encoding | Windows-1252 (ANSI) |
| Columns | 14 (key + 13 languages + x) |
| Delimiter | Semicolon (;) |
| Line Ending | \r\r\n (double carriage return) |
| Empty Lines | Forbidden (causes shifting) |

---

## References

- [Victoria 2 Wiki - Localisation](https://vic2.paradoxwikis.com/Localisation)
- `docs/localisation_wiki.md` - Complete localisation reference
- `app/README.md` - Localisation tooling guide

---

*Generated for CoE_RoI_R mod development*
