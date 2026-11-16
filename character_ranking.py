#!/usr/bin/env python3
"""Standalone SWGOH character-importance ranking.

This module deliberately has no dependency on the mod optimizer. It consumes a
small, documented CSV plus optional release-date metadata and exposes reusable
Python functions as well as a CLI.
"""
from __future__ import annotations

import argparse
import csv
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable

COUNT_FIELDS = {
    "r5_plus": ("global_relic_r5_plus_players", 0.50),
    "r7_plus": ("global_relic_r7_plus_players", 0.30),
    "r9_plus": ("global_relic_r9_plus_players", 0.20),
}
DEFAULT_GLOBAL_WEIGHT = 0.55
DEFAULT_AGE_WEIGHT = 0.45
DEFAULT_COHORT_DAYS = 365
MIN_COHORT_SIZE = 5


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError):
        return None


def _number(value: Any) -> float | None:
    if value is None or str(value).strip() == "":
        return None
    try:
        return max(0.0, float(value))
    except (TypeError, ValueError):
        return None


def _percentile(values: list[float], value: float) -> float:
    """Mid-rank percentile in [0, 100]; ties receive the same score."""
    if not values:
        return 0.0
    below = sum(item < value for item in values)
    equal = sum(item == value for item in values)
    return 100.0 * (below + 0.5 * equal) / len(values)


def load_character_data(csv_path: str | Path,
                        metadata_path: str | Path | None = None) -> list[dict[str, Any]]:
    """Load count data and optional metadata keyed by baseId.

    Required CSV columns: baseId, name, global_relic_r5_plus_players.
    Optional count columns: global_relic_r7_plus_players,
    global_relic_r9_plus_players. Optional release_date may be in CSV or
    metadata JSON: {"CHARACTER_BASE_ID": {"release_date": "YYYY-MM-DD"}}.
    """
    metadata: dict[str, dict[str, Any]] = {}
    if metadata_path and Path(metadata_path).exists():
        raw = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
        metadata = raw.get("characters", raw)

    rows: list[dict[str, Any]] = []
    with Path(csv_path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"baseId", "name", COUNT_FIELDS["r5_plus"][0]}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError("Missing CSV columns: " + ", ".join(sorted(missing)))

        for source in reader:
            base_id = str(source.get("baseId", "")).strip()
            if not base_id:
                continue
            extra = metadata.get(base_id, {})
            row: dict[str, Any] = {
                "base_id": base_id,
                "name": str(source.get("name", "")).strip() or base_id,
                "release_date": _parse_date(
                    source.get("release_date") or extra.get("release_date")
                ),
                "counts": {},
            }
            for key, (column, _weight) in COUNT_FIELDS.items():
                count = _number(source.get(column))
                if count is not None:
                    row["counts"][key] = count
            if "r5_plus" not in row["counts"]:
                continue
            rows.append(row)
    return rows


