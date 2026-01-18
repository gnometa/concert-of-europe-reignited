# Concert of Europe: Roar of Industry - Reignited

A comprehensive total conversion modification for *Victoria II: Heart of Darkness* (v3.04), extending the grand strategy experience from September 1821 through December 1946.

> **Formerly known as:** PDM_Concert

![Version](https://img.shields.io/badge/version-Development-blue)
![Victoria 2](https://img.shields.io/badge/Victoria_2-3.04-green)
![License](https://img.shields.io/badge/license-Modular-orange)

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Mod Statistics](#mod-statistics)
- [Project Structure](#project-structure)
- [Development](#development)
- [Contributing](#contributing)
- [Credits](#credits)
- [License](#license)

---

## Overview

**Concert of Europe: Roar of Industry - Reignited** (CoE_RoI_R) is an ambitious total conversion mod that transforms Victoria 2 into a profoundly expanded historical sandbox. Spanning 125 years from the post-Napoleonic era to the dawn of the Cold War, players guide nations through the Industrial Revolution, the age of imperialism, and into the tumultuous 20th century.

### Key Specifications

| Setting | Value |
|---------|-------|
| **Timeline** | 1821.9.1 – 1946.12.31 |
| **Playable Nations** | 583 (522 with history files) |
| **Provinces** | 3,259 |
| **Great Powers** | 8 |
| **Infamy Limit** | 50 |
| **Colonial Rank** | 16 |

---

## Features

### Expanded Timeline
- **Start Date:** September 1, 1821 — The post-Napoleonic Concert of Europe
- **End Date:** December 31, 1946 — Extended into the post-WWII era

### Global Scope
- **583 playable nations** across a vastly expanded world map
- **522 countries** with detailed historical starting configurations
- Comprehensive coverage of Africa, Asia, the Americas, Europe, and Oceania

### Enhanced Systems
- **9 ideologies** organized into 4 political groups
- **33 government types** with multiple flag variants
- **196KB** of casus belli definitions for nuanced warfare
- **28 trade goods** across 4 economic categories
- **138KB** of culture definitions with extensive assimilation rules

### Political Mechanics
- Custom ideologies including `pro_slavery` and `Executive`
- Sophisticated party systems with economic, trade, religious, citizenship, and war policies
- Dynamic political reform and social reform systems

---

## Installation

### Prerequisites
- **Victoria II: Heart of Darkness** (version 3.04)
- Approximately **2 GB** of free disk space

### Manual Installation

1. **Download** the latest release or clone this repository
2. **Extract/copy** the `CoE_RoI_R` folder to your Victoria 2 mod directory:
   ```
   Steam\steamapps\common\Victoria 2\mod\CoE_RoI_R\
   ```
3. **Verify** the `.mod` file (`CoE_RoI_R.mod`) is present in the mod directory
4. **Launch** Victoria 2 and select "Concert of Europe: Roar of Industry - Reignited" from the launcher

### Installation Path (Windows)
```
D:\Steam\steamapps\common\Victoria 2\mod\CoE_RoI_R\
```

---

## Mod Statistics

| Category | Count | Notable Details |
|----------|-------|-----------------|
| **Countries** | 583 definitions | 522 with history files |
| **Provinces** | 3,259 | Expanded world map |
| **Events** | 170 files | `political_leaders.txt` (261KB) |
| **Decisions** | 74 files | `gtfo.txt` (108KB) |
| **Technologies** | 5 files | ~287KB total |
| **Inventions** | 9 files | `other_inventions.txt` (122KB) |
| **Localization** | 56 CSVs | ~4MB total text |
| **Graphics** | 12,396 files | Flags, unit sprites, UI elements |
| **Population Types** | 13 types | Custom `urban_poor` type |

---

## Project Structure

```
CoE_RoI_R/
├── common/                 # Core game mechanics
│   ├── countries/          # 583 country definition files (TAG.txt)
│   ├── defines.lua         # Central configuration (751 lines)
│   ├── cultures.txt        # Culture groups (138KB)
│   ├── ideologies.txt      # 9 ideologies in 4 groups
│   ├── governments.txt     # 33 government types
│   ├── cb_types.txt        # Casus belli definitions (196KB)
│   ├── religions.txt       # Religion definitions (138KB)
│   └── goods.txt           # 28 trade goods
├── events/                 # 170 event files
│   └── 00_CoE_RoI.txt      # Core maintenance events
├── decisions/              # 74 decision files
│   ├── NationalUnification.txt  # Formation decisions (1,449 lines)
│   └── gtfo.txt            # Largest decision file (108KB)
├── history/                # Starting conditions
│   ├── countries/          # 522 country history files
│   ├── provinces/          # 2,830 province histories
│   ├── pops/               # 62 population files
│   ├── units/              # 437 starting military units
│   ├── diplomacy/          # 8 diplomatic relationship files
│   └── wars/               # 17 active war definitions
├── localisation/           # 56 CSV localization files (~4MB)
│   ├── text.csv            # Primary text (3.7MB)
│   └── 00_PDM_events.csv   # Event localization (988KB)
├── technologies/           # 5 tech tree files
├── inventions/             # 9 invention files
├── poptypes/               # 13 population types
├── units/                  # 24 military unit definitions
├── gfx/                    # 12,396 graphics files
├── map/                    # Province data, terrain, adjacencies
├── interface/              # 19 interface definition files
└── news/                   # 9 newspaper event files
```

---

## Development

### Core Configuration (`defines.lua`)

The mod's central configuration is divided into 7 sections:

| Section | Purpose |
|---------|---------|
| `country` | National mechanics, prestige, infamy, reforms |
| `economy` | Factory behavior, trade, bankruptcy |
| `military` | Combat mechanics, unit organization |
| `diplomacy` | Peace costs, alliances, influence |
| `pops` | Assimilation, promotion, literacy, militancy |
| `ai` | AI behavior tuning |
| `graphics` | Visual settings and performance |

### Notable Settings

```lua
-- Country Section
GREAT_NATIONS_COUNT = 8
BADBOY_LIMIT = 50
COLONIAL_RANK = 16
YEARS_OF_NATIONALISM = 10

-- Military Section
BASE_COMBAT_WIDTH = 30
POP_SIZE_PER_REGIMENT = 5000

-- Economy Section
BASE_COUNTRY_TAX_EFFICIENCY = 0.50
```

### Game Master System

The mod utilizes **Bhutan (BHU)** as a "Game Master" country for background maintenance:

- **Ghost Unit Cleanup:** Removes orphaned military units
- **State Population Display:** Updates province modifiers
- **Random Migration:** Triggers population migration events
- **Vassal Cleanup:** Handles orphaned vassal relationships

Maintenance events are located in `events/00_CoE_RoI.txt` (ID range: 99991-99999).

---

## Contributing

### Development Tools

The project includes several utility scripts for development:

#### Localization Checker
```bash
python check_missing_localizations.py
```
Detects missing localizations for modifiers, events, and decisions.

#### Graphics Conversion
```bash
# Install ImageMagick
winget install --id ImageMagick.ImageMagick

# Convert PNG to TGA (flag format)
magick input.png output.tga

# Batch conversion
magick mogrify -format tga *.png
```

### Adding Content

When contributing new content:

1. **Events:** Add to `events/` using unique ID ranges
2. **Decisions:** Add to thematic files in `decisions/`
3. **Countries:** Create files in `common/countries/` and `history/countries/`
4. **Localization:** Add keys to appropriate CSVs in `localisation/`

### Localization Guidelines

- **Encoding:** Windows-1252 (ANSI) — *not* UTF-8
- **Delimiter:** Semicolon (`;`)
- **Line ending:** Must end with `;x`
- **Files:**
  - Event modifiers → `localisation/00_PDM_events.csv`
  - Economic modifiers → `localisation/0000_economic_rework.csv`
  - Country-specific → `localisation/[TAG]_events.csv`

---

## Credits

This mod builds upon the foundation of the original *PDM (Pop Demand Mod)* and continues the development of *Concert of Europe*.

### Core Contributors
- The original PDM development team
- Concert of Europe developers
- Community contributors and testers

---

## License

This mod is provided as-is for educational and entertainment purposes.

**Victoria II** is a trademark of Paradox Interactive AB. This mod is not affiliated with or endorsed by Paradox Interactive.

---

## Quick Links

- [Paradox Wiki Modding Guide](https://vic2.paradoxwikis.com/Modding)
- [List of Conditions](https://vic2.paradoxwikis.com/List_of_conditions)
- [List of Effects](https://vic2.paradoxwikis.com/List_of_effects)
- [List of Scopes](https://vic2.paradoxwikis.com/List_of_scopes)

---

## Changelog

### Recent Commits
- `7295c07` — feat: add comprehensive localization tools and fix missing localizations
- `111024fa` — fix: correct definition.csv path reference in default.map
- `6cb4c256` — docs: add ImageMagick graphics conversion tool reference
- `8f4ab105` — docs: enhance CLAUDE.md with comprehensive Victoria 2 modding reference

---

## Support

For bug reports, feature requests, or questions, please use the GitHub issue tracker.

*The history of the world is but the biography of great men.* — Thomas Carlyle
