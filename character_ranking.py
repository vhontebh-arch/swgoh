#!/usr/bin/env python3
"""Import Stack Rank and attach canonical SWGOH unit baseIds."""
from __future__ import annotations
import argparse, csv, json
from datetime import datetime
from pathlib import Path
from typing import Any

SOURCE_NAME = "Stack Rank"
SOURCE_URL = "https://swgoh.spineless.net/stackrank?omicronGac=true&omicronTw=true&omicronTb=true&omicronRaids=true&omicronConquest=true&allyCode=972824625&showFullDetails=true"
DEFAULT_MAPPING = Path(__file__).resolve().parent / "data" / "character_base_id_mapping.json"
EXPECTED_COLUMNS = ["Rank", "Character", "Sort Score", "SubSort Score", "Final Tier", "Base Tier", "Synergy Enhancement", "Omicron Boost", "Omicron Synergy Boost", "Relic Gear Level", "Ability Score"]
INTEGER_FIELDS = {"Rank":"rank","Final Tier":"final_tier","Base Tier":"base_tier","Synergy Enhancement":"synergy_enhancement","Omicron Boost":"omicron_boost","Omicron Synergy Boost":"omicron_synergy_boost","Ability Score":"ability_score"}
FLOAT_FIELDS = {"Sort Score":"sort_score","SubSort Score":"subsort_score","Relic Gear Level":"relic_gear_level"}