def rank_characters(rows: Iterable[dict[str, Any]], *,
                    as_of: date | None = None,
                    cohort_days: int = DEFAULT_COHORT_DAYS,
                    global_weight: float = DEFAULT_GLOBAL_WEIGHT,
                    age_weight: float = DEFAULT_AGE_WEIGHT) -> list[dict[str, Any]]:
    """Return ranked characters using global adoption and age-peer standing.

    The global component preserves the value of broadly used legacy units.
    The age component compares a character only with units released within
    +/- cohort_days, reducing the automatic advantage of long-established
    characters. If fewer than MIN_COHORT_SIZE dated peers exist, age adjustment
    is omitted for that character and the global component is used alone.
    Missing R7+/R9+ columns are ignored and the remaining tier weights are
    renormalized.
    """
    items = [dict(row) for row in rows]
    if not items:
        return []

    today = as_of or date.today()
    tier_weights = {
        key: weight for key, (_column, weight) in COUNT_FIELDS.items()
        if any(key in item.get("counts", {}) for item in items)
    }
    total_weight = sum(tier_weights.values()) or 1.0

    tier_percentiles: dict[str, dict[str, float]] = {}
    for tier in tier_weights:
        values = [float(item["counts"][tier]) for item in items
                  if tier in item.get("counts", {})]
        tier_percentiles[tier] = {
            item["base_id"]: _percentile(values, float(item["counts"][tier]))
            for item in items if tier in item.get("counts", {})
        }

    global_scores: dict[str, float] = {}
    for item in items:
        available = [(tier_weights[tier], tier_percentiles[tier][item["base_id"]])
                     for tier in tier_weights
                     if item["base_id"] in tier_percentiles[tier]]
        weight_sum = sum(weight for weight, _score in available)
        global_scores[item["base_id"]] = (
            sum(weight * score for weight, score in available) / weight_sum
            if weight_sum else 0.0
        )

    dated = [item for item in items if item.get("release_date")]
    output = []
    for item in items:
        release = item.get("release_date")
        peers = []
        if release:
            peers = [
                peer for peer in dated
                if abs((peer["release_date"] - release).days) <= cohort_days
            ]
        age_score = None
        if len(peers) >= MIN_COHORT_SIZE:
            peer_scores = [global_scores[peer["base_id"]] for peer in peers]
            age_score = _percentile(peer_scores, global_scores[item["base_id"]])

        if age_score is None:
            score = global_scores[item["base_id"]]
            used_global, used_age = 1.0, 0.0
        else:
            weight_sum = global_weight + age_weight
            used_global = global_weight / weight_sum
            used_age = age_weight / weight_sum
            score = used_global * global_scores[item["base_id"]] + used_age * age_score

        age_days = (today - release).days if release else None
        output.append({
            "base_id": item["base_id"],
            "name": item["name"],
            "rank_score": round(score, 4),
            "global_score": round(global_scores[item["base_id"]], 4),
            "age_adjusted_score": None if age_score is None else round(age_score, 4),
            "age_days": age_days,
            "release_date": release.isoformat() if release else None,
            "cohort_size": len(peers),
            "score_weights": {
                "global": round(used_global, 4),
                "age_adjusted": round(used_age, 4),
            },
            "counts": item.get("counts", {}),
            "tier_percentiles": {
                tier: round(scores[item["base_id"]], 4)
                for tier, scores in tier_percentiles.items()
                if item["base_id"] in scores
            },
            "age_adjustment_applied": age_score is not None,
        })

    output.sort(key=lambda item: (-item["rank_score"], -item["global_score"], item["base_id"]))
    for index, item in enumerate(output, start=1):
        item["rank"] = index
    return output


def get_character_rank(ranking: Iterable[dict[str, Any]], base_id: str) -> dict[str, Any] | None:
    """Lookup helper for optimizers and other scripts."""
    key = str(base_id).upper()
    return next((dict(item) for item in ranking
                 if str(item.get("base_id", "")).upper() == key), None)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Character counts CSV")
    parser.add_argument("--metadata", help="Optional release-date metadata JSON")
    parser.add_argument("--output", default="character_ranking.json")
    parser.add_argument("--as-of", help="Reference date YYYY-MM-DD (for reproducible tests)")
    parser.add_argument("--cohort-days", type=int, default=DEFAULT_COHORT_DAYS)
    args = parser.parse_args()

    rows = load_character_data(args.input, args.metadata)
    ranking = rank_characters(
        rows,
        as_of=_parse_date(args.as_of),
        cohort_days=max(1, args.cohort_days),
    )
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "method": {
            "global_weight": DEFAULT_GLOBAL_WEIGHT,
            "age_adjusted_weight": DEFAULT_AGE_WEIGHT,
            "cohort_days": args.cohort_days,
            "minimum_cohort_size": MIN_COHORT_SIZE,
            "tier_weights": {key: weight for key, (_column, weight) in COUNT_FIELDS.items()},
        },
        "characters": ranking,
    }
    Path(args.output).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Ranked {len(ranking)} characters -> {args.output}")


if __name__ == "__main__":
    main()
