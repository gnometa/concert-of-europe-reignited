# Localisation Fix Plan for CoE_RoI_R

## Executive Summary

**Analysis Date:** 2025-01-25
**Total Files:** 61 CSV files
**Total Entries:** 36,867
**Unique Keys:** 35,060
**Duplicate Issues:** 1,807

### Issues Breakdown
| Issue Type | Count | Affected Files |
|------------|-------|----------------|
| Within-file duplicates | 255 occurrences | 15 files |
| Cross-file duplicates | 1,532 keys | All files |
| Format compliance issues | ~350+ | 1+ files |

---

## File Load Priority System

Victoria 2 loads localisation files in **reverse lexicographic order** (Z→A, 9→0).

**Priority Levels:**
- **HIGHEST**: `0000_*` prefix (overrides everything)
- **HIGH**: `000_*` prefix (overrides most)
- **HIGH**: `00_*` prefix (overrides standard)
- **LOW**: Named files (can be overridden)

**Key Principle:** Later files override earlier ones for matching keys.

---

## Issue Category 1: Within-File Duplicates

### Impact
Later occurrences in the same file override earlier ones. This is typically unintentional and creates confusion.

### Files Affected (15 files)

| File | Duplicate Count | Notes |
|------|----------------|-------|
| `00_PDM_tech.csv` | 11 | Tech name/desc pairs duplicated |
| `newstext_3_01.csv` | 12 | Literature event text |
| `VIP_events.csv` | 7 | Comment section headers |
| `00_PDM_GAGA.csv` | 2 | Effect descriptions |
| `newspaper_text.csv` | 4 | Template keys |
| `beta1.csv` | 2 | UI element keys |
| `beta2.csv` | 1 | UI element key |
| `darkness.csv` | 1 | Crisis text |
| `1.3.csv` | 1 | Factory tooltip |
| `00_PDM_goods.csv` | 1 | Good name |
| `00_PDM_news.csv` | 1 | Event description |
| `GVG_events.csv` | 1 | Comment header |
| `housedivided.csv` | 0 | - |
| `housedivided2_1.csv` | 0 | - |
| `housedivided2_2.csv` | 0 | - |
| `housedivided2_3.csv` | 0 | - |

### Fix Strategy: Within-File Duplicates

1. **Comment Headers**: Remove duplicate comment keys (e.g., `##### Country #####`)
2. **Exact Duplicates**: Remove all but the first occurrence
3. **Similar Duplicates**: Review and merge if text is different

**Example Fix:**
```csv
# BEFORE (00_PDM_tech.csv)
bakery_power;Bakeries and Mills;;;;;;;x;
... (other lines)
bakery_power;Bakeries and Mills;;;;;;;x;  # DUPLICATE

# AFTER
bakery_power;Bakeries and Mills;;;;;;;x;
... (other lines)
# Duplicate removed
```

---

## Issue Category 2: Cross-File Duplicates

### Impact
Higher-priority files (000*, 00*) override lower-priority files. Some overrides are intentional (mod fixes), but many are likely accidental.

### Common Duplicate Patterns

| Pattern | Example | Intentional? |
|---------|---------|--------------|
| FIX files overriding base | `00_FIX_*` overriding `text.csv` | **YES** - Bug fixes |
| Province names | `00_PDM_map.csv` vs `text.csv` | **MAYBE** - Geo updates |
| Tech names | `00_PDM_tech.csv` vs `text.csv` | **MAYBE** - Rebalancing |
| Country names | `00_PDM_countries.csv` vs `text.csv` | **MAYBE** - New tags |
| Event text | `00_PDM_events.csv` vs `text.csv` | **MAYBE** - Event updates |

### Key Duplicate Examples

```csv
# text.csv (LOW priority) gets overridden by:
ABU;Abu Dhabi;;;;;;;x;
ABU_ADJ;Abu Dhabian;;;;;;;x;

# 00_PDM_countries.csv (HIGH priority) - SAME KEY, DIFFERENT VALUE
ABU;Trucial States;;;;;;;x;
ABU_ADJ;Trucial;;;;;;;x;

# RESULT: "Trucial States" displays instead of "Abu Dhabi"
```

### Fix Strategy: Cross-File Duplicates

#### Step 1: Identify Intentional Overrides
Files explicitly named with `FIX` or `00_` prefixes that override base content are typically intentional:
- `00_FIX_*` files → **Keep as overrides**
- `0000_*` files → **Keep as highest priority**

