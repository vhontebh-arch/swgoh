import csv
import json
import sys


C3PO_FILE = "c3po.json"
OUTPUT_FILE = "mods.csv"


# SWGOH stat IDs.
# Zachowujemy również oryginalny unitStatId w CSV, więc brakujące
# mapowanie nie powoduje utraty danych.
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


# Definition IDs modów.
# Te wartości pochodzą z game data i pozwalają rozpoznać zarówno
# set, jak i kształt bez zgadywania na podstawie kolejności.
MOD_DEFINITIONS = {
    # Speed
    151: ("Speed", "Square"),
    152: ("Speed", "Diamond"),
    153: ("Speed", "Triangle"),
    154: ("Speed", "Circle"),
    155: ("Speed", "Cross"),
    156: ("Speed", "Arrow"),

    # Health
    261: ("Health", "Square"),
    262: ("Health", "Diamond"),
    263: ("Health", "Triangle"),
    264: ("Health", "Circle"),
    265: ("Health", "Cross"),
    266: ("Health", "Arrow"),

    # Defense
    271: ("Defense", "Square"),
    272: ("Defense", "Diamond"),
    273: ("Defense", "Triangle"),
    274: ("Defense", "Circle"),
    275: ("Defense", "Cross"),
    276: ("Defense", "Arrow"),

    # Critical Damage
    281: ("Critical Damage", "Square"),
    282: ("Critical Damage", "Diamond"),
    283: ("Critical Damage", "Triangle"),
    284: ("Critical Damage", "Circle"),
    285: ("Critical Damage", "Cross"),
    286: ("Critical Damage", "Arrow"),

    # Critical Chance
    291: ("Critical Chance", "Square"),
    292: ("Critical Chance", "Diamond"),
    293: ("Critical Chance", "Triangle"),
    294: ("Critical Chance", "Circle"),
    295: ("Critical Chance", "Cross"),
    296: ("Critical Chance", "Arrow"),

    # Tenacity
    301: ("Tenacity", "Square"),
    302: ("Tenacity", "Diamond"),
    303: ("Tenacity", "Triangle"),
    304: ("Tenacity", "Circle"),
    305: ("Tenacity", "Cross"),
    306: ("Tenacity", "Arrow"),

    # Offense
    311: ("Offense", "Square"),
    312: ("Offense", "Diamond"),
    313: ("Offense", "Triangle"),
    314: ("Offense", "Circle"),
    315: ("Offense", "Cross"),
    316: ("Offense", "Arrow"),

    # Potency
    321: ("Potency", "Square"),
    322: ("Potency", "Diamond"),
    323: ("Potency", "Triangle"),
    324: ("Potency", "Circle"),
    325: ("Potency", "Cross"),
    326: ("Potency", "Arrow"),
}


def as_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f, strict=False)


def get_stat_name(stat):
    if not isinstance(stat, dict):
        return ""

    stat_data = stat.get("stat", {})

    if not isinstance(stat_data, dict):
        return ""

    stat_id = as_int(
        stat_data.get("unitStatId"),
        -1
    )

    return STAT_NAMES.get(
        stat_id,
        f"Stat {stat_id}"
    )


def get_stat_value(stat):
    if not isinstance(stat, dict):
        return ""

    stat_data = stat.get("stat", {})

    if not isinstance(stat_data, dict):
        return ""

    value = stat_data.get(
        "statValueDecimal",
        ""
    )

    return value


def get_stat_display_value(stat):
    if not isinstance(stat, dict):
        return ""

    stat_data = stat.get("stat", {})

    if not isinstance(stat_data, dict):
        return ""

    stat_id = as_int(
        stat_data.get("unitStatId"),
        -1
    )

    raw = stat_data.get(
        "statValueDecimal",
        ""
    )

    try:
        value = float(raw)

        # Flat stats
        if stat_id in {
            48,
            49,
            53,
            55,
            56,
        }:
            if stat_id == 56:
                return str(int(round(value)))

            return str(int(round(value)))

        # Percentage stats are stored in a scaled representation.
        if stat_id in {
            1,
            5,
            17,
            18,
            28,
            41,
            42,
        }:
            return f"{value / 100000:.2f}%"

    except (TypeError, ValueError):
        pass

    return str(raw)


def get_rolls(stat):
    if not isinstance(stat, dict):
        return []

    rolls = stat.get(
        "roll",
        []
    )

    if not isinstance(rolls, list):
        return []

    return rolls


def get_unscaled_rolls(stat):
    if not isinstance(stat, dict):
        return []

    rolls = stat.get(
        "unscaledRollValue",
        []
    )

    if not isinstance(rolls, list):
        return []

    return rolls


def get_stat_roll_count(stat):
    if not isinstance(stat, dict):
        return 0

    return as_int(
        stat.get("statRolls"),
        0
    )


