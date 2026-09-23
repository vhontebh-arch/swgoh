import csv
from pathlib import Path


SHIPS_FILE = Path("ships.csv")
REPORT_FILE = Path("fleet_analysis.md")


SHIP_ID_ALIASES = {
    # Capital ships
    "Executor": "CAPITALEXECUTOR",
    "Malevolence": "CAPITALMALEVOLENCE",
    "Negotiator": "CAPITALNEGOTIATOR",
    "Finalizer": "CAPITALFINALIZER",
    "Raddus": "CAPITALRADDUS",
    "Home One": "CAPITALHOMEONE",
    "Chimaera": "CAPITALCHIMAERA",
    "Endurance": "CAPITALENDURANCE",
    "Profundity": "CAPITALPROFUNDITY",
    "Leviathan": "CAPITALLEVIATHAN",

    # Executor
    "Hound's Tooth": "HOUNDSTOOTH",
    "Razor Crest": "RAZORCREST",
    "TIE Advanced x1": "TIEADVANCED",
    "Imperial TIE Bomber": "TIEBOMBERIMPERIAL",
    "Imperial TIE Fighter": "TIEFIGHTERIMPERIAL",
    "TIE Defender": "TIEDEFENDER",
    "TIE Reaper": "TIEREAPER",
    "Slave I": "SLAVE1",

    # Malevolence
    "Vulture Droid": "VULTUREDROID",
    "Hyena Bomber": "HYENABOMBER",
    "Sun Fac's Geonosian Starfighter": "GEONOSIANSTARFIGHTER3",
    "Geonosian Spy's Starfighter": "GEONOSIANSTARFIGHTER2",
    "Geonosian Soldier's Starfighter": "GEONOSIANSTARFIGHTER1",
    "IG-2000": "IG2000",

    # Negotiator
    "Anakin's Eta-2 Starfighter": "JEDISTARFIGHTERANAKIN",
    "Ahsoka Tano's Jedi Starfighter": "JEDISTARFIGHTERAHSOKATANO",
    "Umbaran Starfighter": "UMBARANSTARFIGHTER",
    "Clone Sergeant's ARC-170": "ARC170CLONESERGEANT",
    "Plo Koon's Jedi Starfighter": "JEDISTARFIGHTERCONSULAR",
    "Raven's Claw": "RAVENSCLAW",

    # Finalizer
    "First Order TIE Fighter": "TIEFIGHTERFIRSTORDER",
    "First Order SF TIE Fighter": "TIEFIGHTERFOSF",
    "TIE Silencer": "TIESILENCER",
    "TIE Echelon": "FIRSTORDERTIEECHELON",
    "TIE/IN Interceptor Prototype": "TIEINTERCEPTOR",

    # Raddus
    "Resistance X-wing": "XWINGRESISTANCE",
    "Poe Dameron's X-wing": "XWINGBLACKONE",
    "MG-100 StarFortress SF-17": "MG100STARFORTRESSSF17",
    "Rebel Y-wing": "YWINGREBEL",
    "Rogue One": "ROGUEONESHIP",

    # Home One
    "Han's Millennium Falcon": "MILLENNIUMFALCON",
    "Biggs Darklighter's X-wing": "XWINGRED2",
    "Wedge Antilles's X-wing": "XWINGRED3",
    "Bistan's U-wing": "UWINGROGUEONE",
    "Ghost": "GHOST",
    "Phantom II": "PHANTOM2",

    # Profundity
    "Outrider": "OUTRIDER",

    # Leviathan
    "Mark VI Interceptor": "MARKVIINTERCEPTOR",
    "TIE Dagger": "TIEDAGGER",
    "B-28 Extinction-class Bomber": "B28EXTINCTIONCLASSBOMBER",
    "Scimitar": "SCIMITAR",
    "Sith Fighter": "SITHFIGHTER",
    "Ebon Hawk": "EBONHAWK",
}


