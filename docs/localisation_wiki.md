# Localisation - Victoria 2 Wiki

> **Note:** This article is considered accurate for the current version of the game. It is currently undergoing a major reconstruction.

Localisation is an important part of Victoria 2's modding system. It connects the variable 'keys' used in the game's internal code and external scripting system with readable text, and also allows translation into multiple languages. Thus it controls the naming of everything from countries to parties to tech in Victoria 2.

## The Localisation Files

In the Victoria 2 folder, you can find the localisation folder. In here is a long list of documents in csv format. The csv format can be edited in excel or similar software.

The files can be quite chaotic to navigate. They are named after the patch in which the name was first defined. Each 'type' of name is generally stored together (names of countries together, event texts together etc.), but not always. All the possible names for e.g. California is stored across 3 different files. You will have to use the search function a lot.

> **Note:** Many concepts have multiple related text-blurbs e.g. both a proper name and an adjective or the text for multiple buttons. They are usually stored next to each other or at least in the same section.

## Basics

A localisation looks like this (only English, French and German are officially supported and only the default English localisation is generally correct):

```
key;English;French;German;Polish;Spanish;Italian;Swedish;Czech;Hungarian;Dutch;Portugese;Russian;Finnish;
```

For example, this is the localisation for the single player button in the main menu:

```
FE_SINGLE_PLAYER;Single Player;Solo;Einzelspieler;Gra pojedyncza;Un jugador;Giocatore singolo;Egyjátékos mód;Hra pro jednoho hráèe;;;;;;x;;;;
```

Some commands in Paradox Script create localisation keys.

### Events

Events are localised through these three script commands: `title`, `desc`, `name` (the latter in an option code block).

The commands assign keys like this: `command = "key"`. The quotation marks are optional, but it is standard practice to include them.

```paradox
country_event = {
    id = 100
    title = "EVTNAME100"
    desc = "EVTDESC100"

    option = {
        name = "EVTOPTA100"
    }

    option = {
        name = "EVTOPTB100"
    }
}
```

The assigned keys can be any arbitrary string, but should follow the above standard: `"EVTNAME[ID]"` for the title, `"EVTDESC[ID]"` for the description, and `"EVTOPT[A-F][ID]"` for options.

The subtitles of election events are localised by adding `_sub` to the event's title key.

### Decisions

Decisions are automatically localised using the name of the decision as defined through the script with the extensions `_title` and `_desc`.

### Countries

Countries have both a proper name under `TAG` and its adjective under `TAG_ADJ`.

Countries can change names depending on government type. Example:

```
tag_absolute_monarchy;name(English);name(French);name(German);;name(Spanish);;;;;;;;;x;
CAL_absolute_monarchy;Kingdom of California;Royaim de California;Kingdom of California;;Reino de California;;;;;;;;;x;
```

## Dynamic Localisation

Normally, events and decisions can only have one localisation - or in other words, one specific event or decision has only one specific localisation key associated with it which is associated with only one piece of text. However, the `change_region_name` effect can be abused to write decisions, events, or tooltips with localisation that changes depending on in-game circumstances. For more information, see Dynamic localisation.

## Common Modding Issues

There are a few common issues when modding relating to localisation.

### Encoding Issues

One issue is that accented and other special characters are not displaying correctly. E.g. your custom country called Númenor may show up as something weird like NÃºmenor. This is due to the encoding being incorrect when the file was saved.

Encoding determines how the characters are saved, and must match what the game expects. The correct encoding to use is **ANSI (or Windows-1252)**.

- In **Notepad++**, you can switch encoding through the Encoding menu.
- In **VSCode**, you can switch encoding by opening the Command Palette then running Change File Encoding.
- Always ensure you open and save the files in the correct encoding.

### Empty Lines

Another issue is that localisation is shifted around and nonsensical. E.g. your custom country called Númenor is showing up as something completely unexpected and illogical like France or Declare War or some other text.

This is due to there being an empty line in one of your localisation csv files. Simply delete the empty line and all will be well.

### Overriding Vanilla Keys

To modify a single key in a localisation file, instead of copying the whole file along with other keys you are not interested in, you can create a .csv file with any name so long as the name is **lexicographically ahead** of the vanilla file where the key is located.

