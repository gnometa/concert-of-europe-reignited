# CLAUDE.md

This file provides guidance when working with code in the **CoE_RoI_R** (Concert of Europe: Roar of Industry - Reignited) mod for Victoria 2.

## Project Overview

CoE_RoI_R is a comprehensive total conversion mod for Victoria 2, previously known as PDM_Concert. Key features:
- **Timeline**: 1821.9.1 to 1946.12.31 (defined in `common/defines.lua`)
- **Countries**: 583 playable nations (522 with history files)
- **Map**: 3,259 provinces across expanded world map
- **Great Powers**: 8 nations | **Badboy Limit**: 50 | **Colonial Rank**: 16

## Directory Structure

```
CoE_RoI_R/
├── common/              # Core game mechanics (26 config files + 583 country defs)
│   ├── countries/       # 583 country definition files (TAG.txt)
│   ├── defines.lua      # Central config (751 lines, 7 sections)
│   ├── cultures.txt     # Culture groups (138KB, extensive assimilation rules)
│   ├── ideologies.txt   # 9 ideologies in 4 groups (1,186 lines)
│   ├── governments.txt  # 33 government types with flag variants
│   ├── cb_types.txt     # Casus belli definitions (196KB)
│   ├── religion.txt     # Religion definitions (138KB)
│   └── goods.txt        # 28 trade goods (4 categories)
├── events/              # 170 event files including maintenance systems
│   └── 00_CoE_RoI.txt   # Core maintenance events (ghost cleanup, migration)
├── decisions/           # 74 decision files
│   ├── NationalUnification.txt  # 1,449 lines of formation decisions
│   └── gtfo.txt         # Largest decision file (108KB)
├── history/             # Starting conditions
│   ├── countries/       # 522 country history files
│   ├── provinces/       # 2,830 province histories
│   ├── pops/            # 62 population files
│   ├── units/           # 437 starting military units
│   ├── diplomacy/       # 8 diplomatic relationship files
│   └── wars/            # 17 active war definitions
├── localisation/        # 56 CSV localization files (~4MB total)
│   ├── text.csv         # Primary text (3.7MB)
│   └── 00_PDM_events.csv # Event localization (988KB)
├── technologies/        # 5 tech tree files (~287KB total)
├── inventions/          # 9 invention files (122KB other_inventions.txt)
├── poptypes/            # 13 population types (custom: 00_urban_poor)
├── units/               # 24 military unit definitions
├── gfx/                 # 12,396 graphics files (flags, sprites, UI)
├── map/                 # Province map data, terrain, adjacencies
│   └── definition.csv   # Province definitions (89KB)
├── interface/           # 19 interface definition files
└── news/                # 9 newspaper event files
```

## Key Configuration Sections (defines.lua)

| Section | Purpose | Notable Settings |
|---------|---------|------------------|
| `country` | National mechanics | `GREAT_NATIONS_COUNT=8`, `BADBOY_LIMIT=50`, `COLONIAL_RANK=16` |
| `economy` | Economic simulation | Factory behavior, trade caps, bankruptcy rules |
| `military` | Combat mechanics | `BASE_COMBAT_WIDTH=30`, `POP_SIZE_PER_REGIMENT=5000` |
| `diplomacy` | Diplomatic actions | Peace costs, infamy multipliers, alliance mechanics |
| `pops` | Population dynamics | Assimilation, promotion, literacy, militancy |
| `ai` | AI behavior tuning | Army composition, investment chance, peace logic |
| `graphics` | Visual settings | City sprawl, mesh pools |

## Political System

### Ideologies (4 Groups, 9 Types)
- **fascist_group**: `fascist`, `Executive` (custom)
- **conservative_group**: `reactionary`, `pro_slavery` (custom), `conservative`
- **socialist_group**: `socialist`, `communist`
- **liberal_group**: `liberal`, `anarcho_liberal`

### Government Types (33 with flag variants)
Each type has up to 3 flag variants (e.g., `democracy`, `democracy2`, `democracy3`):
- Democracies, HMS governments, Prussian constitutionalism
- Absolute/Constitutional monarchies, Theocracies
- Socialist/Proletarian dictatorships
- Fascist/Presidential/Bourgeois dictatorships

## Population Types (13)

Standard: `aristocrats`, `artisans`, `bureaucrats`, `capitalists`, `clergymen`, `clerks`, `craftsmen`, `farmers`, `labourers`, `officers`, `slaves`, `soldiers`

**Custom**: `00_urban_poor` (166KB definition - detailed urban poor mechanics)

## Trade Goods Categories

| Category | Goods |
|----------|-------|
| **military_goods** | military_industry |
| **industrial_goods** | heavy_industry |
| **consumer_goods** | food_industry, light_industry, luxury_industry |
| **raw_material_goods** | cotton, dye, wool, silk, coal, sulphur, iron, timber, tropical_wood, rubber, oil, precious_metal, copper, lead, cattle, fish, fruit, grain, tobacco, tea, coffee, opium, sugar, spices, horses |