FLEETS = {
    "Executor": {
        "capital": "Executor",
        "core": [
            "Hound's Tooth",
            "Razor Crest",
            "TIE Advanced x1",
            "Imperial TIE Bomber",
            "Imperial TIE Fighter",
        ],
        "reinforcements": [
            "TIE Defender",
            "TIE Reaper",
        ],
    },

    "Malevolence": {
        "capital": "Malevolence",
        "core": [
            "Vulture Droid",
            "Hyena Bomber",
            "Sun Fac's Geonosian Starfighter",
            "Geonosian Spy's Starfighter",
            "Geonosian Soldier's Starfighter",
        ],
        "reinforcements": [
            "Imperial TIE Bomber",
            "IG-2000",
        ],
    },

    "Negotiator": {
        "capital": "Negotiator",
        "core": [
            "Anakin's Eta-2 Starfighter",
            "Ahsoka Tano's Jedi Starfighter",
            "Umbaran Starfighter",
            "Clone Sergeant's ARC-170",
            "Plo Koon's Jedi Starfighter",
        ],
        "reinforcements": [
            "Raven's Claw",
        ],
    },

    "Finalizer": {
        "capital": "Finalizer",
        "core": [
            "First Order TIE Fighter",
            "First Order SF TIE Fighter",
            "TIE Silencer",
            "TIE Echelon",
        ],
        "reinforcements": [
            "TIE/IN Interceptor Prototype",
        ],
    },

    "Raddus": {
        "capital": "Raddus",
        "core": [
            "Resistance X-wing",
            "Poe Dameron's X-wing",
            "MG-100 StarFortress SF-17",
            "Rebel Y-wing",
        ],
        "reinforcements": [
            "Rogue One",
        ],
    },

    "Home One": {
        "capital": "Home One",
        "core": [
            "Han's Millennium Falcon",
            "Biggs Darklighter's X-wing",
            "Wedge Antilles's X-wing",
            "Bistan's U-wing",
            "Rebel Y-wing",
        ],
        "reinforcements": [
            "Ghost",
            "Phantom II",
        ],
    },

    "Chimaera": {
        "capital": "Chimaera",
        "core": [
            "Hound's Tooth",
            "TIE Defender",
            "Imperial TIE Bomber",
            "Imperial TIE Fighter",
            "TIE Advanced x1",
        ],
        "reinforcements": [
            "TIE Reaper",
        ],
    },

    "Endurance": {
        "capital": "Endurance",
        "core": [
            "Raven's Claw",
            "Plo Koon's Jedi Starfighter",
            "Anakin's Eta-2 Starfighter",
            "Ahsoka Tano's Jedi Starfighter",
        ],
        "reinforcements": [
            "Clone Sergeant's ARC-170",
            "Umbaran Starfighter",
        ],
    },

    "Profundity": {
        "capital": "Profundity",
        "core": [
            "Outrider",
            "Bistan's U-wing",
            "Rebel Y-wing",
            "Wedge Antilles's X-wing",
            "Biggs Darklighter's X-wing",
        ],
        "reinforcements": [],
    },

    "Leviathan": {
        "capital": "Leviathan",
        "core": [
            "Mark VI Interceptor",
            "TIE Dagger",
            "Sith Fighter",
            "Ebon Hawk",
        ],
        "reinforcements": [
            "TIE Reaper",
        ],
    },
}


JOURNEY_REQUIREMENTS = {
    "Executor": [
        "Razor Crest",
        "Slave I",
        "IG-2000",
        "Hound's Tooth",
        "TIE Advanced x1",
        "Imperial TIE Bomber",
        "Imperial TIE Fighter",
    ],

    "Profundity": [
        "Outrider",
        "Bistan's U-wing",
        "Wedge Antilles's X-wing",
        "Biggs Darklighter's X-wing",
        "Rebel Y-wing",
    ],

    "Leviathan": [
        "Mark VI Interceptor",
        "TIE Dagger",
        "B-28 Extinction-class Bomber",
        "Scimitar",
        "Sith Fighter",
        "Ebon Hawk",
    ],
}


def ship_id(name):
    return SHIP_ID_ALIASES.get(name, name)


def display_name(name):
    for readable, base_id in SHIP_ID_ALIASES.items():
        if base_id == name:
            return readable

    return name


def load_ships():
    ships = {}

    if not SHIPS_FILE.exists():
        print(f"ERROR: {SHIPS_FILE} not found")
        return ships

    with SHIPS_FILE.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            base_id = (row.get("baseId") or "").strip()
            name = (row.get("name") or "").strip()

            key = base_id or ship_id(name)

            if key:
                ships[key] = row

    return ships


def get_ship(ships, name):
    return ships.get(ship_id(name))


def stars(row):
    if not row:
        return 0

    try:
        return int(row.get("rarity", 0) or 0)
    except (TypeError, ValueError):
        return 0


def level(row):
    if not row:
        return 0

    try:
        return int(row.get("level", 0) or 0)
    except (TypeError, ValueError):
        return 0


def gear(row):
    if not row:
        return 0

    try:
        return int(row.get("gearTier", 0) or 0)
    except (TypeError, ValueError):
        return 0


def star_status(row, required_stars=7):
    if row is None:
        return "BRAK W CSV"

    current = stars(row)

    if current >= required_stars:
        return "OK"

    return f"{current}★ / {required_stars}★"


def format_ship_row(name, row):
    if row is None:
        return f"- **{name}** — BRAK W CSV"

    return (
        f"- **{name}** — "
        f"{stars(row)}★, "
        f"Lv {level(row)}, "
        f"G{gear(row)}"
    )


def get_missing(ships, names, required_stars=7):
    missing = []

    for name in names:
        row = get_ship(ships, name)

        if row is None:
            missing.append(name)
            continue

        if stars(row) < required_stars:
            missing.append(
                f"{name} ({stars(row)}★)"
            )

    return missing


