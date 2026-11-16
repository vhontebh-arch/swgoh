#!/usr/bin/env python3
"""Import the player's Stack Rank export as the sole character-importance source.

Final Tier is the primary importance measure (lower is more important).
Rank is retained as the source's secondary ordering; it is never substituted
for Final Tier. The module is intentionally independent of the mod optimizer.
"""
from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

SOURCE_NAME = "Stack Rank"
SOURCE_URL = (
    "https://swgoh.spineless.net/stackrank?"
    "omicronGac=true&omicronTw=true&omicronTb=true&omicronRaids=true&"
    "omicronConquest=true&allyCode=972824625&showFullDetails=true"
)
EXPECTED_COLUMNS = [
    "Rank", "Character", "Sort Score", "SubSort Score", "Final Tier",
    "Base Tier", "Synergy Enhancement", "Omicron Boost",
    "Omicron Synergy Boost", "Relic Gear Level", "Ability Score",
]
INTEGER_FIELDS = {
    "Rank": "rank",
    "Final Tier": "final_tier",
    "Base Tier": "base_tier",
    "Synergy Enhancement": "synergy_enhancement",
    "Omicron Boost": "omicron_boost",
    "Omicron Synergy Boost": "omicron_synergy_boost",
    "Ability Score": "ability_score",
}
FLOAT_FIELDS = {
    "Sort Score": "sort_score",
    "SubSort Score": "subsort_score",
    "Relic Gear Level": "relic_gear_level",
}


def load_stack_rank(path: str | Path) -> list[dict[str, Any]]:
    """Read the tab-delimited Stack Rank export without changing its meaning."""
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames != EXPECTED_COLUMNS:
            raise ValueError(
                "Unexpected Stack Rank columns. Expected: "
                + ", ".join(EXPECTED_COLUMNS)
            )
        result = []
        seen_names: set[str] = set()
        seen_ranks: set[int] = set()
        for line_number, source in enumerate(reader, start=2):
            name = (source.get("Character") or "").strip()
            if not name:
                raise ValueError(f"Empty Character at line {line_number}")
            normalized = name.casefold()
            if normalized in seen_names:
                raise ValueError(f"Duplicate Character: {name}")
            seen_names.add(normalized)

            row: dict[str, Any] = {"character": name}
            for source_key, target_key in INTEGER_FIELDS.items():
                try:
                    row[target_key] = int(source[source_key])
                except (TypeError, ValueError):
                    raise ValueError(
                        f"Invalid {source_key} at line {line_number}"
                    ) from None
            for source_key, target_key in FLOAT_FIELDS.items():
                try:
                    row[target_key] = float(source[source_key])
                except (TypeError, ValueError):
                    raise ValueError(
                        f"Invalid {source_key} at line {line_number}"
                    ) from None

            if not 1 <= row["final_tier"] <= 19:
                raise ValueError(f"Final Tier outside 1..19 for {name}")
            if not 1 <= row["base_tier"] <= 19:
                raise ValueError(f"Base Tier outside 1..19 for {name}")
            if row["rank"] < 1 or row["rank"] in seen_ranks:
                raise ValueError(f"Invalid or duplicate Rank for {name}")
            seen_ranks.add(row["rank"])

            # Final Tier already incorporates base tier, synergy and boosts.
            # Do not add those inputs again as separate score components.
            row["importance_score"] = 20 - row["final_tier"]
            row["source"] = SOURCE_NAME
            result.append(row)

    result.sort(key=lambda item: item["rank"])
    return result


def rank_characters(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Order by Final Tier (primary), then original Stack Rank (secondary)."""
    return sorted(rows, key=lambda item: (item["final_tier"], item["rank"]))


def get_character_rank(
    ranking: list[dict[str, Any]], character: str
) -> dict[str, Any] | None:
    """Find an entry by its exact display name, case-insensitively."""
    key = str(character).strip().casefold()
    return next(
        (dict(item) for item in ranking
         if str(item.get("character", "")).casefold() == key),
        None,
    )


def build_payload(input_path: str | Path) -> dict[str, Any]:
    rows = load_stack_rank(input_path)
    return {
        "schema_version": 2,
        "source": SOURCE_NAME,
        "source_url": SOURCE_URL,
        "imported_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "record_count": len(rows),
        "method": {
            "primary_field": "final_tier",
            "primary_direction": "ascending (1 is most important; 19 least important)",
            "secondary_field": "rank",
            "secondary_direction": "ascending (original Stack Rank order)",
            "importance_score": "20 - final_tier",
            "note": (
                "Final Tier already includes Base Tier, Synergy Enhancement, "
                "Omicron Boost, Omicron Synergy Boost and Ability Score effects; "
                "these fields are retained for audit and are not scored again."
            ),
            "omicron_boost_options": {
                "gac": True, "territory_war": True, "territory_battle": True,
                "raids": True, "conquest": True,
            },
        },
        "characters": rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", default="data/stack_rank.tsv",
        help="Tab-delimited Stack Rank export",
    )
    parser.add_argument("--output", default="character_ranking.json")
    parser.add_argument("--expected-count", type=int, default=None)
    args = parser.parse_args()

    payload = build_payload(args.input)
    if args.expected_count is not None and payload["record_count"] != args.expected_count:
        raise SystemExit(
            f"Expected {args.expected_count} records, got {payload['record_count']}"
        )
    Path(args.output).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Imported {payload['record_count']} Stack Rank characters -> {args.output}")


if __name__ == "__main__":
    main()
