"""Greedy ROTE Operations coverage planner.

Input format is documented in README.md. This module deliberately consumes
normalized reference data instead of embedding unverified game requirements.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def eligible_members(slot: dict[str, Any], members: list[dict[str, Any]]) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    """Return member/unit pairs satisfying the slot's ownership and tier rules."""
    required_stars = int(slot.get("required_stars", 0) or 0)
    required_relic = int(slot.get("required_relic", 0) or 0)
    unit_id = slot["unit_base_id"]
    matches = []
    for member in members:
        for unit in member.get("units", []):
            if unit.get("unit_base_id") != unit_id:
                continue
            if int(unit.get("stars", 0) or 0) < required_stars:
                continue
            if int(unit.get("relic", 0) or 0) < required_relic:
                continue
            matches.append((member, unit))
    return matches


def plan_operations(data: dict[str, Any]) -> dict[str, Any]:
    """Assign eligible units to platoon slots, prioritizing scarce slots.

    Constraints enforced:
    - A character can only be donated once by a member to the same planet.
    - A member can donate at most 10 units per planet in a phase.
    - Each slot receives at most one assignment.
    - Candidate choice prefers the lower relic tier, then lower unit GP.
    """
    members = data.get("members", [])
    platoons = data.get("platoons", [])
    slots = []
    for platoon in platoons:
        for index, raw_slot in enumerate(platoon.get("slots", []), start=1):
            slot = dict(raw_slot)
            slot.setdefault("slot_id", f'{platoon.get("platoon_id", "platoon")}-{index}')
            slot["platoon_id"] = platoon.get("platoon_id")
            slot["planet_id"] = platoon.get("planet_id")
            slot["phase"] = platoon.get("phase")
            slots.append(slot)

    candidates = {s["slot_id"]: eligible_members(s, members) for s in slots}
    # Most constrained slots first; stable IDs make results deterministic.
    slots.sort(key=lambda s: (len(candidates[s["slot_id"]]), s.get("phase", 0),
                              s.get("planet_id", ""), s.get("platoon_id", ""), s["slot_id"]))

    donated_by_member_planet: dict[tuple[str, str], set[str]] = defaultdict(set)
    assignments = []
    unfilled = []
    for slot in slots:
        planet_id = str(slot.get("planet_id", ""))
        phase = str(slot.get("phase", ""))
        choices = []
        for member, unit in candidates[slot["slot_id"]]:
            member_id = str(member["ally_code"])
            key = (member_id, planet_id)
            unit_id = str(unit["unit_base_id"])
            if unit_id in donated_by_member_planet[key]:
                continue
            if len(donated_by_member_planet[key]) >= int(data.get("donation_cap_per_member_planet_phase", 10)):
                continue
            # Prefer donating lower-tier units; keep stronger versions for combat.
            choices.append((int(unit.get("relic", 0) or 0),
                            int(unit.get("gp", 0) or 0),
                            member_id, member, unit, key, unit_id))
        if not choices:
            unfilled.append({
                "slot_id": slot["slot_id"], "platoon_id": slot.get("platoon_id"),
                "planet_id": planet_id, "phase": phase,
                "unit_base_id": slot["unit_base_id"],
                "eligible_member_count": len(candidates[slot["slot_id"]]),
                "reason": "no eligible member left after ownership, tier, duplicate and donation-cap checks",
            })
            continue
        _, _, member_id, member, unit, key, unit_id = min(choices, key=lambda x: (x[0], x[1], x[2]))
        donated_by_member_planet[key].add(unit_id)
        assignments.append({
            "ally_code": member_id,
            "member_name": member.get("name", ""),
            "unit_base_id": unit_id,
            "unit_stars": int(unit.get("stars", 0) or 0),
            "unit_relic": int(unit.get("relic", 0) or 0),
            "phase": phase,
            "planet_id": planet_id,
            "platoon_id": slot.get("platoon_id"),
            "slot_id": slot["slot_id"],
        })

    summary = {
        "slot_count": len(slots),
        "assigned_count": len(assignments),
        "unfilled_count": len(unfilled),
        "filled_percent": round(100 * len(assignments) / len(slots), 1) if slots else 100.0,
        "unfilled_by_unit": dict(Counter(item["unit_base_id"] for item in unfilled)),
    }
    return {
        "schema_version": 1,
        "source_version": data.get("source_version"),
        "summary": summary,
        "assignments": assignments,
        "unfilled_slots": unfilled,
        "notes": [
            "This is a deterministic greedy baseline, not a proof of globally optimal coverage.",
            "Only supplied, normalized reference requirements are evaluated.",
            "No assignments should be treated as live in-game donations until an officer confirms them.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Plan guild ROTE Operations / Platoon assignments")
    parser.add_argument("input", type=Path, help="Normalized guild + ROTE reference JSON")
    parser.add_argument("-o", "--output", type=Path, default=Path("rote_operations_plan.json"))
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    result = plan_operations(data)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], indent=2))


if __name__ == "__main__":
    main()