def write_fleet_section(lines, fleet_name, fleet, ships):
    lines.append(f"## {fleet_name}")
    lines.append("")

    capital = fleet["capital"]
    capital_row = get_ship(ships, capital)

    lines.append("### Capital ship")
    lines.append("")
    lines.append(format_ship_row(capital, capital_row))
    lines.append("")

    lines.append("### Core fleet")
    lines.append("")

    for name in fleet["core"]:
        row = get_ship(ships, name)
        lines.append(format_ship_row(name, row))

    lines.append("")

    if fleet["reinforcements"]:
        lines.append("### Reinforcements")
        lines.append("")

        for name in fleet["reinforcements"]:
            row = get_ship(ships, name)
            lines.append(format_ship_row(name, row))

        lines.append("")


def write_journey_section(lines, ships):
    lines.append("## Journey requirements")
    lines.append("")

    for journey, required_ships in JOURNEY_REQUIREMENTS.items():
        lines.append(f"### {journey}")
        lines.append("")

        missing = get_missing(
            ships,
            required_ships,
            required_stars=7,
        )

        if not missing:
            lines.append("- **7★ requirement: COMPLETE**")
        else:
            lines.append("- **7★ requirement: NOT COMPLETE**")

            for item in missing:
                lines.append(f"  - {item}")

        lines.append("")


def write_cross_fleet_usage(lines, ships):
    usage = {}

    for fleet_name, fleet in FLEETS.items():
        all_ships = (
            [fleet["capital"]]
            + fleet["core"]
            + fleet["reinforcements"]
        )

        for name in all_ships:
            sid = ship_id(name)

            if sid not in usage:
                usage[sid] = {
                    "name": name,
                    "fleets": [],
                }

            usage[sid]["fleets"].append(fleet_name)

    shared = [
        item
        for item in usage.values()
        if len(item["fleets"]) > 1
    ]

    lines.append("## Cross-fleet ship usage")
    lines.append("")

    if not shared:
        lines.append("- No ships are shared between defined fleets.")
        lines.append("")
        return

    for item in sorted(shared, key=lambda x: x["name"]):
        row = get_ship(ships, item["name"])

        lines.append(
            f"- **{item['name']}** — "
            f"{', '.join(item['fleets'])} — "
            f"{star_status(row)}"
        )

    lines.append("")


def write_low_star_priority(lines, ships):
    fleet_ship_names = []

    for fleet in FLEETS.values():
        fleet_ship_names.extend(
            [fleet["capital"]]
            + fleet["core"]
            + fleet["reinforcements"]
        )

    seen = set()
    unique_names = []

    for name in fleet_ship_names:
        sid = ship_id(name)

        if sid not in seen:
            seen.add(sid)
            unique_names.append(name)

    low_star = []

    for name in unique_names:
        row = get_ship(ships, name)

        if row is None:
            continue

        current_stars = stars(row)

        if current_stars < 7:
            low_star.append(
                (
                    current_stars,
                    name,
                    level(row),
                    gear(row),
                )
            )

    low_star.sort(key=lambda x: (x[0], x[1]))

    lines.append("## Ships below 7★")
    lines.append("")

    if not low_star:
        lines.append("- No fleet ships below 7★.")
        lines.append("")
        return

    for current_stars, name, ship_level, ship_gear in low_star:
        lines.append(
            f"- **{name}** — "
            f"{current_stars}★, "
            f"Lv {ship_level}, "
            f"G{ship_gear}"
        )

    lines.append("")


def main():
    ships = load_ships()

    if not ships:
        raise SystemExit(
            "ERROR: No ships loaded from ships.csv"
        )

    lines = [
        "# Fleet Analysis",
        "",
        f"Loaded **{len(ships)} ships** from `{SHIPS_FILE.name}`.",
        "",
    ]

    for fleet_name, fleet in FLEETS.items():
        write_fleet_section(
            lines,
            fleet_name,
            fleet,
            ships,
        )

    write_journey_section(lines, ships)
    write_cross_fleet_usage(lines, ships)
    write_low_star_priority(lines, ships)

    REPORT_FILE.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )

    print(f"Generated {REPORT_FILE}")
    print(f"Ships loaded: {len(ships)}")

    print("")
    print("Executor hard-check:")

    executor_required = JOURNEY_REQUIREMENTS["Executor"]
    executor_ok = True

    for name in executor_required:
        row = get_ship(ships, name)

        if row is None:
            print(f"  FAIL: {name} -> BRAK W CSV")
            executor_ok = False
            continue

        current_stars = stars(row)

        if current_stars >= 7:
            print(f"  OK:   {name} -> {current_stars}★")
        else:
            print(f"  FAIL: {name} -> {current_stars}★")
            executor_ok = False

    if executor_ok:
        print("Executor hard-check: PASS")
    else:
        print("Executor hard-check: FAIL")


if __name__ == "__main__":
    main()
