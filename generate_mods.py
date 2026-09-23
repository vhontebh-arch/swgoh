import csv
import json
import os
import sys

DEFAULT_FILES = [
    "swgoh_972824625.json",
    "c3po.json",
]

OUTPUT_FILE = "mods.csv"

SET_NAMES = {
    1: "Health",
    2: "Offense",
    3: "Defense",
    4: "Speed",
    5: "Critical Chance",
    6: "Critical Damage",
    7: "Potency",
    8: "Tenacity",
}

SLOT_NAMES = {
    1: "Square",
    2: "Arrow",
    3: "Diamond",
    4: "Triangle",
    5: "Circle",
    6: "Cross",
}

# Aktualne mapowanie unitStatId używane przez eksport raw.
#
# Potwierdzone na podstawie swgoh-stat-calc:
# 1  = Health
# 5  = Speed
# 16 = Critical Damage %
# 17 = Potency %
# 18 = Tenacity %
# 28 = Protection
# 41 = Offense
# 42 = Defense
# 48 = Offense %
# 49 = Defense %
# 53 = Critical Chance %
# 54 = Critical Avoidance %
# 55 = Health %
# 56 = Protection %
# 57 = Speed %
STAT_NAMES = {
    1: "Health",
    5: "Speed",
    16: "Critical Damage %",
    17: "Potency %",
    18: "Tenacity %",
    28: "Protection",
    41: "Offense",
    42: "Defense",
    48: "Offense %",
    49: "Defense %",
    53: "Critical Chance %",
    54: "Critical Avoidance %",
    55: "Health %",
    56: "Protection %",
    57: "Speed %",
}

# Statystyki płaskie w statValueDecimal są zapisane
# w skali 1/10000 względem wartości wyświetlanej.
FLAT_STAT_IDS = {
    1,   # Health
    5,   # Speed
    28,  # Protection
    41,  # Offense
    42,  # Defense
}

# Statystyki procentowe w statValueDecimal są zapisane
# w skali 1/100 względem wartości wyświetlanej.
PERCENT_STAT_IDS = {
    16,  # Critical Damage %
    17,  # Potency %
    18,  # Tenacity %
    48,  # Offense %
    49,  # Defense %
    53,  # Critical Chance %
    54,  # Critical Avoidance %
    55,  # Health %
    56,  # Protection %
    57,  # Speed %
}


def as_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f, strict=False)


def find_mod_lists(obj, path="root"):
    found = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in {
                "unequippedMod",
                "equippedStatMod",
                "equippedMod",
            }:
                if isinstance(value, list):
                    found.append(
                        (
                            f"{path}.{key}",
                            value,
                            key,
                        )
                    )

            found.extend(
                find_mod_lists(
                    value,
                    f"{path}.{key}",
                )
            )

    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            found.extend(
                find_mod_lists(
                    value,
                    f"{path}[{index}]",
                )
            )

    return found


def decode_definition_id(definition_id):
    value = as_int(
        definition_id,
        0,
    )

    if value < 100 or value > 999:
        return "", 0, ""

    text = str(value).zfill(3)

    set_id = int(text[0])
    dots = int(text[1])
    slot_id = int(text[2])

    return (
        SET_NAMES.get(
            set_id,
            f"Set {set_id}",
        ),
        dots,
        SLOT_NAMES.get(
            slot_id,
            f"Slot {slot_id}",
        ),
    )


def get_stat_container(stat):
    if not isinstance(stat, dict):
        return {}

    value = stat.get(
        "stat",
        stat,
    )

    return (
        value
        if isinstance(value, dict)
        else {}
    )


def get_stat_id(stat):
    container = get_stat_container(stat)

    return as_int(
        container.get("unitStatId"),
        -1,
    )


def get_stat_name(stat):
    stat_id = get_stat_id(stat)

    if stat_id < 0:
        return ""

    return STAT_NAMES.get(
        stat_id,
        f"Stat {stat_id}",
    )


def get_raw_value(stat):
    container = get_stat_container(stat)

    # statValueDecimal jest wartością wygodną do
    # prezentacji po zastosowaniu odpowiedniej skali.
    if "statValueDecimal" in container:
        return container["statValueDecimal"]

    # Fallback dla innych formatów danych.
    if "value" in container:
        return container["value"]

    if "statValue" in container:
        return container["statValue"]

    # Ostateczny fallback: unscaledDecimalValue.
    # Dla raw eksportu powinno być ono dostępne,
    # ale nie używamy go jako podstawowego źródła,
    # ponieważ jest w innej skali.
    if "unscaledDecimalValue" in container:
        return container["unscaledDecimalValue"]

    return ""


def format_number(number):
    if number.is_integer():
        return str(int(number))

    return (
        f"{number:.6f}"
        .rstrip("0")
        .rstrip(".")
    )


def format_value(value, stat_id=None):
    if value in ("", None):
        return ""

    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)

    if stat_id in FLAT_STAT_IDS:
        number /= 10_000
        return format_number(number)

    if stat_id in PERCENT_STAT_IDS:
        number /= 100
        return f"{format_number(number)}%"

    # Nieznane ID pozostawiamy bez skalowania.
    # Dzięki temu nowe statystyki nie zostaną
    # po cichu błędnie przeliczone.
    return format_number(number)


def get_roll_count(stat):
    if not isinstance(stat, dict):
        return 0

    for key in (
        "statRolls",
        "rollCount",
    ):
        if key in stat:
            return as_int(
                stat[key],
                0,
            )

    return 0


def get_roll_values(stat):
    if not isinstance(stat, dict):
        return []

    for key in (
        "unscaledRollValue",
        "roll",
        "rollValues",
    ):
        value = stat.get(key)

        if isinstance(value, list):
            return value

    return []