def extract_mods(c3po):
    """
    Extracts the complete mod inventory.

    The current c3po.json structure stores player inventory below
    the top-level "inventory" object.

    We deliberately search recursively for objects that have the
    characteristic mod fields instead of assuming a single exact
    inventory key. This makes the exporter resistant to harmless
    Comlink structure changes.
    """

    found = []

    seen_ids = set()

    def walk(value):

        if isinstance(value, dict):

            # A mod object has these fields in the current export.
            if (
                "id" in value
                and "definitionId" in value
                and "primaryStat" in value
                and "secondaryStat" in value
                and "tier" in value
                and "level" in value
            ):

                mod_id = value.get("id")

                if mod_id and mod_id not in seen_ids:

                    seen_ids.add(mod_id)
                    found.append(value)

            for child in value.values():
                walk(child)

        elif isinstance(value, list):

            for child in value:
                walk(child)

    walk(c3po)

    return found


def definition_info(definition_id):
    return MOD_DEFINITIONS.get(
        as_int(definition_id),
        ("", "")
    )


def build_row(mod):

    definition_id = as_int(
        mod.get("definitionId"),
        0
    )

    mod_set, slot = definition_info(
        definition_id
    )

    primary = mod.get(
        "primaryStat",
        {}
    )

    secondaries = mod.get(
        "secondaryStat",
        []
    )

    if not isinstance(secondaries, list):
        secondaries = []

    row = {
        "id": mod.get("id", ""),
        "definitionId": definition_id,
        "set": mod_set,
        "slot": slot,
        "tier": as_int(
            mod.get("tier"),
            0
        ),
        "level": as_int(
            mod.get("level"),
            0
        ),
        "locked": str(
            bool(mod.get("locked", False))
        ),
        "rerolledCount": as_int(
            mod.get("rerolledCount"),
            0
        ),

        "primaryStat": get_stat_name(
            primary
        ),

        "primaryValue": get_stat_display_value(
            primary
        ),

        "primaryValueRaw": get_stat_value(
            primary
        ),

        "secondary1Stat": "",
        "secondary1Value": "",
        "secondary1Rolls": "",
        "secondary1RawRolls": "",

        "secondary2Stat": "",
        "secondary2Value": "",
        "secondary2Rolls": "",
        "secondary2RawRolls": "",

        "secondary3Stat": "",
        "secondary3Value": "",
        "secondary3Rolls": "",
        "secondary3RawRolls": "",

        "secondary4Stat": "",
        "secondary4Value": "",
        "secondary4Rolls": "",
        "secondary4RawRolls": "",
    }

    for index, secondary in enumerate(
        secondaries[:4],
        start=1
    ):

        prefix = f"secondary{index}"

        row[f"{prefix}Stat"] = (
            get_stat_name(
                secondary
            )
        )

        row[f"{prefix}Value"] = (
            get_stat_display_value(
                secondary
            )
        )

        row[f"{prefix}Rolls"] = (
            get_stat_roll_count(
                secondary
            )
        )

        row[f"{prefix}RawRolls"] = (
            "|".join(
                str(x)
                for x in get_unscaled_rolls(
                    secondary
                )
            )
        )

    return row


def write_csv(rows):

    fieldnames = [
        "id",
        "definitionId",
        "set",
        "slot",
        "tier",
        "level",
        "locked",
        "rerolledCount",

        "primaryStat",
        "primaryValue",
        "primaryValueRaw",

        "secondary1Stat",
        "secondary1Value",
        "secondary1Rolls",
        "secondary1RawRolls",

        "secondary2Stat",
        "secondary2Value",
        "secondary2Rolls",
        "secondary2RawRolls",

        "secondary3Stat",
        "secondary3Value",
        "secondary3Rolls",
        "secondary3RawRolls",

        "secondary4Stat",
        "secondary4Value",
        "secondary4Rolls",
        "secondary4RawRolls",
    ]

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8-sig",
        newline=""
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(
            rows
        )


def main():

    print(
        f"Ładowanie {C3PO_FILE}..."
    )

    c3po = load_json(
        C3PO_FILE
    )

    print(
        "Wyszukiwanie modów..."
    )

    mods = extract_mods(
        c3po
    )

    print(
        f"Znaleziono modów: {len(mods)}"
    )

    rows = [
        build_row(mod)
        for mod in mods
    ]

    rows.sort(
        key=lambda row: (
            row["slot"],
            row["set"],
            -row["tier"],
            -row["level"],
            row["id"],
        )
    )

    write_csv(
        rows
    )

    print(
        f"Wygenerowano {OUTPUT_FILE}"
    )

    # Prosta kontrola jakości.
    unknown_definitions = sorted(
        {
            row["definitionId"]
            for row in rows
            if not row["set"]
            or not row["slot"]
        }
    )

    if unknown_definitions:

        print("")
        print(
            "UWAGA: nierozpoznane definitionId:"
        )

        for definition_id in unknown_definitions:
            print(
                f"  {definition_id}"
            )

        print(
            "CSV nadal zawiera te mody, "
            "ale trzeba uzupełnić mapowanie."
        )

    print("")
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
