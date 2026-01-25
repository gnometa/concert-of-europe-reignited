# Localisation Duplicate Fix Summary

## Analysis Complete

**Date:** 2025-01-25
**Mod:** CoE_RoI_R (Concert of Europe: Roar of Industry - Reignited)
**Location:** `D:\Steam\steamapps\common\Victoria 2\mod\CoE_RoI_R\localisation\`

---

## Quick Statistics

| Metric | Count |
|--------|-------|
| **Total CSV Files** | 61 |
| **Total Localisation Entries** | 36,867 |
| **Unique Keys** | 35,060 |
| **Duplicate Entries** | 1,807 |
| **Within-File Duplicates** | 255 occurrences in 15 files |
| **Cross-File Duplicates** | 1,532 keys with conflicts |

---

## Tools Created

### 1. `analyze_localisation_duplicates.py`
**Purpose:** Scan and report duplicate issues

**Usage:**
```bash
# Full analysis
python app/analyze_localisation_duplicates.py

# Show only within-file duplicates
python app/analyze_localisation_duplicates.py --intra

# Show only cross-file duplicates
python app/analyze_localisation_duplicates.py --inter --limit 100

# Show only format issues
python app/analyze_localisation_duplicates.py --format

# Show file load order
python app/analyze_localisation_duplicates.py --order
```

### 2. `fix_localisation_duplicates.py`
**Purpose:** Automatically fix duplicate issues

**Usage:**
```bash
# Dry run (show what would change)
python app/fix_localisation_duplicates.py --dry-run --all

# Generate cross-file duplicate report
python app/fix_localisation_duplicates.py --report --output app/localisation_duplicate_report.md

# Fix within-file duplicates only
python app/fix_localisation_duplicates.py --fix-within

# Fix format issues only
python app/fix_localisation_duplicates.py --fix-format

# Apply all automatic fixes
python app/fix_localisation_duplicates.py --all
```

---

## Issues Found

### 1. Within-File Duplicates (255 occurrences)

**Most Affected Files:**

| File | Duplicates | Type |
|------|-----------|------|
| `newstext_3_01.csv` | 12 | Literature event text |
| `00_PDM_tech.csv` | 11 | Tech name/description pairs |
| `VIP_events.csv` | 7 | Comment section headers |
| `00_PDM_GAGA.csv` | 2 | Effect descriptions |
| `newspaper_text.csv` | 4 | Template keys |

**Example:**
```csv
# 00_PDM_tech.csv has duplicate tech entries:
bakery_power;Bakeries and Mills;;;;;;;x;  # Line 438
...
bakery_power;Bakeries and Mills;;;;;;;x;  # Line 496 (DUPLICATE)
```

### 2. Cross-File Duplicates (1,532 keys)

**Major Conflicts:**

| File Pair | Conflicts | Notes |
|----------|-----------|-------|
| `00_FIX_modifiers.csv` vs `00_FIX_event_modifiers.csv` | 38 | Same modifiers, different names |
| `00_FIX_triggered_modifiers.csv` vs `0000_economic_rework.csv` | 46 | Economic tier modifiers |
| `text.csv` vs `00_PDM_countries.csv` | 100+ | Country name conflicts |
| `text.csv` vs `00_PDM_map.csv` | 50+ | Province name conflicts |
| `text.csv` vs `00_PDM_tech.csv` | 30+ | Tech name conflicts |

**Example Conflict:**
```csv
# text.csv (LOW priority - gets overridden)
ABU;Abu Dhabi;;;;;;;x;
ABU_ADJ;Abu Dhabian;;;;;;;x;

# 00_PDM_countries.csv (HIGH priority - wins)
ABU;Trucial States;;;;;;;x;
ABU_ADJ;Trucial;;;;;;;x;

# RESULT: Game shows "Trucial States" instead of "Abu Dhabi"
```

### 3. Format Issues

**File: `0000_economic_rework.csv`**
- **337 format issues**
- Column count mismatch (16 columns instead of 14)
- Missing/incorrect end markers
- Extra trailing commas

---

## Recommended Fix Strategy

### Phase 1: Automatic Fixes (Safe)

Run these commands in sequence:

```bash
# 1. Create backup
git checkout -b backup/localisation-before-fix
git commit -am "backup: localisation before duplicate fixes"

# 2. Fix within-file duplicates
python app/fix_localisation_duplicates.py --fix-within

# 3. Fix format issues
python app/fix_localisation_duplicates.py --fix-format

# 4. Commit automatic fixes
git commit -am "fix: remove within-file duplicates and fix format issues"
```

### Phase 2: Manual Review Required

The cross-file duplicate report (`app/localisation_duplicate_report.md`) contains **hundreds of value conflicts** that require manual review.

**Key Categories to Review:**

1. **Modifier Names** (38 conflicts between `00_FIX_modifiers.csv` and `00_FIX_event_modifiers.csv`)
   - Same modifier, different display names
   - **Recommendation:** Consolidate to single authoritative name per modifier

2. **Economic Tiers** (46 conflicts between `00_FIX_triggered_modifiers.csv` and `0000_economic_rework.csv`)
   - Same modifier, different naming styles
   - **Recommendation:** Use `0000_economic_rework.csv` names (highest priority)

3. **Country Names** (100+ conflicts)
   - `text.csv` has traditional names
   - `00_PDM_countries.csv` has mod-specific names
   - **Recommendation:** Remove duplicates from `text.csv`, keep in `00_PDM_countries.csv`

4. **Province Names** (50+ conflicts)
   - Similar to country names
   - **Recommendation:** Remove duplicates from `text.csv`, keep in `00_PDM_map.csv`

5. **Tech Names** (30+ conflicts)
   - **Recommendation:** Remove duplicates from `text.csv`, keep in `00_PDM_tech.csv`

---

## File Load Priority Reference

```
HIGHEST Priority (overrides everything):
  0000_economic_rework.csv
  000_crownsteler_*.csv
  000_persia_*.csv
  000_indies_*.csv

HIGH Priority (overrides standard):
  00_FIX_*.csv
  00_PDM_*.csv

LOW Priority (can be overridden):
  text.csv
  beta*.csv
  named files
```

**Rule:** When the same key appears in multiple files, the **HIGHER priority** file's value is used in-game.

---

## Before Applying Fixes

1. **Review the report:** Check `app/localisation_duplicate_report.md`
2. **Understand impacts:** Some duplicates may be intentional (overrides)
3. **Create backup:** Use git branch or copy folder
4. **Test changes:** After each phase, test in-game

---

## Success Criteria

After fixes are applied:

- [ ] Zero within-file duplicates
- [ ] All CSV files have 14 columns
- [ ] All files end with `;x;` pattern
- [ ] Cross-file duplicates are reviewed and intentional
- [ ] No broken localisation in-game

---

## Files Generated

| File | Purpose |
|------|---------|
| `app/analyze_localisation_duplicates.py` | Analysis tool |
| `app/fix_localisation_duplicates.py` | Fix automation tool |
| `app/LOCALISATION_FIX_PLAN.md` | Detailed fix plan |
| `app/localisation_duplicate_report.md` | Cross-file conflict report |
| `app/LOCALISATION_FIX_SUMMARY.md` | This file |

---

## Next Steps

1. **Review this summary** and understand the scope
2. **Read the full report** at `app/localisation_duplicate_report.md`
3. **Decide on approach:**
   - Apply automatic fixes only
   - Manually review and fix cross-file conflicts
   - Selective fixing by file/category
4. **Execute fixes** with proper backups
5. **Validate** with re-run of analysis script
6. **Test in-game** to ensure no broken text