#### Step 2: Resolve Unintentional Duplicates

For each duplicate key appearing across multiple files:

1. **Check priority order:** Higher priority (later) file wins
2. **Compare values:**
   - **Identical values:** Remove from lower-priority files
   - **Different values:** Decide which is correct and remove others

3. **Special cases:**
   - **Comment keys** (`#`, `###`): Remove all but highest priority
   - **Province names** (`XXX_1234`): Keep in `00_PDM_map.csv` if different
   - **Country names** (`TAG`, `TAG_ADJ`): Consolidate into `00_PDM_countries.csv`
   - **Tech names**: Consolidate into `00_PDM_tech.csv`

#### Step 3: File Consolidation Plan

**Merge similar content into authoritative files:**

| Content Type | Authoritative File | Remove From |
|--------------|-------------------|-------------|
| Country names/adjectives | `00_PDM_countries.csv` | `text.csv`, beta files |
| Province names | `00_PDM_map.csv` | `text.csv` |
| Tech names/descriptions | `00_PDM_tech.csv` | `text.csv`, beta files |
| Good names | `00_PDM_goods.csv` | `text.csv` |
| Event text | `00_PDM_events.csv` | `text.csv` |
| Modifiers | `00_FIX_event_modifiers.csv` | Keep distributed |
| UI elements | `00_PDM_GAGA.csv` | Keep distributed |

---

## Issue Category 3: Format Compliance Issues

### File: `0000_economic_rework.csv` (337 issues)

**Problems:**
- Column count mismatch (16 instead of 14)
- Missing end markers (`x`)
- Extra commas at line end

**Example:**
```csv
# BEFORE (malformed)
money_hoarder_1;Money Hoarder;;;;;;;;x,,,,,,

# AFTER (correct)
money_hoarder_1;Money Hoarder;;;;;;;;x;
```

### Fix Strategy: Format Issues

1. **Fix column counts:** Ensure exactly 14 semicolon-separated fields
2. **Fix end markers:** Last column must be `x`
3. **Remove trailing commas:** Eliminate extra commas after `x`
4. **Validate encoding:** Ensure Windows-1252 (ANSI) encoding

---

## Implementation Plan

### Phase 1: Fix Format Issues (Quick Win)
1. Fix `0000_economic_rework.csv` format
2. Validate all CSV files have 14 columns
3. Ensure proper line endings

### Phase 2: Remove Within-File Duplicates
1. Process each affected file
2. Remove duplicate comment headers
3. Remove exact duplicate entries
4. Review and merge similar duplicates

### Phase 3: Resolve Cross-File Duplicates
1. **Priority 1:** Consolidate country names to `00_PDM_countries.csv`
2. **Priority 2:** Consolidate province names to `00_PDM_map.csv`
3. **Priority 3:** Consolidate tech names to `00_PDM_tech.csv`
4. **Priority 4:** Review and remove comment key duplicates
5. **Priority 5:** Review remaining value conflicts

### Phase 4: Validation
1. Re-run duplicate analysis
2. Verify all duplicates resolved
3. Test in-game display

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing overrides | HIGH | Commit before changes; test thoroughly |
| Encoding corruption | MEDIUM | Use validated CSV editor |
| Accidental deletion | HIGH | Keep backups; review changes |
| In-game display issues | MEDIUM | Test all major categories |

---

## Backup Plan

Before making changes:
1. **Create backup branch:** `git checkout -b backup/localisation-before-fix`
2. **Copy folder:** `localisation/` → `localisation.backup/`
3. **Commit current state:** `git commit -m "backup: localisation before fix"`

---

## Success Criteria

- [ ] Zero within-file duplicates
- [ ] Only intentional cross-file duplicates remain
- [ ] All CSV files have 14 columns
- [ ] All files end with `;x;` pattern
- [ ] Encoding is Windows-1252 (ANSI)
- [ ] No broken localisation in-game

---

## Tools Required

1. **Python script:** `analyze_localisation_duplicates.py` (✓ created)
2. **CSV editor:** LibreOffice Calc or similar with CSV support
3. **Encoding converter:** Notepad++ or similar for encoding validation
4. **Git:** For version control and rollback

---

## Next Steps

1. Review this plan and approve approach
2. Create backup branch
3. Execute Phase 1 (format fixes)
4. Execute Phase 2 (within-file duplicates)
5. Execute Phase 3 (cross-file duplicates - may require manual review)
6. Validate with re-run of analysis script
7. In-game testing
