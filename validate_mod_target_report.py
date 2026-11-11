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
    """Enforce the player-facing Vel/Cinta report, not merely a technical 6/6 dump."""
    errors = []
    required_sections = (
        "## Status",
        "### Sześć modów docelowych",
        "## MOD — mody przenoszone na cel",
        "## PATCH — uzupełnienie dawców",
        "## Kontrola profili użytych w łańcuchu",
        "## Kolejność przekładania",
        "## Wpływ na postacie-dawców",
        "## Założenia projekcji",
    )
    for heading in required_sections:
        if heading not in report:
            errors.append("Brak wymaganej sekcji raportu użytkowego: {}".format(heading))

    if "### Sześć modów docelowych" in report:
        section = report.split("### Sześć modów docelowych", 1)[1]
        for slot in SLOTS:
            match = re.search(r"^#### " + re.escape(slot) + r"\s*$", section, re.MULTILINE)
            if not match:
                errors.append("Brak sekcji slotu {}.".format(slot))
                continue
            next_slot = re.search(r"^#### (?:Arrow|Square|Diamond|Triangle|Circle|Cross)\s*$", section[match.end():], re.MULTILINE)
            slot_text = section[match.end():match.end() + next_slot.start()] if next_slot else section[match.end():]
            if "**Obecny mod:**" not in slot_text:
                errors.append("{}: brak pełnego opisu obecnego moda.".format(slot))
            if "**Proponowany mod:**" not in slot_text:
                errors.append("{}: brak pełnego opisu proponowanego moda.".format(slot))

    if "## Kolejność przekładania" in report and "**Wykonalność fizyczna:** POTWIERDZONA" in report:
        order = report.split("## Kolejność przekładania", 1)[1]
        if not re.search(r"(?m)^\s*1\.\s+\*\*", order):
            errors.append("Brak ponumerowanej, konkretnej kolejności wykonania.")
    if "**Wykonalność fizyczna:**" not in report:
        errors.append("Brak jawnego statusu walidacji fizycznej.")
    if "**Ocena:**" not in report:
        errors.append("Brak klasyfikacji REKOMENDACJA/KOMPROMIS/BLOKADA.")
    if "Brak kompletnego buildu" not in report and "## Kontrola profili użytych w łańcuchu" not in report:
        errors.append("Brak kontroli profili uczestników łańcucha.")

    # Guard against accidentally publishing the former technical dashboard.
    forbidden = ("## Globalny optimizer 6-slotowy", "## Najważniejsi kandydaci",
                 "| Akcja | Mod | Źródło | Set | Tier |")
    if any(token in report for token in forbidden):
        errors.append("Wygenerowano techniczny raport zamiast raportu użytkowego Vel/Cinta.")
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