## Naming Conventions

### Event Files
- `00_*` - Core setup, maintenance events (e.g., `00_CoE_RoI.txt`)
- `0_*` - System mechanics (demographics, colony types)
- `+prefix_*` - Specific mechanics (e.g., `+education_RGO.txt`)
- `*Flavor.txt` - Country-specific flavor events (e.g., `ENGFlavor.txt`)
- Thematic names: `ACW.txt`, `GreatWar_Events.txt`, `Olympics.txt`

### Decision Files
- `00_*`, `01_*` - Setup and system decisions
- Country codes: `ENG.txt`, `RUS.txt`, `Germany.txt`
- Geographic: `Balkans.txt`, `SouthAmerica.txt`
- Mechanics: `NationalUnification.txt`, `Canals.txt`, `land_reform.txt`

### Country History Files
- Format: `TAG - Country Name.txt`
- Example: `ENG - United Kingdom.txt`, `PRU - Prussia.txt`
- Located in `history/countries/`

## Architecture Patterns

### Event Structure
```
country_event = {
    id = [unique_number]
    title = "[localization_key]"
    desc = "[localization_key]"
    
    is_triggered_only = yes  # OR
    trigger = { [conditions] }
    mean_time_to_happen = { months = [value] }
    
    option = {
        name = "[localization_key]"
        [effects]
    }
}
```

### Decision Structure
```
political_decisions = {
    decision_name = {
        potential = { [visibility conditions] }
        allow = { [availability conditions] }
        effect = { [outcomes] }
        ai_will_do = { factor = [weight] }
    }
}
```

### Country History Structure
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

# Technologies
[tech_name] = 1

ruling_party = [TAG_party_name]
last_election = [YYYY.MM.DD]
upper_house = { [ideology] = [amount] }
```

## Advanced Mod Mechanics

### Game Master System (BHU)
Bhutan (`BHU`) is used as a "Game Master" country for background maintenance:
- **Ghost Unit Cleanup**: Removes orphaned military units from non-existent countries
- **State Population Display**: Updates province modifiers based on population tiers
- **Random Migration**: Triggers population migration events
- **Vassal Cleanup**: Handles orphaned vassal relationships

### Maintenance Events (00_CoE_RoI.txt)
- Event IDs 99991-99999: Core maintenance systems
- Event IDs 6016818-6016821: Ghost unit cleanup chain
- Uses province 2127-2128 as "ghost country" staging area
- Runs via `is_triggered_only` or low MTTH triggers

### State Population Modifiers
The mod tracks state population with province modifiers:
- `s_pop_not_100k`, `s_pop_100k`, `s_pop_250k`
- `s_pop_500k`, `s_pop_1000k`, `s_pop_2500k`

### Land Property Reform
Event 99999: Automatic deregulation of land property when conditions met

## File Statistics

| Category | Count | Notable Size |
|----------|-------|--------------|
| Events | 170 files | `political_leaders.txt` (261KB), `GreatWar_Events.txt` (190KB) |
| Decisions | 74 files | `gtfo.txt` (108KB), `NationalUnification.txt` (26KB) |
| Countries | 583 defs | History for 522 |
| Provinces | 3,259 | Via `map/definition.csv` |
| Localization | 56 CSVs | ~4MB total |
| Graphics | 12,396 | Flags, units, UI |

## Development Workflow

### Adding Content

1. **Events**: Add to appropriate file in `events/`, use unique ID range
2. **Decisions**: Add to thematic file in `decisions/`
3. **Countries**: Create `TAG - Name.txt` in `history/countries/`
4. **Localization**: Add keys to CSVs in `localisation/`
5. **Technologies**: Define in `technologies/` subdirectory

### Common Patterns

- **Commented-out code**: Extensive use of `#` for disabled features/alternate paths
- **Flag variants**: Government types use numbered variants (`democracy`, `democracy2`, `democracy3`)
- **Maintenance events**: Use dedicated country (BHU) as trigger anchor
- **Backup files**: Map files include backups (e.g., `provinces_backup.bmp`)

### Validation
- `ValidatorSettings.txt` with `NoCheckKey` for relaxed localization checking
- Use Victoria 2 validator tool before committing
- Test in-game for complex event chains

## Event ID Ranges

| Range | Usage |
|-------|-------|
| 99991-99999 | Core maintenance events |
| 6016818-6016821 | Ghost unit cleanup |
| Other ranges | Country/feature specific (see `EventIDs.txt`) |

## Quick Reference

- **Base Tax Efficiency**: 50%
- **Pop Size Per Regiment**: 5,000
- **Years of Nationalism**: 10
- **Base Truce Duration**: 60 months
- **Campaign Duration**: 6 months
- **Tech Year Span**: 50 years
- **Colonial Liferating**: 30
