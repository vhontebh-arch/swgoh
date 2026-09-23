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


# Stat IDs used by SWGOH exports.
#
# The export contains two groups:
# - percentage/stat IDs used by the mod data
# - flat stat IDs used by the mod data
#
# Keep the IDs already confirmed in Vhonte's export and add
# the missing IDs that were previously printed as "Stat XX".
STAT_NAMES = {
    # Percentage stats
    1: "Health %",
    5: "Offense %",
    16: "Critical Damage %",
    17: "Defense %",
    18: "Potency %",
    28: "Protection %",
    41: "Critical Avoidance %",
    42: "Tenacity %",
    54: "Critical Chance %",
    
    # Flat stats
    48: "Health",
    49: "Protection",
    53: "Defense",
    55: "Offense",
    56: "Speed",
}


# Stats whose values are stored by the export as scaled integers.
# The CSV will contain:
#   primaryValue      -> human-readable value
#   primaryValueRaw   -> original export value
#
# Percentage values in the Comlink export are stored at 1,000,000
# units per 1%. For example:
#
#   23500000 -> 23.5%
#   8500000  -> 8.5%
#
PERCENT_STAT_IDS = {
    1,
    5,
    16,
    17,
    18,
    28,
    41,
    42,
    54,
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
    """
    Recursively searches JSON for lists associated with:
      - unequippedMod
      - equippedStatMod
      - equippedMod
    """

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
    """
    Current SWGOH mod definition IDs use three digits:

        ABC

        A = mod set
        B = dots / rarity
        C = shape / slot

    Example:
        756 = Potency / 5 dots / Cross
    """

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

    if isinstance(value, dict):
        return value

    return {}


def get_stat_id(stat):
    container = get_stat_container(stat)

    return as_int(
        container.get(
            "unitStatId"
        ),
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

    for key in (
        "statValueDecimal",
        "value",
        "statValue",
    ):
        if key in container:
            return container[key]

    return ""


def format_value(value, stat_id=None):
    if value in ("", None):
        return ""

    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)

    # Percentage values in the export use micro-percent units.
    if stat_id in PERCENT_STAT_IDS:
        number /= 1_000_000

        if number.is_integer():
            return f"{int(number)}%"

        return f"{number:.6f}".rstrip("0").rstrip(".") + "%"

    if number.is_integer():
        return str(int(number))

    return f"{number:.6f}".rstrip("0").rstrip(".")


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

        f"{prefix}Rolls": get_roll_count(
            stat
        ),

        f"{prefix}RawRolls": "|".join(
            str(value)
            for value in get_roll_values(stat)
        ),
    }


def get_assigned_to(mod):
    """
    Try all known character-assignment fields.

    Different SWGOH export layouts use different fields.
    """

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

    definition_id = mod.get(
        "definitionId"
    )

    if definition_id is None:
        definition_id = mod.get(
            "definition"
        )

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

    if not isinstance(
        secondaries,
        list,
    ):
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
            source_type
            != "unequippedMod"
        ),

        "source": source_type,

        "assignedTo": get_assigned_to(
            mod
        ),
    }

    row.update(
        stat_columns(
            "primary",
            primary,
        )
    )

    for index in range(1, 5):

        if index <= len(secondaries):
            stat = secondaries[
                index - 1
            ]
        else:
            stat = {}

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

    locations = find_mod_lists(
        data
    )

    for location, mods, source_type in locations:

        print(
            f"Znaleziono {len(mods)} modów: "
            f"{location}"
        )

        for mod in mods:

            normalized = normalize_mod(
                mod,
                source_type,
            )

            if normalized:
                result.append(
                    normalized
                )

    return result


def merge_mods(rows):
    """
    Same mod ID can appear in multiple parts
    of the export.

    Prefer equipped data over inventory data.
    """

    merged = {}

    for row in rows:

        mod_id = row["id"]

        existing = merged.get(
            mod_id
        )

        if existing is None:
            merged[mod_id] = row
            continue

        if (
            row["equipped"]
            and not existing["equipped"]
        ):
            merged[mod_id] = row

    return list(
        merged.values()
    )


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
        files.append(
            env_file
        )

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

        rows = extract_mods_from_file(
            path
        )

        print(
            f"Znormalizowano: {len(rows)}"
        )

        all_rows.extend(
            rows
        )

    rows = merge_mods(
        all_rows
    )

    if not rows:
        raise RuntimeError(
            "Nie znaleziono żadnych modów."
        )

    write_csv(
        rows
    )

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
