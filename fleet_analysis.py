import csv
from pathlib import Path


SHIPS_FILE = Path("ships.csv")
REPORT_FILE = Path("fleet_analysis.md")


# Statki przypisane do najważniejszych flot.
# "core" = statki charakterystyczne / najważniejsze dla danej floty.
# "reinforcements" = typowe statki rezerwowe.
#
# To nie jest lista wymagań Journey. Journey jest raportowane osobno.
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


# Rzeczywiste wymagania statkowe Journey/Capital Ship.
# Lista służy do wskazania braków rozwojowych, a nie do
# odtwarzania całej mechaniki eventu.
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


def load_ships():
    if not SHIPS_FILE.exists():
        raise FileNotFoundError(
            f"Nie znaleziono pliku {SHIPS_FILE}"
        )

    with SHIPS_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as f:
        rows = list(csv.DictReader(f))

    if not rows:
        raise RuntimeError(
            "ships.csv jest pusty."
        )

    return {
        row.get("name", "").strip(): row
        for row in rows
        if row.get("name")
    }


def stars(ship):
    try:
        return int(ship.get("rarity", 0))
    except (TypeError, ValueError):
        return 0


def level(ship):
    try:
        return int(ship.get("level", 0))
    except (TypeError, ValueError):
        return 0


def gear(ship):
    try:
        return int(ship.get("gearTier", 0))
    except (TypeError, ValueError):
        return 0


def star_status(ship):
    if ship is None:
        return "BRAK W CSV"

    current = stars(ship)

    if current >= 7:
        return "READY"

    return f"{current}★ → 7★"


def format_ship_row(name, ships, role):
    ship = ships.get(name)

    if ship is None:
        return (
            f"| {name} | — | — | — | "
            f"**BRAK W CSV** | {role} |"
        )

    current = stars(ship)

    return (
        f"| {name} | "
        f"{current}★ | "
        f"{level(ship)} | "
        f"G{gear(ship)} | "
        f"{star_status(ship)} | "
        f"{role} |"
    )


def get_missing(ships, names):
    result = []

    for name in names:
        ship = ships.get(name)

        if ship is None:
            result.append((name, 0))
            continue

        current = stars(ship)

        if current < 7:
            result.append((name, current))

    return sorted(
        result,
        key=lambda item: (
            item[1],
            item[0]
        )
    )


def write_fleet_section(lines, fleet_name, fleet, ships):
    capital_name = fleet["capital"]
    capital = ships.get(capital_name)

    lines.append(f"## {fleet_name}")
    lines.append("")

    if capital is None:
        lines.append(
            f"**Capital ship:** {capital_name} — BRAK W CSV"
        )
    else:
        lines.append(
            f"**Capital ship:** "
            f"{capital_name} — "
            f"{stars(capital)}★"
        )

    lines.append("")

    lines.append(
        "| Statek | ★ | Level | Gear | Status | Rola |"
    )
    lines.append(
        "|---|---:|---:|---:|---|---|"
    )

    for name in fleet["core"]:
        lines.append(
            format_ship_row(
                name,
                ships,
                "CORE"
            )
        )

    for name in fleet["reinforcements"]:
        lines.append(
            format_ship_row(
                name,
                ships,
                "REINFORCEMENT"
            )
        )

    lines.append("")

    core_missing = get_missing(
        ships,
        fleet["core"]
    )

    reinforcement_missing = get_missing(
        ships,
        fleet["reinforcements"]
    )

    lines.append(
        f"**Core poniżej 7★:** "
        f"{len(core_missing)}"
    )

    lines.append(
        f"**Reinforcementy poniżej 7★:** "
        f"{len(reinforcement_missing)}"
    )

    lines.append("")

    if core_missing:
        lines.append("### Braki CORE")

        for name, current in core_missing:
            lines.append(
                f"- **{name}** — "
                f"{current}★ → 7★"
            )

        lines.append("")

    if reinforcement_missing:
        lines.append("### Braki reinforcementów")

        for name, current in reinforcement_missing:
            lines.append(
                f"- {name} — "
                f"{current}★ → 7★"
            )

        lines.append("")

    if not core_missing and not reinforcement_missing:
        lines.append(
            "Wszystkie zdefiniowane statki tej floty są 7★."
        )
        lines.append("")


def write_global_summary(lines, ships):
    lines.append("## Podsumowanie konta")
    lines.append("")

    total = len(ships)

    counts = {}

    for ship in ships.values():
        current = stars(ship)
        counts[current] = counts.get(current, 0) + 1

    lines.append(
        f"- Wszystkich statków: **{total}**"
    )
    lines.append(
        f"- 7★: **{counts.get(7, 0)}**"
    )
    lines.append(
        f"- 6★: **{counts.get(6, 0)}**"
    )
    lines.append(
        f"- 5★: **{counts.get(5, 0)}**"
    )
    lines.append(
        f"- 4★: **{counts.get(4, 0)}**"
    )

    lines.append("")


