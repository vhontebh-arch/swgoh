import csv
import json
import sys


C3PO_FILE = "c3po.json"
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


STAT_NAMES = {
    1: "Health %",
    5: "Offense %",
    17: "Defense %",
    18: "Potency %",
    28: "Protection %",
    41: "Critical Avoidance %",
    42: "Tenacity %",
    48: "Health",
    49: "Protection",
    53: "Defense",
    55: "Offense",
    56: "Speed",
}


PERCENT_STATS = {
    1,
    5,
    17,
    18,
    28,
    41,
    42,
}


FLAT_STATS = {
    48,
    49,
    53,
    55,
    56,
}


def as_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f, strict=False)


def decode_definition_id(definition_id):
    """
    SWGOH mod definitionId:

        ABC

    A = set
    B = rarity / dots
    C = slot

    Example:
        756 = Potency / 5 dots / Cross
        356 = Defense / 5 dots / Cross
        152 = Speed / 5 dots / Arrow
    """

    definition_id = as_int(definition_id, 0)

    if definition_id < 100 or definition_id > 999:
        return "", 0, ""

    value = str(definition_id).zfill(3)

    set_id = int(value[0])
    dots = int(value[1])
    slot_id = int(value[2])

    return (
        SET_NAMES.get(set_id, f"Set {set_id}"),
        dots,
        SLOT_NAMES.get(slot_id, f"Slot {slot_id}"),
    )


def get_stat_id(stat):
    if not isinstance(stat, dict):
        return -1

    stat_data = stat.get("stat", {})

    if not isinstance(stat_data, dict):
        return -1

    return as_int(
        stat_data.get("unitStatId"),
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


def get_stat_raw_value(stat):
    if not isinstance(stat, dict):
        return ""

    stat_data = stat.get("stat", {})

    if not isinstance(stat_data, dict):
        return ""

    return stat_data.get(
        "statValueDecimal",
        "",
    )


def get_stat_display_value(stat):
    stat_id = get_stat_id(stat)
    raw = get_stat_raw_value(stat)

    if raw == "":
        return ""

    try:
        value = float(raw)
    except (TypeError, ValueError):
        return str(raw)

    if stat_id == 56:
        return str(int(round(value)))

    if stat_id in FLAT_STATS:
        return str(int(round(value)))

    if stat_id in PERCENT_STATS:
        return f"{value / 100000:.2f}%"

    return str(raw)


def get_stat_roll_count(stat):
    if not isinstance(stat, dict):
        return 0

    return as_int(
        stat.get("statRolls"),
        0,
    )


def get_unscaled_rolls(stat):
    if not isinstance(stat, dict):
        return []

    values = stat.get(
        "unscaledRollValue",
        [],
    )

    if not isinstance(values, list):
        return []

    return values


def get_rolls(stat):
    if not isinstance(stat, dict):
        return []

    values = stat.get(
        "roll",
        [],
    )

    if not isinstance(values, list):
        return []

    return values


def extract_mods(c3po):
    """
    c3po.json currently stores unequipped mods at:

        inventory.unequippedMod

    The export therefore represents the mod inventory available
    for swapping/farming analysis.

    Equipped mods are not present in this c3po.json export.
    """

    inventory = c3po.get(
        "inventory",
        {},
    )

    if not isinstance(inventory, dict):
        return []

    mods = inventory.get(
        "unequippedMod",
        [],
    )

    if not isinstance(mods, list):
        return []

    return [
        mod
        for mod in mods
        if isinstance(mod, dict)
        and mod.get("id")
        and mod.get("definitionId") is not None
    ]


def build_stat_columns(prefix, stat):
    return {
        f"{prefix}Stat": get_stat_name(stat),
        f"{prefix}Value": get_stat_display_value(stat),
        f"{prefix}ValueRaw": get_stat_raw_value(stat),
        f"{prefix}Rolls": get_stat_roll_count(stat),
        f"{prefix}RawRolls": "|".join(
            str(x)
            for x in get_unscaled_rolls(stat)
        ),
        f"{prefix}RollWeights": "|".join(
            str(x)
            for x in get_rolls(stat)
        ),
    }


def build_row(mod):
    definition_id = as_int(
        mod.get("definitionId"),
        0,
    )

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
        "id": mod.get("id", ""),
        "definitionId": definition_id,

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
            mod.get("locked", False)
        ),

        "rerolledCount": as_int(
            mod.get("rerolledCount"),
            0,
        ),

        # Wszystkie mody z tego eksportu są niezałożone.
        "equipped": False,
        "assignedTo": "",
    }

    row.update(
        build_stat_columns(
            "primary",
            primary,
        )
    )

    for index in range(1, 5):
        if index <= len(secondaries):
            stat = secondaries[index - 1]
        else:
            stat = {}

        row.update(
            build_stat_columns(
                f"secondary{index}",
                stat,
            )
        )

    return row


def write_csv(rows):
    fieldnames = [
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
        "assignedTo",

        "primaryStat",
        "primaryValue",
        "primaryValueRaw",
        "primaryRolls",
        "primaryRawRolls",
        "primaryRollWeights",
    ]

    for index in range(1, 5):
        fieldnames.extend([
            f"secondary{index}Stat",
            f"secondary{index}Value",
            f"secondary{index}ValueRaw",
            f"secondary{index}Rolls",
            f"secondary{index}RawRolls",
            f"secondary{index}RollWeights",
        ])

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(rows)


def main():
    print(f"Ładowanie {C3PO_FILE}...")

    c3po = load_json(
        C3PO_FILE
    )

    mods = extract_mods(
        c3po
    )

    print(
        f"Znaleziono niezałożonych modów: {len(mods)}"
    )

    rows = [
        build_row(mod)
        for mod in mods
    ]

    rows.sort(
        key=lambda row: (
            row["set"],
            row["dots"],
            row["slot"],
            -row["level"],
            row["id"],
        )
    )

    write_csv(rows)

    print(
        f"Wygenerowano {OUTPUT_FILE}"
    )

    unknown_sets = sorted({
        row["set"]
        for row in rows
        if row["set"].startswith("Set ")
    })

    unknown_slots = sorted({
        row["slot"]
        for row in rows
        if row["slot"].startswith("Slot ")
    })

    if unknown_sets:
        print(
            "UWAGA - nierozpoznane sety:",
            ", ".join(unknown_sets),
        )

    if unknown_slots:
        print(
            "UWAGA - nierozpoznane sloty:",
            ", ".join(unknown_slots),
        )

    print(
        "Gotowe."
    )


if __name__ == "__main__":
    try:
        main()

    except FileNotFoundError as exc:
        print(
            f"BŁĄD: nie znaleziono pliku: {exc.filename}"
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
