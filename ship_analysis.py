import csv
from pathlib import Path


SHIPS_FILE = Path("ships.csv")
REPORT_FILE = Path("ship_analysis.md")


CAPITAL_SHIPS = {
    "CAPITALMALEVOLENCE",
    "CAPITALRADDUS",
    "CAPITALMONCALAMARICRUISER",
    "CAPITALSTARDESTROYER",
    "CAPITALNEGOTIATOR",
    "CAPITALJEDICRUISER",
    "CAPITALCHIMAERA",
    "CAPITALFINALIZER",
}


def as_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


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
        return list(csv.DictReader(f))


def stars(ship):
    return as_int(ship.get("rarity"))


def level(ship):
    return as_int(ship.get("level"))


def gear(ship):
    return as_int(ship.get("gearTier"))


def is_capital(ship):
    return ship.get("baseId") in CAPITAL_SHIPS


def star_group(ships, minimum, maximum=None):
    if maximum is None:
        return [
            ship for ship in ships
            if stars(ship) >= minimum
        ]

    return [
        ship for ship in ships
        if minimum <= stars(ship) <= maximum
    ]


def sort_by_stars_then_name(ships):
    return sorted(
        ships,
        key=lambda ship: (
            -stars(ship),
            ship.get("name", "")
        )
    )


def sort_by_stars_then_level_then_name(ships):
    return sorted(
        ships,
        key=lambda ship: (
            stars(ship),
            level(ship),
            ship.get("name", "")
        )
    )


def write_capital_section(lines, ships):
    capitals = [
        ship for ship in ships
        if is_capital(ship)
    ]

    lines.append("## Capital ships")
    lines.append("")
    lines.append(
        "| Statek | ★ | Level | Gear |"
    )
    lines.append(
        "|---|---:|---:|---:|"
    )

    for ship in sort_by_stars_then_name(capitals):
        lines.append(
            f"| **{ship['name']}** | "
            f"{stars(ship)} | "
            f"{level(ship)} | "
            f"G{gear(ship)} |"
        )

    lines.append("")


def write_incomplete_section(lines, ships):
    incomplete = [
        ship for ship in ships
        if stars(ship) < 7
    ]

    lines.append("## Statki poniżej 7★")
    lines.append("")

    if not incomplete:
        lines.append(
            "Wszystkie statki są na 7★."
        )
        lines.append("")
        return

    lines.append(
        "| Statek | ★ | Level | Gear |"
    )
    lines.append(
        "|---|---:|---:|---:|"
    )

    for ship in sort_by_stars_then_level_then_name(
        incomplete
    ):
        lines.append(
            f"| {ship['name']} | "
            f"{stars(ship)} | "
            f"{level(ship)} | "
            f"G{gear(ship)} |"
        )

    lines.append("")


def write_star_summary(lines, ships):
    counts = {}

    for ship in ships:
        star = stars(ship)
        counts[star] = counts.get(star, 0) + 1

    lines.append("## Podsumowanie ★")
    lines.append("")

    lines.append(
        f"- Wszystkich statków: **{len(ships)}**"
    )
    lines.append(
        f"- Statków 7★: **{counts.get(7, 0)}**"
    )
    lines.append(
        f"- Statków 6★: **{counts.get(6, 0)}**"
    )
    lines.append(
        f"- Statków 5★: **{counts.get(5, 0)}**"
    )
    lines.append(
        f"- Statków 4★: **{counts.get(4, 0)}**"
    )

    other = sum(
        quantity
        for star, quantity in counts.items()
        if star not in {4, 5, 6, 7}
    )

    if other:
        lines.append(
            f"- Statków z inną liczbą ★: **{other}**"
        )

    lines.append("")


def write_priority_candidates(lines, ships):
    candidates = [
        ship for ship in ships
        if not is_capital(ship)
        and stars(ship) < 7
    ]

    candidates = sorted(
        candidates,
        key=lambda ship: (
            stars(ship),
            -level(ship),
            ship.get("name", "")
        )
    )

    lines.append(
        "## Kandydaci do dalszego rozwoju"
    )
    lines.append("")

    if not candidates:
        lines.append(
            "Brak statków poniżej 7★."
        )
        lines.append("")
        return

    lines.append(
        "To jest **lista techniczna**, a nie kolejka farmienia. "
        "Priorytet flotowy zostanie dodany po połączeniu "
        "statków z wymaganiami flot i Journey."
    )
    lines.append("")

    lines.append(
        "| Statek | ★ | Level | Gear |"
    )
    lines.append(
        "|---|---:|---:|---:|"
    )

    for ship in candidates:
        lines.append(
            f"| {ship['name']} | "
            f"{stars(ship)} | "
            f"{level(ship)} | "
            f"G{gear(ship)} |"
        )

    lines.append("")


def write_7star_section(lines, ships):
    completed = [
        ship for ship in ships
        if stars(ship) == 7
    ]

    lines.append("## Statki 7★")
    lines.append("")

    for ship in sorted(
        completed,
        key=lambda x: x.get("name", "")
    ):
        lines.append(
            f"- {ship['name']}"
        )

    lines.append("")


def generate_report(ships):
    lines = []

    lines.append("# Ship Analysis")
    lines.append("")
    lines.append(
        "Automatyczna analiza aktualnego stanu statków "
        "na podstawie `ships.csv`."
    )
    lines.append("")

    write_star_summary(
        lines,
        ships
    )

    write_capital_section(
        lines,
        ships
    )

    write_incomplete_section(
        lines,
        ships
    )

    write_priority_candidates(
        lines,
        ships
    )

    write_7star_section(
        lines,
        ships
    )

    REPORT_FILE.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )


def main():
    ships = load_ships()

    if not ships:
        raise RuntimeError(
            "ships.csv jest pusty."
        )

    generate_report(ships)

    print(
        f"Wygenerowano {REPORT_FILE}"
    )
    print(
        f"Liczba statków: {len(ships)}"
    )


if __name__ == "__main__":
    main()
