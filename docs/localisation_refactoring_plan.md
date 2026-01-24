# Localisation Refactoring Plan

**Mod**: CoE_RoI_R (Concert of Europe: Roar of Industry - Reignited)
**Date**: 2025-01-25
**Status**: Pilot Phase - text.csv Proof of Concept

---

## Overview

Refactor the localisation system from 61 scattered CSV files (with prefix-gaming load order hacks) to ~40 logically organized files by content domain, fixing encoding issues, adding missing keys, and establishing maintainable structure.

**Goals**:
- **Eliminate prefix gaming** - No more `00_`, `000_`, `0000_` load order tricks
- **Single source of truth** - Countries in ONE file, not scattered across 10+
- **Logical organization** - By content domain (events, decisions, regions), not load timing
- **Bug fixing** - Encoding, missing keys, structural issues
- **Documentation** - Clear standards for future maintenance

---

## Current State Analysis

```
61 files accumulated over 10+ years:
├── 00_PDM_* (14 files)        - Base PDM mod content
├── 00_FIX_* (5 files)         - Corrections (load BEFORE PDM due to reverse sort)
├── 000_crownsteler_* (4 files)- Crowns of Steel scenario
├── 000_persia_* (4 files)     - Persia country pack
├── 0000_economic_rework.csv   - Economics overhaul (loads LAST)
├── darkness_*.csv (5 files)   - Darkness campaign
├── housedivided_*.csv (4 files)- House Divided (ACW) scenario
├── 1.*.csv, beta*.csv (7 files)- Unclear origin/testing files
└── [scattered single files]   - Various content packs
```

### Issues

| Issue | Severity | Description |
|-------|----------|-------------|
| Prefix gaming | High | `00_FIX_*` loads before `00_PDM_*` due to reverse lexicographic sort |
| Scattered countries | High | TAG entries spread across 10+ files |
| text.csv line 1 | Critical | Empty row with 86 comma fields - causes localisation shifting |
| Encoding | Medium | UTF-8 bytes interpreted as Windows-1252 (mojibake) |
| Missing keys | Medium | 448 missing localisations (1.3%) |
| Validator bug | Low | `TARGET_COLUMNS = 19` should be `14` |

---

## Target Structure (40-45 Files)

### Core (4 files)
```
countries.csv              # ALL 583 country tags + ADJ forms
goods.csv                  # Trade goods
tech.csv                   # Techs, inventions
units.csv                  # Units, terrain, wargoals
```

### Politics (3 files)
```
governments.csv            # Political parties, ideologies
decisions.csv              # All decisions
reforms.csv                # Political/social reform text
```

### Events - Vanilla (8 files, alphabetically)
```
events_a.csv
events_b_c.csv
events_d_e.csv
events_f_l.csv
events_m_p.csv
events_q_s.csv
events_t.csv
events_u_z.csv
```

### Events - Mod (6 files)
```
events_persia.csv          # Persia-specific
events_gvg.csv             # GVG events
events_vip.csv             # VIP events
events_scenario.csv        # Darkness, House Divided
events_economic.csv        # Economic rework
events_special.csv         # Taiping, Scandinavian Famine
```

### News (2 files)
```
news.csv                   # Newspaper events
news_scenarios.csv         # Scenario-specific news
```

### Modifiers (2 files)
```
event_modifiers.csv        # All event modifiers + desc_*
triggered_modifiers.csv    # All triggered modifiers + desc_*
```

### UI/Interface (3 files)
```
ui_core.csv                # Core UI, ledger, budget
ui_map.csv                 # Map-related text
ui_military.csv            # Military interface
```

### Scenarios - Regional (10 files)
```
scenario_americas.csv      # Crownsteler Americas
scenario_east_indies.csv   # Crownsteler East Indies
scenario_europe.csv        # European scenario content
scenario_persia.csv        # Persia map/province text
scenario_asia.csv          # Asian scenario content
scenario_darkness.csv      # Darkness campaign
scenario_civilwar.csv      # House Divided (ACW)
scenario_special.csv       # One-off scenarios
```

### Miscellaneous (2 files)
```
misc.csv                   # Misc, GAGA, gtfo
overrides.csv              # True mod-specific overrides (minimal)
```

**Total**: ~40-45 files (down from 61, up from arbitrary consolidation)

---

## Implementation Phases

### Phase 0: Proof of Concept (CURRENT) ⚠️

**Goal**: Validate refactoring approach on text.csv before full rollout