def load_base_id_mapping(path: str | Path = DEFAULT_MAPPING) -> dict[str, dict[str, str]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    entries = payload.get("characters", [])
    if payload.get("record_count") != len(entries):
        raise ValueError("baseId mapping record_count does not match its entries")
    by_name, seen_ids = {}, set()
    for entry in entries:
        name, base_id = str(entry.get("character","")).strip(), str(entry.get("base_id","")).strip()
        if not name or not base_id: raise ValueError("baseId mapping contains an empty name or base_id")
        if name.casefold() in by_name or base_id in seen_ids:
            raise ValueError(f"Duplicate name or base_id in mapping: {name} / {base_id}")
        by_name[name.casefold()] = entry
        seen_ids.add(base_id)
    return by_name

def rank_importance_score(rank: int, record_count: int) -> float:
    """Bounded Rank-derived value: 3.0 at Rank 1, 1.0 at the last rank."""
    if record_count < 2:
        raise ValueError("record_count must be at least 2")
    if not 1 <= rank <= record_count:
        raise ValueError(f"Rank must be within 1..{record_count}")
    percentile = (rank - 1) / (record_count - 1)
    return round(1.0 + 2.0 * (1.0 - percentile) ** 2, 6)

def load_stack_rank(path: str | Path, mapping_path: str | Path | None = None) -> list[dict[str, Any]]:
    mapping = load_base_id_mapping(mapping_path) if mapping_path else None
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames != EXPECTED_COLUMNS:
            raise ValueError("Unexpected Stack Rank columns. Expected: " + ", ".join(EXPECTED_COLUMNS))
        result, seen_names, seen_ranks = [], set(), set()
        for line_number, source in enumerate(reader, start=2):
            name = (source.get("Character") or "").strip()
            if not name: raise ValueError(f"Empty Character at line {line_number}")
            if name.casefold() in seen_names: raise ValueError(f"Duplicate Character: {name}")
            seen_names.add(name.casefold())
            row: dict[str, Any] = {"character": name}
            if mapping is not None:
                match = mapping.get(name.casefold())
                if match is None: raise ValueError(f"No baseId mapping for Stack Rank character: {name}")
                row["base_id"] = match["base_id"]
            for source_key, target_key in INTEGER_FIELDS.items():
                try: row[target_key] = int(source[source_key])
                except (TypeError, ValueError): raise ValueError(f"Invalid {source_key} at line {line_number}") from None
            for source_key, target_key in FLOAT_FIELDS.items():
                try: row[target_key] = float(source[source_key])
                except (TypeError, ValueError): raise ValueError(f"Invalid {source_key} at line {line_number}") from None
            if not 1 <= row["final_tier"] <= 19: raise ValueError(f"Final Tier outside 1..19 for {name}")
            if not 1 <= row["base_tier"] <= 19: raise ValueError(f"Base Tier outside 1..19 for {name}")
            if row["rank"] < 1 or row["rank"] in seen_ranks: raise ValueError(f"Invalid or duplicate Rank for {name}")
            seen_ranks.add(row["rank"])
            result.append(row)
    if not result: raise ValueError("Stack Rank contains no character rows")
    expected_ranks = set(range(1, len(result) + 1))
    if seen_ranks != expected_ranks:
        raise ValueError("Stack Rank values must form a continuous sequence from 1 to record count")
    for row in result:
        row["importance_score"] = rank_importance_score(row["rank"], len(result))
        row["source"] = SOURCE_NAME
    if mapping is not None and len(result) != len(mapping):
        raise ValueError(f"Stack Rank has {len(result)} rows but mapping has {len(mapping)} entries")
    return sorted(result, key=lambda item:item["rank"])

def load_ranking_json(path: str | Path = "character_ranking.json") -> list[dict[str, Any]]:
    """Load the generated Stack Rank snapshot for optimizer chain scoring."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = payload.get("characters", [])
    record_count = int(payload.get("record_count", 0))
    if record_count < 2 or len(rows) != record_count:
        raise ValueError("character_ranking.json has an invalid record_count")
    seen = set()
    for item in rows:
        rank = int(item.get("rank", 0))
        base_id = str(item.get("base_id", "")).strip()
        if not base_id or base_id in seen:
            raise ValueError("character_ranking.json has an empty or duplicate base_id")
        rank_importance_score(rank, record_count)
        seen.add(base_id)
    return rows


def rank_weighted_donor_delta(moves, ranking, aliases=None) -> float:
    """Sum donor build deltas weighted by Stack Rank; target gain is not included."""
    aliases = aliases or {}
    rows = list(ranking or [])
    count = len(rows)
    by_id = {
        str(item.get("base_id", "")).upper(): item
        for item in rows if item.get("base_id")
    }
    deltas: dict[str, float] = {}
    for move in moves or []:
        owner = str(move.get("owner", "") or "")
        base_id = str(aliases.get(owner, owner) or "").upper()
        if not base_id:
            continue
        deltas[base_id] = deltas.get(base_id, 0.0) + float(move.get("gain", 0.0) or 0.0)
    total = 0.0
    for base_id, delta in deltas.items():
        item = by_id.get(base_id)
        weight = (
            rank_importance_score(int(item["rank"]), count)
            if item and count >= 2 else 1.0
        )
        total += delta * weight
    return round(total, 6)


def rank_characters(rows):
    """Return characters in source Rank order (1 is most important)."""
    return sorted(rows, key=lambda item:item["rank"])

def get_character_rank(ranking, character):
    key = str(character).strip().casefold()
    return next((dict(item) for item in ranking if str(item.get("character","")).casefold()==key or str(item.get("base_id","")).casefold()==key),None)

def build_payload(input_path: str | Path, mapping_path: str | Path = DEFAULT_MAPPING):
    rows = load_stack_rank(input_path, mapping_path)
    mapping_payload = json.loads(Path(mapping_path).read_text(encoding="utf-8"))
    return {"schema_version":4,"source":SOURCE_NAME,"source_url":SOURCE_URL,
        "snapshot_date":datetime.now().date().isoformat(),"record_count":len(rows),
        "base_id_mapping":mapping_payload["sources"],
        "method":{"primary_field":"rank","primary_direction":"ascending (1 is most important; larger values are less important)",
        "importance_score":"1 + 2 * (1 - (rank - 1) / (record_count - 1))^2; bounded 1.0..3.0",
        "secondary_fields":["final_tier","sort_score"],
        "note":"Rank is the sole primary importance signal. Final Tier and Sort Score are retained for audit and are not added to importance_score; Sort Score may later be used only as a small, separate donor-protection adjustment.",
        "omicron_boost_options":{"gac":True,"territory_war":True,"territory_battle":True,"raids":True,"conquest":True}},
        "characters":rows}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",default="data/stack_rank.tsv")
    parser.add_argument("--mapping",default=str(DEFAULT_MAPPING))
    parser.add_argument("--output",default="character_ranking.json")
    parser.add_argument("--expected-count",type=int,default=None)
    args=parser.parse_args()
    payload=build_payload(args.input,args.mapping)
    if args.expected_count is not None and payload["record_count"]!=args.expected_count:
        raise SystemExit(f"Expected {args.expected_count} records, got {payload['record_count']}")
    Path(args.output).write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Imported {payload['record_count']} Stack Rank characters with baseIds -> {args.output}")

if __name__=="__main__": main()