For example, if you want to replace the text of `small_arms_production_desc` which is defined in `beta1.csv` in vanilla, your file name must be less than `beta1.csv`. `beta0.csv` will work and so will `0anyname.csv`; but not `beta1_my_replacement.csv`.

## Localisation Colours

Below is a list of colours recognised by Victoria 2's localisation system. You can use colours to highlight important information in event or decision text or any part of the interface localisation.

For example, to get "This text is red" to appear as red, you would write in the localisation: `§RThis text is red.`

| Key | Colour |
|:---|:---|
| `§W` | White |
| `§Y` | Yellow |
| `§R` | Red |
| `§b` | Black |
| `§G` | Green |
| `§B` | Blue |
| `§g` | Light grey |
| `§!` | Return to default colour |

## Localisation Keys

Below is a list of all localisation keys found in Victoria 2's files, along with their scopes and meanings.

### Special Characters

| Key | Scope | Description | Example Value |
|:---|:---|:---|:---|
| `\n` | Events/Decisions | Skips Line | |
| `@TAG` | Events/Decisions | Adds the country flag of that tag | `@ENG` |

### Dynamic Keys Reference

| Key | Scope | Description | Example Value |
|:---|:---|:---|:---|
| `$ACTION$` | | Action variable | |
| `$ACTIVE$` | | Active status | |
| `$ACTOR$` | | Acting party | |
| `$ADJ$` | | Adjective form | |
| `$AGAINST$` | | Opposition target | |
| `$AGRESSOR$` | | Aggressor country | |
| `$ALLOWED$` | | Allowed status | |
| `$AMOUNT$` | | Numerical amount | |
| `$ANYPROVINCE$` | Fake News | Any province in the country | Liverpool |
| `$ARMY_NAME$` | | Army name | |
| `$ARMY$` | | Army reference | |
| `$ASTATE$` | | State A | |
| `$ATTACKER$` | | Attacking party | |
| `$ATTUNIT$` | | Attacking unit | |
| `$AVG$` | | Average value | |
| `$BADBOY$` | | Infamy value | |
| `$BASE$` | | Base value | |
| `$BASE_PERCENTAGE$` | | Base percentage | |
| `$BONUS$` | | Bonus amount | |
| `$BUILDING$` | | Building name | |
| `$CAPITAL$` | Events/Decisions | The capital city of the country | London |
| `$CASH$` | | Cash amount | |
| `$CASUS$` | | Casus belli | |
| `$CB_TARGET_NAME$` | | CB target name | |
| `$CB_TARGET_NAME_ADJ$` | | CB target adjective | |
| `$CHANCE$` | | Probability | |
| `$CHANGE$` | | Change amount | |
| `$COMMANDER$` | | Commander name | |
| `$CONSTRUCTION$` | | Construction details | |
| `$CONTINENTNAME$` | | Continent name | |
| `$COST$` | | Cost amount | |
| `$COUNT$` | | Count value | |
| `$COUNTRIES$` | | Countries list | |
| `$COUNTRY$` | | Country name | |
| `$COUNTRY_ADJ$` | | Country adjective | |
| `$COUNTRY1$` | | First country | |
| `$COUNTRY2$` | | Second country | |
| `$COUNTRYADJ$` | | Country adjective | |
| `$COUNTRYCULTURE$` | | Country culture | |
| `$COUNTRYNAME$` | | Country name | |
| `$CREATOR$` | | Creator | |
| `$CREDITS$` | | Credits | |
| `$CRISISAREA$` | | Crisis area | |
| `$CRISISATTACKER$` | | Crisis attacker | |
| `$CRISISDEFENDER$` | | Crisis defender | |
| `$CRISISTAKER$` | | Crisis taker | |
| `$CRISISTAKER_ADJ$` | | Crisis taker adjective | |
| `$CRISISTARGET$` | | Crisis target | |
| `$CRISISTARGET_ADJ$` | | Crisis target adjective | |
| `$CULTURE$` | | Culture name | |
| `$CULTUREGROUP$` | | Culture group | |
| `$CULTURE_GROUP_UNION$` | | Culture group union | |
| `$CURRENT$` | | Current value | |
| `$DATE$` | | Date | |
| `$DATE_LONG_0$` | | Long date format 0 | |
| `$DATE_LONG_1$` | | Long date format 1 | |
| `$DATE_SHORT_0$` | | Short date format | |
| `$DAY$` | | Day | |
| `$DAYS$` | | Days count | |
| `$DEFENDER$` | | Defending party | |
| `$DEFUNIT$` | | Defending unit | |
| `$DESC$` | | Description | |
| `$DEST$` | | Destination | |
| `$DETAILS$` | | Details | |
| `$DIRECTION$` | | Direction | |
| `$EFFECT$` | | Effect description | |
| `$EFFECTS$` | | Effects list | |
| `$EMILIST$` | | Emigration list | |
| `$EMPLOYEE_MAX$` | | Maximum employees | |
| `$EMPLOYEES$` | | Employees count | |
| `$ENEMY$` | | Enemy | |
| `$ESCORTS$` | | Escort ships | |
| `$EVENT$` | | Event reference | |
| `$EVENTDESC$` | | Event description | |
| `$EXPLANATION$` | | Explanation text | |
| `$FACTION$` | | Faction name | |
| `$FACTORY$` | | Factory name | |
| `$FIRST$` | | First item | |
| `$FOCUS$` | | Focus type | |
| `$FOLDER$` | | Folder name | |
| `$FRACTION$` | | Fraction value | |
| `$FRIEND$` | | Friend country | |
| `$FROM$` | | Source | |
| `$FROMCOUNTRY$` | | From country | |
| `$FROMCOUNTRY_ADJ$` | | From country adjective | |
| `$FROMPROVINCE$` | | From province | |
| `$FROMRULER$` | | From ruler | |
| `$FUNDS$` | | Funds amount | |
| `$GOAL$` | | Goal | |
| `$GOOD$` | | Good type | |
| `$GOODS$` | | Goods list | |
| `$GOVERNMENT$` | | Government type | |
| `$GOVT$` | | Government abbreviation | |
| `$GP$` | | Great Power | |
| `$GP_ADJ$` | | Great Power adjective | |
| `$GROUP$` | | Group name | |
| `$HIGH_TAX$` | | High tax rate | |
| `$HOME$` | | Home location | |
| `$HULL$` | | Ship hull | |
| `$IDEOLOGY$` | | Ideology | |
| `$IMMLIST$` | | Immigration list | |
| `$IMPACT$` | | Impact value | |
| `$INCOME$` | | Income amount | |
| `$INDEP$` | | Independence | |
| `$INFAMY$` | | Infamy value | |
| `$INPUT$` | | Input | |
| `$INVENTION$` | | Invention name | |
| `$INVESTED$` | | Investment amount | |
| `$INVESTED_IN_US_MESSAGE$` | | Investment message | |
| `$ISSUE$` | | Issue type | |
| `$LAW$` | | Law name | |
| `$LEADER$` | | Leader name | |
| `$LEVEL$` | | Level | |
| `$LEVELS$` | | Levels count | |
| `$LIMIT$` | | Limit value | |
| `$LIST$` | | List | |
| `$LITERACY$` | | Literacy rate | |
| `$LOCAL$` | | Local reference | |
| `$LOCATION$` | | Location name | |
| `$LORD$` | | Lord/Overlord | |
| `$LOSE$` | | Loss amount | |
| `$LOW_TAX$` | | Low tax rate | |
| `$MAX$` | | Maximum value | |
| `$MAXLOAN$` | | Maximum loan | |
| `$MEN$` | | Men count | |
| `$MESSENGER$` | | Messenger | |
| `$MILITANCY$` | | Militancy value | |
| `$MIN$` | | Minimum value | |
| `$MONARCHTITLE$` | | Monarch title | |
| `$MONEY$` | | Money amount | |
| `$MONTH$` | | Month | |
| `$MONTHS$` | | Months count | |
| `$MOVEMENT$` | | Movement name | |
| `$NAME$` | | Name | |
| `$NATION$` | | Nation name | |
| `$NATIONALVALUE$` | UI | The National value of the country | Order |
| `$NATIVES$` | | Natives | |
| `$NAVY_NAME$` | | Navy name | |
| `$NAVY$` | | Navy reference | |
| `$NEED$` | | Need | |
| `$NEEDED$` | | Needed amount | |
| `$NEGATIVE$` | | Negative value | |
| `$NEW$` | | New item | |
| `$NEWCOUNTRY$` | | New country | |
| `$NF$` | | National Focus | |
| `$NOW$` | | Current time | |
| `$NUM$` | | Number | |
| `$NUMBER$` | | Number | |
| `$NUMFACTORIES$` | | Factory count | |
| `$NUMSPECIALFACTORIES$` | | Special factory count | |
| `$ODDS$` | | Odds | |
| `$OLD$` | | Old item | |
| `$OLDCOUNTRY$` | | Old country | |
| `$OPERATOR$` | | Operator | |
| `$OPINION$` | | Opinion value | |
| `$OPPOSING_ARMY$` | | Opposing army | |
| `$OPPOSING_NAVY$` | | Opposing navy | |
| `$OPRESSOR$` | | Oppressor | |
| `$OPTIMAL$` | | Optimal value | |
| `$OPTION$` | | Option | |
| `$ORDER$` | | Order | |
| `$ORGANISATION$` | | Organisation value | |
| `$OTHER$` | | Other | |
| `$OTHERRESULT$` | | Other result | |
| `$OUR_LEAD$` | | Our leader | |
| `$OUR_NUM$` | | Our numbers | |
| `$OUR_RES$` | | Our result | |
| `$OURCAPITAL$` | Fake News | The capital of the country | London |
| `$OURCOUNTRY$` | Fake News | The name of the country | United Kingdom |
| `$OURCOUNTRY_ADJ$` | Fake News | The country adjective | British |
| `$OUTPUT$` | | Output | |
| `$OVERLORD$` | | Overlord country | |
| `$PARAM$` | | Parameter | |
| `$PARTY$` | | Party name | |
| `$PASSIVE$` | | Passive status | |
| `$PAY$` | | Pay amount | |
| `$PENALTY$` | | Penalty | |
| `$PERCENT$` | | Percent value | |
| `$PERCENTAGE$` | | Percentage | |
| `$PLAYER$` | | Player | |
| `$POLICY$` | | Policy | |
| `$POP$` | | Pop reference | |
| `$POPTYPE$` | | Pop type | |
| `$POPULARITY$` | | Popularity | |
| `$POSITION$` | | Position | |
| `$POSITIVE$` | | Positive value | |
| `$POWER$` | | Power | |
| `$PRESTIGE$` | | Prestige value | |
| `$PRODUCED$` | | Produced amount | |
| `$PRODUCER$` | | Producer | |
| `$PROGRESS$` | | Progress | |
| `$PROVINCE$` | | Province name | |
| `$PROVINCECULTURE$` | | Province culture | |
| `$PROVINCENAME$` | | Province name | |
| `$PROVINCERELIGION$` | | Province religion | |
| `$PROVINCES$` | | Provinces list | |
| `$RANK$` | | Rank | |
| `$RATE$` | | Rate | |
| `$RECIPIENT$` | | Recipient | |
| `$REFORM$` | | Reform name | |
| `$REGION$` | | Region name | |
| `$RELATION$` | | Relation value | |
| `$REQLEVEL$` | | Required level | |
| `$REQUIRED$` | | Required | |
| `$RESOURCE$` | | Resource | |
| `$RESULT$` | | Result | |
| `$RSTATE$` | | State R | |
| `$RULE$` | | Rule | |
| `$RUNS$` | | Runs | |
| `$SEA$` | | Sea zone | |
| `$SECOND$` | | Second item | |
| `$SECOND_COUNTRY$` | | Second country | |
| `$SELF$` | | Self reference | |
| `$SELL$` | | Sell price | |
| `$SETTING$` | | Setting | |
| `$SHIPS$` | | Ships count | |
| `$SIZE$` | | Size | |
| `$SKILL$` | | Skill level | |
| `$SOURCE$` | | Source | |
| `$SPEED$` | | Speed | |
| `$SPHEREMASTER$` | | Sphere master | |
| `$STATE$` | | State name | |
| `$STATENAME$` | | State name | |
| `$STRATA$` | | Strata | |
| `$STRENGTH$` | | Strength | |
| `$STRING_0_0$` | | String variable | |
| `$STRING_0_1$` | | String variable | |
| `$STRING_0_2$` | | String variable | |
| `$STRING_0_3$` | | String variable | |
| `$STRING_0_4$` | | String variable | |
| `$STRING_9_0$` | | String variable | |
| `$STRINGS_LIST_4$` | | String list | |
| `$TABLE$` | | Table | |
| `$TAG$` | | Country tag | |
| `$TAG_0_0$` | | Tag variable | |
| `$TAG_0_0_ADJ$` | | Tag adjective | |
| `$TAG_0_0_UPPER$` | | Tag uppercase | |
| `$TAG_0_1$` | | Tag variable | |
| `$TAG_0_1_ADJ$` | | Tag adjective | |
| `$TAG_0_1_UPPER$` | | Tag uppercase | |
| `$TAG_0_2$` | | Tag variable | |
| `$TAG_0_2_ADJ$` | | Tag adjective | |
| `$TAG_0_3$` | | Tag variable | |
| `$TAG_0_3_ADJ$` | | Tag adjective | |
| `$TAG_1_0$` | | Tag variable | |
| `$TAG_2_0$` | | Tag variable | |
| `$TAG_2_0_UPPER$` | | Tag uppercase | |
| `$TAG_3_0$` | | Tag variable | |
| `$TAG_3_0_UPPER$` | | Tag uppercase | |
| `$TAG0_0$` | | Tag variable | |
| `$TARGET$` | | Target | |
| `$TARGET_COUNTRY$` | | Target country | |
| `$TARGETLIST$` | | Target list | |
| `$TECH$` | | Technology | |
| `$TEMPERATURE$` | | Temperature | |
| `$TERMS$` | | Terms | |
| `$TERRAIN$` | | Terrain type | |
| `$TERRAINMOD$` | | Terrain modifier | |
| `$TEXT$` | | Text | |
| `$THEIR_LEAD$` | | Their leader | |
| `$THEIR_NUM$` | | Their numbers | |
| `$THEIR_RES$` | | Their result | |
| `$THEIRLOST$` | | Their losses | |
| `$THEIRNUM$` | | Their number | |
| `$THEIRSHIP$` | | Their ship | |
| `$THEM$` | | Them reference | |
| `$THIRD$` | | Third item | |
| `$THREAT$` | | Threat level | |
| `$TIME$` | | Time | |
| `$TITLE$` | | Title | |
| `$TO$` | | Destination | |
| `$TOTAL$` | | Total | |
| `$TOTALEMI$` | | Total emigration | |
| `$TOTALIMM$` | | Total immigration | |
| `$TRUTH$` | | Truth value | |
| `$TYPE$` | | Type | |
| `$UNEMPLOYED$` | | Unemployed count | |
| `$UNION$` | | Union name | |
| `$UNION_ADJ$` | | Union adjective | |
| `$UNIT$` | | Unit | |
| `$UNITS$` | | Units count | |
| `$UNTIL$` | | Until date | |
| `$USLOSS$` | | US loss | |
| `$USNUM$` | | US number | |
| `$VALUE$` | | Value | |
| `$VALUE_INT_0_0$` | | Integer value | |
| `$VALUE_INT_0_1$` | | Integer value | |
| `$VALUE_INT_0_2$` | | Integer value | |
| `$VALUE_INT_0_3$` | | Integer value | |
| `$VALUE_INT_0_4$` | | Integer value | |
| `$VALUE_INT1$` | | Integer value | |
| `$VERB$` | | Verb | |
| `$VERSUS$` | | Versus | |
| `$WAR$` | | War name | |
| `$WARGOAL$` | | War goal | |
| `$WE$` | | We reference | |
| `$WHAT$` | | What | |
| `$WHERE$` | | Where | |
| `$WHICH$` | | Which | |
| `$WHO$` | | Who | |
| `$WINNER$` | | Winner | |
| `$X$` | | X coordinate | |
| `$Y$` | | Y coordinate | |
| `$YEAR$` | | Year | |
| `$YEARS$` | | Years count | |
| `$YESTERDAY$` | | Yesterday | |

### Cabinet Position Keys

| Key | Description |
|:---|:---|
| `$chief_of_army$` | Chief of Army |
| `$chief_of_navy$` | Chief of Navy |
| `$chief_of_staff$` | Chief of Staff |
| `$head_of_government$` | Head of Government |

### Miscellaneous Keys

| Key | Description |
|:---|:---|
| `$control$` | Control reference |
| `$owner$` | Owner reference |
| `$playername$` | Player name |

## References

1. [Paradox Plaza Forum: Localization text key list](https://forum.paradoxplaza.com/forum/threads/localization-text-key-list.946323/)

---

*Source: [Victoria 2 Wiki - Localisation](https://vic2.paradoxwikis.com/Localisation)*
