# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**CoE_RoI_R** (Concert of Europe: Roar of Industry - Reignited) is a comprehensive total conversion mod for Victoria 2. Previously known as PDM_Concert, it extends the timeline from 1821-1946 and features 583 playable countries, an expanded map with 3,259 provinces, and extensive historical and alternate history content.

## Directory Structure

```
CoE_RoI_R/
├── common/              # Core game mechanics and definitions
│   ├── defines.lua      # Central configuration (timeline, great powers, mechanics)
│   ├── buildings.txt    # Factory and building definitions
│   ├── cultures.txt     # Culture groups and assimilation rules (3,189 lines)
│   ├── goods.txt        # Trade goods and properties
│   └── governments.txt  # Government types and mechanics
├── events/              # 173 event files (historical, flavor, mechanics)
├── decisions/           # 74 decision files (country-specific chains)
├── history/             # Starting conditions for countries, provinces, pops
│   └── countries/       # Country history files (TAG - Country Name.txt)
├── localisation/        # CSV-based multi-language files
├── technologies/        # Tech trees (army, commerce, culture, industry, navy)
├── gfx/                 # Flags, unit sprites, interface graphics
├── map/                 # Province definitions, terrain, adjacencies
├── units/               # Military unit definitions
├── poptypes/            # Population type definitions
└── ValidatorSettings.txt # Validation configuration
```

## Naming Conventions

### Event Files
- `00_*` - Setup and initialization events
- `0_*` - Major historical events
- `1_`, `2_` etc. - Chronological progression
- `+prefix_*` - Specific mechanics (e.g., `+education_RGO.txt`)
- Thematic names: `ACW.txt` (American Civil War), `ARAFlavor.txt` (Arabia)

### Decision Files
- `00_*`, `01_*` - Setup and flavor decisions
- Geographic/cultural: `Balkans.txt`, `AUS.txt` (Australia)
- Mechanic-specific: `Canals.txt`, `archaeology.txt`

### Country Files
- Format: `TAG - Country Name.txt` (e.g., `ENG - United Kingdom.txt`)
- Uses Victoria 2 three-letter country tags
- Located in `history/countries/`

## File Organization Patterns

1. **Prefix-based ordering**: Numeric prefixes (`00_`, `0_`, `1_`) control load order
2. **Geographic grouping**: Content organized by region (Arabia, Balkans, etc.)
3. **Thematic separation**: Mechanics vs. historical events vs. flavor content
4. **Comment-based organization**: Events use `#` comments for sections

## Scripting Patterns

### Country History Files ([history/countries/](history/countries/))
Structure for country initialization:
```lua
capital = [province_id]
primary_culture = [culture]
religion = [religion]
government = [government_type]
plurality = [value]
literacy = [value]
civilized = yes/no
prestige = [value]

# Political reforms
slavery = [level]
upper_house_composition = [level]
# ... more reforms

# Technologies
[tech_name] = 1

ruling_party = [TAG_party_name]
last_election = [YYYY.MM.DD]
upper_house = { [ideology] = [amount] }
```

### Events
Standard Victoria 2 event structure:
- Use `is_triggered_only = yes` for scripted events
- Use `mean_time_to_happen` for random events
- Limit clauses use `AND`/`OR` with `{ }` blocks
- Comments with `#` for organization

### Decisions
Structure in `political_decisions = { }` blocks:
- `potential` - When decision appears
- `allow` - When decision can be taken
- `effect` - What happens
- `ai_will_do` - AI weighting

## Validation

The mod uses [ValidatorSettings.txt](ValidatorSettings.txt) with:
- `NoCheckKey` - Disables localization key checking (keys are used throughout)
- Relaxed validation for development workflow

When adding new events or decisions:
- Ensure all localization keys are added to CSV files in [localisation/](localisation/)
- Use the Victoria 2 validator tool to check for syntax errors
- Comments are used extensively to disable content without deletion

## Key Configuration

- **Timeline**: 1821.9.1 to 1946.12.31 (defined in [common/defines.lua](common/defines.lua))
- **Great Powers**: 8 nations
- **Badboy Limit**: 50
- **Colonial Rank**: 16 (minimum rank to colonize)

## Development Notes

- No build process: Victoria 2 loads mod files directly
- Git version control with feature branch workflow
- Localization uses CSV format for easy translation management
- The mod contains significant commented-out content (marked with `#`) for debugging or alternate paths
- Map modifications include backup files suggesting active development

## Working with This Codebase

When adding new content:
1. **Events**: Place in appropriately named/prefixed file in [events/](events/)
2. **Decisions**: Add to thematic file or create new one in [decisions/](decisions/)
3. **Countries**: Create `TAG - Name.txt` in [history/countries/](history/countries/)
4. **Localization**: Add keys to CSV files in [localisation/](localisation/)
5. **Technologies**: Define in appropriate [technologies/](technologies/) subdirectory
6. **Common definitions**: Add to relevant file in [common/](common/)

When modifying existing content:
- Preserve comment structure and organization
- Maintain prefix-based load ordering
- Add localization for any new text keys
- Test with Victoria 2 validator before committing
