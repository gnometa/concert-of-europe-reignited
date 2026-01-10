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

---

# Victoria 2 Modding Reference Guide

> Comprehensive modding reference extracted from the [Paradox Wiki Modding Guide](https://vic2.paradoxwikis.com/Modding).

---

## Scripting Fundamentals

### Boolean Operators

| Operator | Description | Usage |
|----------|-------------|-------|
| `AND` | All conditions must be true (default behavior) | `AND = { condition1 condition2 }` |
| `OR` | At least one condition must be true | `OR = { condition1 condition2 }` |
| `NOT` | Condition must be false | `NOT = { condition }` |

### Scope Keywords

| Keyword | Description |
|---------|-------------|
| `THIS` | Refers to the current country/province receiving the event |
| `FROM` | Refers to the country/province that triggered the event |
| `ROOT` | Refers to the original scope in nested contexts |

---

## Conditions Reference (Triggers)

Conditions are used in `trigger`, `potential`, and `allow` blocks to check game state.

### Country-Scope Conditions

| Condition | Syntax | Description |
|-----------|--------|-------------|
| `tag` | `tag = TAG` | Checks country tag |
| `exists` | `exists = TAG` | Checks if country exists |
| `civilized` | `civilized = yes/no` | Checks civilized status |
| `is_greater_power` | `is_greater_power = yes` | Checks Great Power status |
| `prestige` | `prestige = n` | Minimum prestige check |
| `war` | `war = yes/no` | Checks if at war |
| `war_with` | `war_with = TAG` | Checks specific war |
| `alliance_with` | `alliance_with = TAG` | Checks alliance status |
| `truce_with` | `truce_with = TAG` | Checks truce status |
| `in_sphere` | `in_sphere = TAG` | Checks sphere membership |
| `vassal_of` | `vassal_of = TAG` | Checks vassal relationship |
| `is_vassal` | `is_vassal = yes` | Checks if country is a vassal |
| `government` | `government = type` | Checks government type |
| `ruling_party_ideology` | `ruling_party_ideology = ideology` | Checks ruling ideology |
| `has_country_flag` | `has_country_flag = flag_name` | Checks country flag |
| `has_global_flag` | `has_global_flag = flag_name` | Checks global flag |
| `primary_culture` | `primary_culture = culture` | Checks primary culture |
| `accepted_culture` | `accepted_culture = culture` | Checks accepted cultures |
| `literacy` | `literacy = n` | Minimum literacy (0.0-1.0) |
| `money` | `money = n` | Minimum treasury |
| `total_num_of_ports` | `total_num_of_ports = n` | Checks port count |
| `military_score` | `military_score = n` | Minimum military score |
| `industrial_score` | `industrial_score = n` | Minimum industrial score |
| `is_mobilised` | `is_mobilised = yes` | Checks mobilization status |
| `war_exhaustion` | `war_exhaustion = n` | Minimum war exhaustion |
| `badboy` | `badboy = n` | Minimum infamy |
| `num_of_cities` | `num_of_cities = n` | Minimum city count |

### Province-Scope Conditions

| Condition | Syntax | Description |
|-----------|--------|-------------|
| `province_id` | `province_id = n` | Checks specific province |
| `owned_by` | `owned_by = TAG` | Checks province owner |
| `controlled_by` | `controlled_by = TAG` | Checks province controller |
| `is_core` | `is_core = TAG` | Checks if core of nation |
| `is_capital` | `is_capital = yes` | Checks if capital province |
| `is_coastal` | `is_coastal = yes` | Checks coastal status |
| `port` | `port = yes` | Checks for port |
| `continent` | `continent = name` | Checks continent |
| `terrain` | `terrain = type` | Checks terrain type |
| `has_building` | `has_building = type` | Checks building presence |
| `life_rating` | `life_rating = n` | Minimum life rating |
| `trade_goods` | `trade_goods = good` | Checks produced good |
| `has_pop_type` | `has_pop_type = type` | Checks for pop type |
| `has_province_modifier` | `has_province_modifier = mod` | Checks province modifier |
| `has_factories` | `has_factories = yes` | Checks factory presence |

### Pop-Scope Conditions

| Condition | Syntax | Description |
|-----------|--------|-------------|
| `type` | `type = pop_type` | Checks pop type (e.g., craftsmen) |
| `strata` | `strata = poor/middle/rich` | Checks economic strata |
| `culture` | `culture = culture_name` | Checks pop culture |
| `religion` | `religion = religion_name` | Checks pop religion |
| `literacy` | `literacy = n` | Minimum pop literacy |
| `consciousness` | `consciousness = n` | Minimum consciousness |
| `militancy` | `militancy = n` | Minimum militancy |
| `life_needs` | `life_needs = n` | Life needs satisfaction |
| `everyday_needs` | `everyday_needs = n` | Everyday needs satisfaction |
| `luxury_needs` | `luxury_needs = n` | Luxury needs satisfaction |

---

## Effects Reference (Commands)

Effects are used in `option` blocks (events) and `effect` blocks (decisions) to modify game state.

### Country Effects

| Effect | Syntax | Description |
|--------|--------|-------------|
| `prestige` | `prestige = n` | Changes prestige |
| `badboy` | `badboy = n` | Changes infamy |
| `money` | `money = n` | Changes treasury |
| `research_points` | `research_points = n` | Grants research points |
| `war_exhaustion` | `war_exhaustion = n` | Changes war exhaustion |
| `plurality` | `plurality = n` | Changes plurality |
| `civilized` | `civilized = yes` | Sets civilized status |
| `capital` | `capital = province_id` | Moves capital |
| `primary_culture` | `primary_culture = culture` | Changes primary culture |
| `add_accepted_culture` | `add_accepted_culture = culture` | Adds accepted culture |
| `remove_accepted_culture` | `remove_accepted_culture = culture` | Removes accepted culture |
| `government` | `government = type` | Changes government |
| `ruling_party_ideology` | `ruling_party_ideology = ideology` | Changes ruling ideology |
| `election` | `election = yes` | Triggers election |
| `political_reform` | `political_reform = reform` | Enacts political reform |
| `social_reform` | `social_reform = reform` | Enacts social reform |
| `set_country_flag` | `set_country_flag = flag` | Sets country flag |
| `clr_country_flag` | `clr_country_flag = flag` | Clears country flag |
| `set_global_flag` | `set_global_flag = flag` | Sets global flag |
| `country_event` | `country_event = { id = n days = n }` | Fires country event |
| `change_tag` | `change_tag = TAG` | Changes country tag |
| `inherit` | `inherit = TAG` | Inherits/annexes country |
| `annex_to` | `annex_to = TAG` | Annexes to another country |
| `release_vassal` | `release_vassal = TAG` | Releases vassal |
| `create_alliance` | `create_alliance = TAG` | Creates alliance |
| `leave_alliance` | `leave_alliance = TAG` | Leaves alliance |
| `relation` | `relation = { who = TAG value = n }` | Changes relations |
| `war` | `war = TAG` | Declares war |
| `add_casus_belli` | `add_casus_belli = { target = TAG type = cb }` | Adds CB |
| `remove_casus_belli` | `remove_casus_belli = { target = TAG type = cb }` | Removes CB |

### Province Effects

| Effect | Syntax | Description |
|--------|--------|-------------|
| `add_core` | `add_core = TAG` | Adds national core |
| `remove_core` | `remove_core = TAG` | Removes national core |
| `secede_province` | `secede_province = TAG` | Transfers to country |
| `trade_goods` | `trade_goods = good` | Changes RGO good |
| `life_rating` | `life_rating = n` | Changes life rating |
| `infrastructure` | `infrastructure = n` | Changes railroad level |
| `fort` | `fort = n` | Changes fort level |
| `naval_base` | `naval_base = n` | Changes naval base level |
| `set_province_flag` | `set_province_flag = flag` | Sets province flag |
| `clr_province_flag` | `clr_province_flag = flag` | Clears province flag |
| `add_province_modifier` | `add_province_modifier = { name = mod duration = n }` | Adds modifier |
| `province_event` | `province_event = { id = n }` | Fires province event |
| `assimilate` | `assimilate = yes` | Assimilates pops to primary culture |

### Pop Effects

| Effect | Syntax | Description |
|--------|--------|-------------|
| `consciousness` | `consciousness = n` | Changes consciousness |
| `militancy` | `militancy = n` | Changes militancy |
| `literacy` | `literacy = n` | Changes literacy |
| `money` | `money = n` | Changes pop savings |
| `reduce_pop` | `reduce_pop = n` | Reduces pop size (0.95 = 5% reduction) |
| `move_pop` | `move_pop = province_id` | Moves pop |
| `pop_type` | `pop_type = type` | Changes pop type |

### Logic Effects

| Effect | Syntax | Description |
|--------|--------|-------------|
| `random` | `random = { chance = n effect }` | Random chance (0-100) |
| `random_list` | `random_list = { 50 = { } 50 = { } }` | Weighted random |
| `set_variable` | `set_variable = { which = var value = n }` | Sets variable |
| `change_variable` | `change_variable = { which = var value = n }` | Changes variable |
| `check_variable` | `check_variable = { which = var value = n }` | Checks variable |

---

## Scopes Reference

Scopes change the context for conditions and effects.

### Country Scope (Triggers)

| Scope | Syntax | Description |
|-------|--------|-------------|
| `any_core` | `any_core = { triggers }` | Any core province |
| `all_core` | `all_core = { triggers }` | All core provinces |
| `any_owned_province` | `any_owned_province = { }` | Any owned province |
| `any_neighbor_country` | `any_neighbor_country = { }` | Any neighbor |
| `any_greater_power` | `any_greater_power = { }` | Any Great Power |
| `any_pop` | `any_pop = { }` | Any pop in country |
| `any_state` | `any_state = { }` | Any owned state |
| `any_sphere_member` | `any_sphere_member = { }` | Any sphere member |
| `capital_scope` | `capital_scope = { }` | Capital province |
| `overlord` | `overlord = { }` | Overlord country |
| `sphere_owner` | `sphere_owner = { }` | Sphere leader |
| `cultural_union` | `cultural_union = { }` | Cultural union tag |
| `[TAG]` | `GER = { triggers }` | Specific country |
| `[region]` | `REGION_NAME = { }` | Specific region |

### Province Scope (Triggers)

| Scope | Syntax | Description |
|-------|--------|-------------|
| `owner` | `owner = { }` | Province owner |
| `controller` | `controller = { }` | Province controller |
| `any_neighbor_province` | `any_neighbor_province = { }` | Any neighbor |
| `any_pop` | `any_pop = { }` | Any pop in province |
| `state_scope` | `state_scope = { }` | State containing province |
| `sea_zone` | `sea_zone = { }` | Adjacent sea zones |

### Country Scope (Effects)

| Scope | Syntax | Description |
|-------|--------|-------------|
| `any_owned` | `any_owned = { effects }` | All owned provinces |
| `any_country` | `any_country = { limit = { } effects }` | Countries matching limit |
| `random_country` | `random_country = { limit = { } effects }` | Random country |
| `random_owned` | `random_owned = { limit = { } effects }` | Random province |
| `random_pop` | `random_pop = { limit = { } effects }` | Random pop |
| `[province_id]` | `123 = { effects }` | Specific province |

---

## Modifier Effects Reference

Modifiers can be applied via events, decisions, or static definitions.

### Country Modifiers

| Modifier | Description | Example |
|----------|-------------|---------|
| `prestige` | Monthly prestige change | `prestige = 0.5` |
| `badboy` | Monthly infamy change | `badboy = -0.1` |
| `research_points` | Daily RP change | `research_points = 0.5` |
| `research_points_modifier` | RP generation % | `research_points_modifier = 0.1` |
| `tax_efficiency` | Tax collection % | `tax_efficiency = 0.1` |
| `administrative_efficiency_modifier` | Admin efficiency % | `administrative_efficiency_modifier = 0.1` |
| `education_efficiency_modifier` | Education % | `education_efficiency_modifier = 0.1` |
| `global_immigrant_attract` | Immigration attractiveness | `global_immigrant_attract = 1` |
| `global_assimilation_rate` | Assimilation rate % | `global_assimilation_rate = 0.25` |
| `global_population_growth` | Pop growth % | `global_population_growth = 0.001` |
| `global_pop_militancy_modifier` | Monthly militancy | `global_pop_militancy_modifier = -0.01` |
| `global_pop_consciousness_modifier` | Monthly consciousness | `global_pop_consciousness_modifier = 0.01` |
| `factory_output` | Factory output % | `factory_output = 0.1` |
| `factory_throughput` | Factory throughput % | `factory_throughput = 0.1` |
| `factory_cost` | Factory build cost % | `factory_cost = -0.1` |
| `rgo_output` | RGO output % | `rgo_output = 0.1` |
| `rgo_throughput` | RGO throughput % | `rgo_throughput = 0.1` |
| `land_organisation` | Land org % | `land_organisation = 0.1` |
| `naval_organisation` | Naval org % | `naval_organisation = 0.1` |
| `land_unit_start_experience` | Starting experience | `land_unit_start_experience = 10` |
| `mobilisation_size` | Mobilization % | `mobilisation_size = 0.02` |
| `war_exhaustion` | Monthly war exhaustion | `war_exhaustion = -0.01` |
| `cb_generation_speed_modifier` | CB justification speed | `cb_generation_speed_modifier = 0.25` |
| `diplomatic_points_modifier` | Diplo points % | `diplomatic_points_modifier = 0.1` |
| `influence_modifier` | Influence generation % | `influence_modifier = 0.1` |
| `supply_consumption` | Unit supply cost | `supply_consumption = -0.1` |
| `leadership_modifier` | Leadership generation | `leadership_modifier = 0.1` |

### Province Modifiers

| Modifier | Description | Example |
|----------|-------------|---------|
| `life_rating` | Life rating % | `life_rating = 0.1` |
| `population_growth` | Local pop growth % | `population_growth = 0.001` |
| `assimilation_rate` | Local assimilation % | `assimilation_rate = 0.25` |
| `immigrant_attract` | Local immigration | `immigrant_attract = 1` |
| `immigrant_push` | Emigration modifier | `immigrant_push = 0.1` |
| `local_rgo_output` | Local RGO output % | `local_rgo_output = 0.1` |
| `local_rgo_throughput` | Local RGO throughput % | `local_rgo_throughput = 0.1` |
| `local_factory_output` | Local factory output % | `local_factory_output = 0.1` |
| `local_factory_throughput` | Local factory throughput % | `local_factory_throughput = 0.1` |
| `pop_militancy_modifier` | Local militancy | `pop_militancy_modifier = 0.01` |
| `pop_consciousness_modifier` | Local consciousness | `pop_consciousness_modifier = 0.01` |
| `local_repair` | Ship repair rate | `local_repair = 0.1` |
| `min_build_railroad` | Min railroad level | `min_build_railroad = 1` |
| `farm_rgo_eff` | Farm RGO efficiency | `farm_rgo_eff = 0.1` |
| `mine_rgo_eff` | Mine RGO efficiency | `mine_rgo_eff = 0.1` |
| `farm_rgo_size` | Farm RGO size | `farm_rgo_size = 0.1` |
| `mine_rgo_size` | Mine RGO size | `mine_rgo_size = 0.1` |

---

## Event Modding

Events are defined in `.txt` files in the `/events` folder.

### Event Structure

```pdx
country_event = {
    id = 12345                      # Unique numerical ID
    title = "EVTNAME12345"          # Localization key for title
    desc = "EVTDESC12345"           # Localization key for description
    picture = "picture_name"        # GFX file name (no extension)
    
    # Firing control (use ONE of these methods)
    is_triggered_only = yes         # Only fires via effect (recommended)
    # OR
    trigger = { conditions }        # Conditions to check
    mean_time_to_happen = {         # Random firing interval
        months = 12
        modifier = {
            factor = 0.5            # <1 speeds up, >1 slows down
            condition = yes
        }
    }
    
    # Optional flags
    fire_only_once = yes            # Can only happen once per game
    major = yes                     # Shows as newspaper headline
    allow_multiple_instances = yes  # Can trigger multiple times simultaneously
    
    option = {
        name = "EVTOPTA12345"       # Localization key
        # Effects here
        ai_chance = {
            factor = 50
            modifier = { factor = 2 condition = yes }
        }
    }
}
```

### Event Types

| Type | Description |
|------|-------------|
| `country_event` | Standard country-scoped event |
| `province_event` | Province-scoped event |
| News event | Add `major = yes` to `country_event` |

### MTTH Modifiers

```pdx
mean_time_to_happen = {
    months = 24
    modifier = { factor = 0.5 prestige = 100 }      # Halves time if prestige >= 100
    modifier = { factor = 2.0 NOT = { literacy = 0.5 } }  # Doubles if literacy < 50%
}
```

---

## Decision Modding

Decisions are defined in `.txt` files in the `/decisions` folder.

### Decision Structure

```pdx
political_decisions = {
    decision_name = {
        picture = "picture_name"      # Optional GFX
        
        potential = {                  # Visibility conditions
            tag = TAG
            NOT = { has_country_flag = did_this }
        }
        
        allow = {                      # Clickability conditions
            war = no
            prestige = 50
        }
        
        effect = {                     # What happens on click
            prestige = 10
            set_country_flag = did_this
        }
        
        ai_will_do = {                 # AI decision-making
            factor = 1                 # Base probability
            modifier = { factor = 0 NOT = { money = 10000 } }
        }
    }
}
```

### Decision News

```pdx
decision_name = {
    news = yes
    news_desc_long = "NEWS_LONG_KEY"
    news_desc_medium = "NEWS_MEDIUM_KEY"
    news_desc_short = "NEWS_SHORT_KEY"
    # ... rest of decision
}
```

---

## Country Modding

### Country Definition (`common/countries/TAG.txt`)

```pdx
color = { 123 45 67 }               # RGB country color
graphical_culture = EuropeanGC      # Unit/leader sprites

party = {
    name = "TAG_conservative"
    ideology = conservative
    economic_policy = interventionism
    trade_policy = protectionism
    religious_policy = moralism
    citizenship_policy = residency
    war_policy = pro_military
    start_date = 1830.1.1
    end_date = 1946.1.1
}
```

### Country History (`history/countries/TAG - Name.txt`)

```pdx
capital = 123                       # Province ID
primary_culture = culture_name
culture = accepted_culture          # Optional
religion = religion_name
government = government_type
nationalvalue = nv_order            # nv_order, nv_liberty, nv_equality
literacy = 0.1                      # 10%
plurality = 0
prestige = 0

# Political reforms
slavery = yes_slavery
upper_house_composition = appointed
voting_rights = landed_voting
public_meetings = no_meeting
press_rights = censored_press
trade_unions = no_trade_unions
political_parties = none

# Social reforms (initially none, unlocked via events)

# Starting technologies
post_napoleonic_thought = 1
flintlock_rifles = 1

# Government setup
ruling_party = TAG_conservative
upper_house = {
    fascist = 0
    liberal = 10
    conservative = 70
    reactionary = 20
    anarcho_liberal = 0
    socialist = 0
    communist = 0
}

# Diplomatic setup
set_country_flag = initial_flag

# Date-specific changes
1861.1.1 = {
    government = democracy
}
```

### Required Country Files

1. `common/countries.txt` - Add tag link: `TAG = "countries/NewCountry.txt"`
2. `common/countries/NewCountry.txt` - Color, parties, graphical culture
3. `history/countries/TAG - Name.txt` - Starting state
4. `history/provinces/XXX - Name.txt` - Assign provinces: `owner = TAG`
5. `gfx/flags/TAG.tga` - Default flag (32x22 TGA)
6. `gfx/flags/TAG_communist.tga`, `TAG_fascist.tga`, `TAG_republic.tga`, `TAG_monarchy.tga`
7. `localisation/*.csv` - Name entries: `TAG;Country Name;...;x`

---

## Culture Modding

### Culture Structure (`common/cultures.txt`)

```pdx
culture_group_name = {
    leader = european               # Portrait set
    unit = EuropeanGC              # Unit sprites
    union = GER                    # Cultural union tag (optional)
    
    culture_name = {
        color = { 90 60 60 }       # RGB for pie charts
        first_names = { "Hans" "Fritz" "Wilhelm" }
        last_names = { "Müller" "Schmidt" "Schneider" }
        radicalism = 10            # Optional: base radicalism
    }
}
```

### Graphical Presets

**Leader Portraits:** `european`, `southamerican`, `russian`, `arab`, `asian`, `indian`, `african`, `polar_bear`

**Unit Models:** `EuropeanGC`, `BritishGC`, `ItalianGC`, `SpanishGC`, `FrenchGC`, `AustriaHungaryGC`, `RussianGC`, `MiddleEasternGC`, `IndianGC`, `AsianGC`, `ChineseGC`, `AfricanGC`, `ZuluGC`

---

## Government Modding

### Government Structure (`common/governments.txt`)

```pdx
government_type = {
    # Allowed party ideologies for appointment
    liberal = yes
    conservative = yes
    reactionary = yes
    socialist = no
    communist = no
    fascist = no
    anarcho_liberal = no
    
    election = yes                  # Has elections
    duration = 48                   # Months between elections
    appoint_ruling_party = yes      # Player can change party manually
    
    flagType = monarchy             # monarchy, republic, fascist, communist
}
```

### Flag Types

| flagType | Description |
|----------|-------------|
| `monarchy` | Uses `TAG.tga` or `TAG_monarchy.tga` |
| `republic` | Uses `TAG_republic.tga` |
| `fascist` | Uses `TAG_fascist.tga` |
| `communist` | Uses `TAG_communist.tga` |

---

## Map Modding

### Key Map Files

| File | Format | Description |
|------|--------|-------------|
| `map/provinces.bmp` | 24-bit RGB | Province shapes (unique colors) |
| `map/terrain.bmp` | 8-bit indexed | Terrain types |
| `map/rivers.bmp` | 8-bit indexed | River network |
| `map/definition.csv` | CSV | Province ID to color mapping |
| `map/default.map` | Text | Map configuration |
| `map/region.txt` | Text | State/region definitions |
| `map/adjacencies.csv` | CSV | Straits and connections |
| `map/terrain.txt` | Text | Terrain type definitions |
| `map/positions.txt` | Text | Unit/city positions |

### Province Definition (`map/definition.csv`)

```csv
province;red;green;blue;name;x
1;50;100;150;London;x
2;60;110;160;Yorkshire;x
```

### Region Definition (`map/region.txt`)

```pdx
STATE_NAME = { 1 2 3 4 5 }         # List of province IDs
```

### Province History (`history/provinces/ID - Name.txt`)

```pdx
owner = TAG
controller = TAG
add_core = TAG
trade_goods = iron
life_rating = 35
fort = 1
railroad = 0

party_loyalty = {
    ideology = liberal
    loyalty_value = 0.1
}
```

---

## Casus Belli Modding

### CB Structure (`common/cb_types.txt`)

```pdx
cb_name = {
    war_name = WAR_NAME_KEY
    sprite_index = 1
    
    is_civil_war = no
    months = 12                     # Duration before CB expires
    
    badboy_factor = 1.0             # Infamy multiplier
    prestige_factor = 1.0           # Prestige multiplier
    peace_cost_factor = 1.0         # War score cost multiplier
    
    can_use = { conditions }        # Who can use this CB
    is_valid = { conditions }       # When CB remains valid
    on_add = { effects }            # Effects when CB is added
    on_po_accepted = { effects }    # Effects when peace accepted
    
    # Peace treaty options
    po_annex = yes
    po_demand_state = yes
    po_add_to_sphere = yes
    po_disarmament = yes
    po_reparations = yes
    po_transfer_provinces = yes
    po_make_puppet = yes
    po_release_puppet = yes
    po_status_quo = yes
    po_colony = yes
    po_remove_cores = yes
    
    # Special flags
    crisis = yes                    # Available in crisis
    great_war_obligatory = yes      # Auto-added in Great War
}
```

---

## Localisation

### File Format

- **Location:** `/localisation/*.csv`
- **Encoding:** Windows-1252 (ANSI) - NOT UTF-8
- **Delimiter:** Semicolon (`;`)
- **Line ending:** Must end with `;x`

### Column Structure

```csv
KEY;ENGLISH;FRENCH;GERMAN;;SPANISH;;;;;;;;;x
```

| Column | Language |
|--------|----------|
| 1 | Key |
| 2 | English |
| 3 | French |
| 4 | German |
| 5 | (Reserved) |
| 6 | Spanish |
| 7-14 | (Reserved) |
| 15 | End marker (x) |

### Common Keys

```csv
EVTNAME12345;Event Title;;;;;;;;;;;;;x
EVTDESC12345;Event description text;;;;;;;;;;;;;x
EVTOPTA12345;Option A text;;;;;;;;;;;;;x
decision_name_title;Decision Title;;;;;;;;;;;;;x
decision_name_desc;Decision tooltip description;;;;;;;;;;;;;x
TAG;Country Name;;;;;;;;;;;;;x
TAG_ADJ;Country Adjective;;;;;;;;;;;;;x
```

### Color Codes

Use `§` followed by a letter:
- `§R` Red, `§G` Green, `§B` Blue
- `§Y` Yellow, `§W` White, `§O` Orange
- `§!` Reset to default

### Dynamic Variables

- `$COUNTRY$` - Country name
- `$FROMCOUNTRY$` - FROM country name
- `$DATE$` - Current date
- `$VALUE$` - Numeric value

---

## Building Modding

### Building Definition (`common/buildings.txt`)

```pdx
fort = {
    type = fort
    goods_cost = {
        cement = 100
        lumber = 50
        steel = 50
    }
    time = 1080                     # Days to build
    visibility = yes
    onmap = yes
    max_level = 6
    province = yes                  # Province-level building
    fort_level = 1                  # Modifier effect
}

factory_name = {
    type = factory
    on_completion = factory
    completion_size = 0.2
    max_level = 99
    goods_cost = {
        machine_parts = 20
        cement = 200
    }
    time = 365
    production_type = factory_name  # Links to production_types.txt
    pop_build_factory = yes         # Capitalists can build
}
```

---

## .mod File Structure

### Required Parameters

```pdx
name = "Mod Display Name"
path = "mod/mod_folder"
user_dir = "mod_folder"
```

### Optional Parameters

```pdx
dependencies = { "Base Mod Name" }  # Load order dependency
replace_path = "events"             # Overwrite base game folder
replace_path = "decisions"
```

### Complete Example

```pdx
name = "Concert of Europe"
path = "mod/CoE_RoI_R"
user_dir = "CoE_RoI_R"
replace_path = "history/provinces"
```

---

## Mod-Specific Patterns (CoE_RoI_R)

### Political System

**Ideologies (4 Groups, 9 Types):**
- **fascist_group**: `fascist`, `Executive` (custom)
- **conservative_group**: `reactionary`, `pro_slavery` (custom), `conservative`
- **socialist_group**: `socialist`, `communist`
- **liberal_group**: `liberal`, `anarcho_liberal`

**Government Types:** 33 types with up to 3 flag variants each

### Game Master System (BHU)

Bhutan (`BHU`) is used as a "Game Master" country for background maintenance:
- **Ghost Unit Cleanup**: Removes orphaned military units
- **State Population Display**: Updates province modifiers based on population tiers
- **Random Migration**: Triggers population migration events
- **Vassal Cleanup**: Handles orphaned vassal relationships

### Maintenance Events (00_CoE_RoI.txt)

| ID Range | Purpose |
|----------|---------|
| 99991-99999 | Core maintenance events |
| 6016818-6016821 | Ghost unit cleanup chain |

Uses province 2127-2128 as "ghost country" staging area.

### State Population Modifiers

`s_pop_not_100k`, `s_pop_100k`, `s_pop_250k`, `s_pop_500k`, `s_pop_1000k`, `s_pop_2500k`

### Naming Conventions

**Event Files:**
- `00_*` - Core setup, maintenance events
- `0_*` - System mechanics
- `+prefix_*` - Specific mechanics
- `*Flavor.txt` - Country-specific flavor

**Decision Files:**
- `00_*`, `01_*` - Setup and system
- Country codes: `ENG.txt`, `RUS.txt`
- Geographic: `Balkans.txt`, `SouthAmerica.txt`
- Mechanics: `NationalUnification.txt`, `Canals.txt`

**Country History:**
- Format: `TAG - Country Name.txt`

---

## Development Workflow

### Adding Content

1. **Events**: Add to `events/`, use unique ID range
2. **Decisions**: Add to thematic file in `decisions/`
3. **Countries**: Create files in `common/countries/` + `history/countries/`
4. **Localization**: Add keys to CSVs in `localisation/`

### Common Patterns

- **Commented-out code**: `#` for disabled features
- **Flag variants**: `democracy`, `democracy2`, `democracy3`
- **Maintenance events**: Use BHU as trigger anchor

### Validation

- Use `ValidatorSettings.txt` with `NoCheckKey` for relaxed checking
- Use Victoria 2 validator tool before testing
- Test complex event chains in-game

### Debugging

- Console command: `event [id] [tag]` to trigger events
- Startup crash = syntax error (missing `}`)
- Gameplay crash = context error (invalid reference)

---

## Graphics and Asset Tools

### ImageMagick - Image Conversion Tool

ImageMagick is a powerful CLI tool for converting and manipulating graphics assets. It is essential for working with Victoria 2's graphics formats.

**Installation:**
```bash
winget install --id ImageMagick.ImageMagick
```

**Common Conversions for Victoria 2:**

```bash
# PNG to TGA (flag format)
magick input.png output.tga

# PNG to DDS (texture format)
magick input.png output.dds

# Batch conversion (all PNG to TGA in directory)
magick mogrify -format tga *.png

# Resize flag to standard dimensions (32x22)
magick input.png -resize 32x22! output.tga

# Convert with specific compression
magick input.png -define tga:compression=1 output.tga
```

**Flag Requirements:**
- Standard flag dimensions: **32x22 pixels**
- Format: TGA (Targa)
- Required variants: `TAG.tga`, `TAG_communist.tga`, `TAG_fascist.tga`, `TAG_monarchy.tga`, `TAG_republic.tga`
- Location: `gfx/flags/`

**Installation Path (Windows):**
```
C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe
```

*Note: After installation, restart thy terminal to enable the `magick` command in PATH.*

---

## Quick Reference

| Setting | Value |
|---------|-------|
| Base Tax Efficiency | 50% |
| Pop Size Per Regiment | 5,000 |
| Years of Nationalism | 10 |
| Base Truce Duration | 60 months |
| Campaign Duration | 6 months |
| Tech Year Span | 50 years |
| Colonial Liferating | 30 |
| Factory Input Limit | 4 goods max |

---

## File Statistics

| Category | Count | Notable Size |
|----------|-------|--------------|
| Events | 170 files | `political_leaders.txt` (261KB) |
| Decisions | 74 files | `gtfo.txt` (108KB) |
| Countries | 583 defs | History for 522 |
| Provinces | 3,259 | Via `map/definition.csv` |
| Localization | 56 CSVs | ~4MB total |
| Graphics | 12,396 | Flags, units, UI |

---

## External Resources

- **[Paradox Wiki Modding Portal](https://vic2.paradoxwikis.com/Modding)** - Official modding documentation
- **[List of Conditions](https://vic2.paradoxwikis.com/List_of_conditions)** - Complete trigger reference
- **[List of Effects](https://vic2.paradoxwikis.com/List_of_effects)** - Complete command reference
- **[List of Scopes](https://vic2.paradoxwikis.com/List_of_scopes)** - Scope targeting reference
- **[Modifier Effects](https://vic2.paradoxwikis.com/Modifier_effects)** - All modifier documentation