| Task | Status | Notes |
|------|--------|-------|
| 0.1 | In Progress | Analyze text.csv structure and content |
| 0.2 | Pending | Refactor text.csv (fix line 1, normalize encoding) |
| 0.3 | Pending | Game test - verify no breaks |
| 0.4 | Pending | Document lessons learned |

**Success Criteria**:
- Game loads without errors
- No "KEY" strings visible in UI
- All text displays correctly

### Phase 1: Foundation (after POC success)

| Task | Git Commit |
|------|------------|
| Fix `validator.py:116` - `TARGET_COLUMNS = 14` | `fix: correct validator column count` |
| Scan for cross-file duplicate keys | `docs: add duplicate key analysis` |
| Generate baseline validation report | `docs: add baseline validation` |

### Phase 2: Stabilization

| Task | Git Commit |
|------|------------|
| Fix encoding across all CSVs | `fix: normalize encoding to Windows-1252` |
| Add 448 missing localisations | `feat: add missing localisations` |

### Phase 3: Rebaseline

| Task | Git Commit |
|------|------------|
| Create new 40-file structure | `refactor: create localisation rebaseline` |
| Merge countries from 10+ files → 1 | `refactor: consolidate countries to single file` |
| Merge events by alphabet | `refactor: organize events alphabetically` |
| Eliminate prefix gaming (merge FIX files) | `refactor: eliminate prefix gaming` |
| Validate consolidated system | `refactor: validate rebaselined localisation` |

### Phase 4: Completion

| Task | Git Commit |
|------|------------|
| Game test - full verification | `test: verify localisation refactoring` |
| Create LOCALISATION.md | `docs: add localisation guide` |
| Archive legacy files | `chore: archive legacy localisation` |

---

## File Mapping

### countries.csv (NEW - single source of truth)
**Source files to merge**:
- 00_PDM_countries.csv
- 000_persia_map_countries.csv
- 000_indies_map_countries.csv
- CountriesGVG.csv
- Scattered TAG entries in other files

### event_modifiers.csv (NEW - consolidated)
**Source files to merge**:
- 00_FIX_event_modifiers.csv
- All event-modifier entries scattered across event files

### events_*.csv (alphabetically organized)
**Source files**:
- 00_PDM_events.csv
- 00_PDM_events_2.csv
- 00_FIX_events_A-O.csv
- 00_FIX_events_P-Z.csv
- 000_persia_events.csv
- VIP_events.csv
- GVG_events.csv
- And others...

---

## Validation Checklist

- [ ] All files have exactly 14 columns
- [ ] Column 15 contains `x` terminator
- [ ] All files use Windows-1252 encoding
- [ ] All files use `\r\r\n` line endings
- [ ] No duplicate keys within files
- [ ] Countries: single file, 583 entries
- [ ] Total key count ≥ 34,487 (34,039 + 448 new)
- [ ] Zero missing keys
- [ ] Game loads without errors
- [ ] No "KEY" strings visible in UI

---

## Pilot Phase: text.csv Refactoring

**Current text.csv issues**:
1. Line 1: Empty row with 86 comma fields
2. Mixed content (UI, events, decisions, modifiers)
3. Possible encoding issues

**Refactoring steps**:
1. Fix line 1 empty row bug
2. Normalize encoding to Windows-1252
3. Verify line endings (\r\r\n)
4. Validate column count (14)
5. Game test

**Rollback**: `git checkout text.csv`

---

## Key Standards

| Attribute | Standard |
|-----------|----------|
| Encoding | Windows-1252 (ANSI) |
| Columns | 14 (key + 13 languages + x) |
| Delimiter | Semicolon (;) |
| Line Ending | \r\r\n (double carriage return) |
| Empty Lines | Forbidden |
| Prefix Gaming | Eliminated |

---

## Tools

| Tool | Purpose | Location |
|------|---------|----------|
| V2LocKit GUI | Validation, fixing | `app/v2lockit/` |
| check_missing_localizations.py | Find missing keys | `app/` |
| check_duplicate_localizations.py | Find duplicate keys | `app/` |

---

## Rollback Strategy

```bash
# Quick rollback (git-based)
git checkout localisation/
git clean -fd localisation/

# Rollback specific file
git checkout localisation/text.csv

# View changes before committing
git diff localisation/
```

---

## References

- [Victoria 2 Wiki - Localisation](https://vic2.paradoxwikis.com/Localisation)
- `docs/localisation_wiki.md` - Complete localisation reference
- `app/README.md` - Localisation tooling guide

---

*Generated for CoE_RoI_R mod development*
