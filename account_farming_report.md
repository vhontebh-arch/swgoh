# Vhonte – Account Farming Report

Automatycznie wygenerowany raport na podstawie aktualnego gamedata, rosteru oraz `c3po.json`.

## Cele

- **JARJARBINKS**: G9 → G13, R1 → R5

## Łączne braki

| ID | Przedmiot | Wymagane | Posiadane | Brakuje |
|---|---|---:|---:|---:|
| `GRIND` | GRIND | 1133450 | 0 | **1133450** |
| `172Salvage` | EQUIPMENT_172SALVAGE_NAME | 166 | 34 | **166** |
| `129Salvage` | EQUIPMENT_129SALVAGE_NAME | 142 | 38 | **142** |
| `144Salvage` | EQUIPMENT_144SALVAGE_NAME | 134 | 16 | **134** |
| `152Salvage` | EQUIPMENT_152SALVAGE_NAME | 80 | 0 | **80** |
| `108Salvage` | EQUIPMENT_108SALVAGE_NAME | 78 | 22 | **78** |
| `116PrototypeSalvage` | EQUIPMENT_116PROTOTYPESALVAGE_NAME | 64 | 36 | **64** |
| `168PrototypeSalvage` | EQUIPMENT_168PROTOTYPESALVAGE_NAME | 55 | 45 | **55** |
| `173Salvage` | EQUIPMENT_173SALVAGE_NAME | 48 | 2 | **48** |
| `158PrototypeSalvage` | EQUIPMENT_158PROTOTYPESALVAGE_NAME | 30 | 0 | **30** |
| `168PrototypeSalvage_V2` | EQUIPMENT_168PROTOTYPESALVAGE_NAME_V2 | 25 | 15 | **25** |
| `120PrototypeSalvage` | EQUIPMENT_120PROTOTYPESALVAGE_NAME | 18 | 32 | **18** |
| `RM_002` | RM_DESC | 65 | 49 | **16** |
| `147Salvage` | EQUIPMENT_147SALVAGE_NAME | 13 | 7 | **13** |
| `150Salvage` | EQUIPMENT_150SALVAGE_NAME | 13 | 37 | **13** |
| `159PrototypeSalvage` | EQUIPMENT_159PROTOTYPESALVAGE_NAME | 13 | 17 | **13** |
| `RM_003` | RM_DESC | 15 | 2 | **13** |
| `002` | EQUIPMENT_002_NAME | 11 | 3 | **11** |
| `153Salvage` | EQUIPMENT_153SALVAGE_NAME | 10 | 40 | **10** |
| `145Salvage` | EQUIPMENT_145SALVAGE_NAME | 5 | 45 | **5** |
| `151Salvage` | EQUIPMENT_151SALVAGE_NAME | 5 | 35 | **5** |
| `015Prototype` | EQUIPMENT_015PROTOTYPE_NAME | 2 | 4 | **2** |

## Szczegóły

### JARJARBINKS

Gear: **G9 → G13**
Relic: **R1 → R5**

#### Bezpośredni wymagany gear

- `116` × 1 — NULL
- `125` × 1 — NULL
- `129` × 2 — EQUIPMENT_129_NAME
- `134` × 1 — NULL
- `142` × 1 — NULL
- `144` × 3 — NULL
- `146` × 1 — NULL
- `158` × 1 — EQUIPMENT_158_NAME
- `159` × 1 — EQUIPMENT_159_NAME
- `160` × 1 — EQUIPMENT_160_NAME
- `168` × 2 — EQUIPMENT_168_NAME
- `174` × 2 — EQUIPMENT_174_NAME
- `G12Finisher_JARJARBINKS_C` × 1 — EQUIPMENT_G12Finisher_JARJARBINKS_NAME

#### Materiały relic

- `GRIND` × 250000 — GRIND
- `RM_001` × 75 — RM_DESC
- `RM_002` × 65 — RM_DESC
- `RM_003` × 15 — RM_DESC
- `SCV_001` × 120 — SCV_001_DESCRIPTION
- `SCV_002` × 160 — SCV_002_DESCRIPTION
- `SCV_003` × 90 — SCV_003_DESCRIPTION
- `SCV_004` × 20 — SCV_004_DESCRIPTION

#### Braki

| ID | Przedmiot | Brakuje |
|---|---|---:|
| `GRIND` | GRIND | **1133450** |
| `172Salvage` | EQUIPMENT_172SALVAGE_NAME | **166** |
| `129Salvage` | EQUIPMENT_129SALVAGE_NAME | **142** |
| `144Salvage` | EQUIPMENT_144SALVAGE_NAME | **134** |
| `152Salvage` | EQUIPMENT_152SALVAGE_NAME | **80** |
| `108Salvage` | EQUIPMENT_108SALVAGE_NAME | **78** |
| `116PrototypeSalvage` | EQUIPMENT_116PROTOTYPESALVAGE_NAME | **64** |
| `168PrototypeSalvage` | EQUIPMENT_168PROTOTYPESALVAGE_NAME | **55** |
| `173Salvage` | EQUIPMENT_173SALVAGE_NAME | **48** |
| `158PrototypeSalvage` | EQUIPMENT_158PROTOTYPESALVAGE_NAME | **30** |
| `168PrototypeSalvage_V2` | EQUIPMENT_168PROTOTYPESALVAGE_NAME_V2 | **25** |
| `120PrototypeSalvage` | EQUIPMENT_120PROTOTYPESALVAGE_NAME | **18** |
| `RM_002` | RM_DESC | **16** |
| `147Salvage` | EQUIPMENT_147SALVAGE_NAME | **13** |
| `150Salvage` | EQUIPMENT_150SALVAGE_NAME | **13** |
| `159PrototypeSalvage` | EQUIPMENT_159PROTOTYPESALVAGE_NAME | **13** |
| `RM_003` | RM_DESC | **13** |
| `002` | EQUIPMENT_002_NAME | **11** |
| `153Salvage` | EQUIPMENT_153SALVAGE_NAME | **10** |
| `145Salvage` | EQUIPMENT_145SALVAGE_NAME | **5** |
| `151Salvage` | EQUIPMENT_151SALVAGE_NAME | **5** |
| `015Prototype` | EQUIPMENT_015PROTOTYPE_NAME | **2** |

## Informacje techniczne

- Inventory pochodzi z `c3po.json`.
- Aktualny gear/relic pochodzi z rosteru.
- Wymagany gear pochodzi z `unitTier[].equipmentSet`.
- Receptury gearu są rozwijane rekurencyjnie.
- Materiały reliców pochodzą z `relic_promotion_recipe_01...10`.
- `9999` jest traktowane jako placeholder G13 i nie jest liczone jako gear.
