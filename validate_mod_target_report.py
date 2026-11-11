#!/usr/bin/env python3
"""Fail a workflow run when the selected mod target has no complete six-slot report."""
from __future__ import annotations

import argparse
import re
from pathlib import Path


SLOTS = ("Arrow", "Square", "Diamond", "Triangle", "Circle", "Cross")


def parse_targets(value: str) -> list[str]:
    targets = []
    for item in str(value or "").split(","):
        target = item.strip().upper()
        if not target:
            continue
        if not re.fullmatch(r"[A-Z0-9_]+", target):
            raise ValueError("Nieprawidłowy BASE_ID celu: {!r}".format(item))
        if target not in targets:
            targets.append(target)
    if not targets:
        raise ValueError("Nie wskazano żadnego celu.")
    return targets


def validate_report(report: str, targets: list[str]) -> list[str]:
    errors = []
    for target in targets:
        heading = "### {} — najlepszy wirtualny build 6/6".format(target)
        start = report.find(heading)
        if start < 0:
            errors.append("{}: brak sekcji kompletnego buildu 6/6.".format(target))
            continue

        section = report[start + len(heading):]
        next_heading = re.search(r"\n###? ", section)
        if next_heading:
            section = section[:next_heading.start()]

        table_header = "| Slot | Mod — parametry wyszukiwalne | Źródło | Fit |"
        if table_header not in section:
            errors.append("{}: brak tabeli sześciu modów.".format(target))
            continue

        table = section.split(table_header, 1)[1]
        found = []
        for line in table.splitlines():
            if not line.startswith("|"):
                if found:
                    break
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) < 4 or cells[0] in {"---", "Slot"}:
                continue
            if cells[0] in SLOTS:
                found.append(cells[0])

        if len(found) != 6 or set(found) != set(SLOTS) or len(set(found)) != 6:
            errors.append(
                "{}: build nie zawiera dokładnie sześciu różnych slotów; znaleziono: {}."
                .format(target, ", ".join(found) or "brak")
            )

    chain_heading = "## BEZPIECZNY ŁAŃCUCH — walidacja globalna"
    if chain_heading not in report:
        errors.append("Brak sekcji walidacji łańcucha transferów.")
    elif not (
        "**STATUS: OK" in report or "**STATUS: BLOKADA" in report
    ):
        errors.append("Brak jawnego statusu walidacji łańcucha transferów.")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--targets", required=True, help="BASE_ID,BASE_ID")
    parser.add_argument("--report", default="mod_analysis.md")
    args = parser.parse_args()

    targets = parse_targets(args.targets)
    report = Path(args.report).read_text(encoding="utf-8")
    errors = validate_report(report, targets)
    if errors:
        for error in errors:
            print("FAIL:", error)
        print("MOD TARGET REPORT: INCOMPLETE")
        return 1

    print("PASS: kompletne sekcje 6/6 dla: {}".format(", ".join(targets)))
    print("PASS: obecna walidacja łańcucha transferów.")
    print("MOD TARGET REPORT: COMPLETE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