def stat_columns(prefix, stat):
    stat_id = get_stat_id(stat)
    raw_value = get_raw_value(stat)

    return {
        f"{prefix}Stat": get_stat_name(stat),
        f"{prefix}Value": format_value(
            raw_value,
            stat_id,
        ),
        f"{prefix}ValueRaw": (
            str(raw_value)
            if raw_value != ""
            else ""
        ),
        f"{prefix}Rolls": get_roll_count(stat),
        f"{prefix}RawRolls": "|".join(
            str(value)
            for value in get_roll_values(stat)
        ),
    }


def get_assigned_to(mod):
    for key in (
        "assignedTo",
        "characterId",
        "unitId",
        "ownerId",
        "equippedTo",
    ):
        value = mod.get(key)

        if value:
            return value

    return ""


def normalize_mod(mod, source_type):
    if not isinstance(mod, dict):
        return None

    mod_id = mod.get("id")

    if not mod_id:
        return None

    definition_id = mod.get("definitionId")

    if definition_id is None:
        definition_id = mod.get("definition")

    if definition_id is None:
        return None

    mod_set, dots, slot = decode_definition_id(
        definition_id
    )

    primary = mod.get(
        "primaryStat",
        {},
    )

    secondaries = mod.get(
        "secondaryStat",
        [],
    )

    if not isinstance(secondaries, list):
        secondaries = []

    row = {
        "id": mod_id,
        "definitionId": as_int(
            definition_id,
            0,
        ),
        "set": mod_set,
        "dots": dots,
        "slot": slot,
        "tier": as_int(
            mod.get("tier"),
            0,
        ),
        "level": as_int(
            mod.get("level"),
            0,
        ),
        "locked": bool(
            mod.get(
                "locked",
                False,
            )
        ),
        "rerolledCount": as_int(
            mod.get(
                "rerolledCount",
                0,
            ),
            0,
        ),
        "equipped": (
            source_type != "unequippedMod"
        ),
        "source": source_type,
        "assignedTo": get_assigned_to(mod),
    }

    row.update(
        stat_columns(
            "primary",
            primary,
        )
    )

    for index in range(1, 5):
        stat = (
            secondaries[index - 1]
            if index <= len(secondaries)
            else {}
        )

        row.update(
            stat_columns(
                f"secondary{index}",
                stat,
            )
        )

    return row


def extract_mods_from_file(path):
    data = load_json(path)

    result = []

    locations = find_mod_lists(data)

    for location, mods, source_type in locations:
        print(
            f"Znaleziono {len(mods)} modów: {location}"
        )

        for mod in mods:
            normalized = normalize_mod(
                mod,
                source_type,
            )

            if normalized:
                result.append(normalized)

    return result


def merge_mods(rows):
    merged = {}

    for row in rows:
        mod_id = row["id"]

        existing = merged.get(mod_id)

        if existing is None:
            merged[mod_id] = row
            continue

        # Jeśli ten sam mod występuje jako wyposażony
        # i niewyposażony, zachowujemy wersję wyposażoną.
        if (
            row["equipped"]
            and not existing["equipped"]
        ):
            merged[mod_id] = row

    return list(merged.values())


def write_csv(rows):
    fields = [
        "id",
        "definitionId",
        "set",
        "dots",
        "slot",
        "tier",
        "level",
        "locked",
        "rerolledCount",
        "equipped",
        "source",
        "assignedTo",

        "primaryStat",
        "primaryValue",
        "primaryValueRaw",
        "primaryRolls",
        "primaryRawRolls",
    ]

    for index in range(1, 5):
        fields.extend([
            f"secondary{index}Stat",
            f"secondary{index}Value",
            f"secondary{index}ValueRaw",
            f"secondary{index}Rolls",
            f"secondary{index}RawRolls",
        ])

    rows.sort(
        key=lambda row: (
            row["set"],
            row["dots"],
            row["slot"],
            -row["level"],
            row["id"],
        )
    )

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fields,
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(rows)


def main():
    print("=" * 80)
    print("SWGOH MOD GENERATOR")
    print("=" * 80)
    print()

    files = []

    env_file = os.environ.get(
        "MODS_SOURCE_FILE"
    )

    if env_file:
        files.append(env_file)

    for path in DEFAULT_FILES:
        if (
            path not in files
            and os.path.exists(path)
        ):
            files.append(path)

    if not files:
        raise FileNotFoundError(
            "Nie znaleziono żadnego źródła modów."
        )

    all_rows = []

    for path in files:
        print()
        print(
            f"--- Źródło: {path} ---"
        )

        rows = extract_mods_from_file(path)

        print(
            f"Znormalizowano: {len(rows)}"
        )

        all_rows.extend(rows)

    rows = merge_mods(all_rows)

    if not rows:
        raise RuntimeError(
            "Nie znaleziono żadnych modów."
        )

    write_csv(rows)

    equipped = sum(
        1
        for row in rows
        if row["equipped"]
    )

    unequipped = len(rows) - equipped

    print()
    print("=" * 80)
    print("WYNIK")
    print("=" * 80)
    print(
        f"Łącznie modów: {len(rows)}"
    )
    print(
        f"Założonych:    {equipped}"
    )
    print(
        f"Niezałożonych: {unequipped}"
    )
    print(
        f"CSV:           {OUTPUT_FILE}"
    )
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()

    except FileNotFoundError as exc:
        print(
            f"BŁĄD: {exc}"
        )
        sys.exit(1)

    except json.JSONDecodeError as exc:
        print(
            f"BŁĄD JSON: {exc}"
        )
        sys.exit(1)

    except Exception as exc:
        print(
            f"BŁĄD: {type(exc).__name__}: {exc}"
        )
        sys.exit(1)