def write_low_star_priority(lines, ships):
    lines.append("## Statki <7★")
    lines.append("")

    candidates = []

    for name, ship in ships.items():
        current = stars(ship)

        if current < 7:
            candidates.append(
                (
                    current,
                    name,
                    level(ship),
                    gear(ship)
                )
            )

    candidates.sort(
        key=lambda item: (
            item[0],
            item[1]
        )
    )

    if not candidates:
        lines.append(
            "Brak statków poniżej 7★."
        )
        lines.append("")
        return

    lines.append(
        "| Statek | ★ | Level | Gear |"
    )
    lines.append(
        "|---|---:|---:|---:|"
    )

    for current, name, lvl, g in candidates:
        lines.append(
            f"| {name} | "
            f"{current}★ | "
            f"{lvl} | "
            f"G{g} |"
        )

    lines.append("")


def write_cross_fleet_usage(lines, ships):
    usage = {}

    for fleet_name, fleet in FLEETS.items():
        all_names = (
            fleet["core"]
            + fleet["reinforcements"]
        )

        for name in all_names:
            usage.setdefault(
                name,
                []
            ).append(fleet_name)

    shared = [
        (name, fleets)
        for name, fleets in usage.items()
        if len(fleets) > 1
    ]

    shared.sort(
        key=lambda item: (
            -len(item[1]),
            item[0]
        )
    )

    lines.append(
        "## Statki używane przez wiele flot"
    )
    lines.append("")

    if not shared:
        lines.append(
            "Brak wspólnych statków w zdefiniowanych składach."
        )
        lines.append("")
        return

    lines.append(
        "| Statek | ★ | Floty |"
    )
    lines.append(
        "|---|---:|---|"
    )

    for name, fleets in shared:
        ship = ships.get(name)

        if ship is None:
            current = "—"
        else:
            current = f"{stars(ship)}★"

        lines.append(
            f"| {name} | "
            f"{current} | "
            f"{', '.join(fleets)} |"
        )

    lines.append("")


def write_journey_section(lines, ships):
    lines.append(
        "## Statki związane z Journey"
    )
    lines.append("")

    for journey, required in JOURNEY_REQUIREMENTS.items():
        lines.append(
            f"### {journey}"
        )
        lines.append("")

        lines.append(
            "| Statek | ★ | Status |"
        )
        lines.append(
            "|---|---:|---|"
        )

        missing = []

        for name in required:
            ship = ships.get(name)

            if ship is None:
                current = "—"
                status = "BRAK W CSV"
                missing.append(
                    (name, 0)
                )
            else:
                current = f"{stars(ship)}★"

                if stars(ship) >= 7:
                    status = "READY"
                else:
                    status = (
                        f"{stars(ship)}★ → 7★"
                    )
                    missing.append(
                        (name, stars(ship))
                    )

            lines.append(
                f"| {name} | "
                f"{current} | "
                f"{status} |"
            )

        lines.append("")

        if missing:
            lines.append(
                "**Braki:**"
            )

            for name, current in sorted(
                missing,
                key=lambda item: (
                    item[1],
                    item[0]
                )
            ):
                lines.append(
                    f"- {name} — "
                    f"{current}★ → 7★"
                )

            lines.append("")
        else:
            lines.append(
                "Wszystkie wymienione statki są 7★."
            )
            lines.append("")


def generate_report(ships):
    lines = []

    lines.append("# Fleet Analysis")
    lines.append("")

    lines.append(
        "Automatyczna analiza flot na podstawie "
        "`ships.csv`."
    )

    lines.append("")

    lines.append(
        "> **READY = 7★ statku.** "
        "Nie oznacza automatycznie gotowej całej floty."
    )

    lines.append("")

    write_global_summary(
        lines,
        ships
    )

    for fleet_name, fleet in FLEETS.items():
        write_fleet_section(
            lines,
            fleet_name,
            fleet,
            ships
        )

    write_journey_section(
        lines,
        ships
    )

    write_cross_fleet_usage(
        lines,
        ships
    )

    write_low_star_priority(
        lines,
        ships
    )

    lines.append(
        "## Uwagi"
    )
    lines.append("")
    lines.append(
        "- Dane o ★, levelu i gearze pochodzą z `ships.csv`."
    )
    lines.append(
        "- Lista flot jest warstwą analityczną i nie zmienia danych konta."
    )
    lines.append(
        "- Brak statku w `ships.csv` nie oznacza automatycznie, "
        "że konto go nie posiada; oznacza tylko brak wpisu w aktualnym eksporcie."
    )
    lines.append(
        "- Kolejność statków w raporcie nie jest rankingiem farmienia."
    )
    lines.append("")

    return "\n".join(lines)


def main():
    ships = load_ships()

    report = generate_report(
        ships
    )

    REPORT_FILE.write_text(
        report,
        encoding="utf-8"
    )

    print(
        f"Wygenerowano {REPORT_FILE}"
    )

    print(
        f"Liczba statków: {len(ships)}"
    )


if __name__ == "__main__":
    main()
