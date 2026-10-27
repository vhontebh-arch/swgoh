#!/usr/bin/env python3
"""Diagnostic importer: inspect Comlink guild response before normalizing roster data.

Import every public roster in the guild containing the configured seed player.

Requires a running SWGOH Comlink HTTP service. Writes normalized JSON locally;
the caller should upload it as a private/short-lived CI artifact, not commit it.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def post_json(base_url: str, endpoint: str, payload: dict, retries: int = 3) -> dict:
    body = json.dumps({"payload": payload, "enums": False}).encode("utf-8")
    request = Request(
        base_url.rstrip("/") + "/" + endpoint.lstrip("/"),
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    last_error = None
    for attempt in range(retries):
        try:
            with urlopen(request, timeout=90) as response:
                result = json.loads(response.read().decode("utf-8"))
            if not isinstance(result, dict):
                raise RuntimeError(f"/{endpoint} returned a non-object response")
            return result
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError, RuntimeError) as exc:
            last_error = exc
            if attempt + 1 < retries:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"Comlink /{endpoint} failed after {retries} attempts: {last_error}")


def normalize_player(player: dict, expected_player_id: str | None = None) -> dict:
    player_id = player.get("playerId") or expected_player_id
    roster = player.get("rosterUnit") or []
    units = []
    for unit in roster:
        if not isinstance(unit, dict):
            continue
        # Preserve source fields for future mapping; do not invent relic/tier values.
        units.append({
            "unit_id": unit.get("definitionId") or unit.get("unitId"),
            "definition_id": unit.get("definitionId"),
            "current_rarity": unit.get("currentRarity"),
            "current_level": unit.get("currentLevel"),
            "current_tier": unit.get("currentTier"),
            "relic_tier": unit.get("relic"),
            "gear": unit.get("equipment"),
            "skills": unit.get("skill"),
            "source": unit,
        })
    return {
        "player_id": player_id,
        "ally_code": str(player.get("allyCode") or ""),
        "name": player.get("name") or "",
        "guild_id": player.get("guildId"),
        "guild_name": player.get("guildName") or "",
        "galactic_power": player.get("galacticPower"),
        "roster_unit_count": len(units),
        "units": units,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ally-code", default=os.environ.get("ROTE_ALLY_CODE", "972824625"))
    parser.add_argument("--comlink-url", default=os.environ.get("COMLINK_URL", "http://127.0.0.1:3000"))
    parser.add_argument("--output", default="rote_planner/imports/guild_rosters.json")
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()

    ally_code = "".join(ch for ch in args.ally_code if ch.isdigit())
    if len(ally_code) != 9:
        raise SystemExit("ROTE_ALLY_CODE must be a 9-digit Ally Code.")

    seed = post_json(args.comlink_url, "player", {"allyCode": ally_code})
    guild_id = seed.get("guildId")
    if not guild_id:
        raise SystemExit("Seed profile has no guildId; confirm the account belongs to a guild.")

    guild = post_json(args.comlink_url, "guild", {"guildId": guild_id, "includeRecentGuildActivityInfo": True})
    members = guild.get("member") or []
    player_ids = list(dict.fromkeys(
        str(member.get("playerId")) for member in members
        if isinstance(member, dict) and member.get("playerId")
    ))
    if not player_ids:
        # Diagnostic only: log response structure, never player values or roster data.
        print("DEBUG guild response top-level keys:", sorted(guild.keys()), file=sys.stderr)
        print("DEBUG guild response member type:", type(guild.get("member")).__name__, file=sys.stderr)
        print("DEBUG guild response member count:", len(guild.get("member") or []) if isinstance(guild.get("member"), list) else "n/a", file=sys.stderr)
        profile = guild.get("profile")
        print("DEBUG guild response profile keys:", sorted(profile.keys()) if isinstance(profile, dict) else type(profile).__name__, file=sys.stderr)
        if isinstance(guild.get("member"), list) and guild["member"]:
            first = guild["member"][0]
            print("DEBUG first member keys:", sorted(first.keys()) if isinstance(first, dict) else type(first).__name__, file=sys.stderr)
        raise SystemExit("Guild response contains no member player IDs; refusing to create an empty import.")

    players: list[dict] = [normalize_player(seed)]
    seed_player_id = seed.get("playerId")
    remaining = [pid for pid in player_ids if pid != seed_player_id]
    failures = []

    def fetch_member(player_id: str) -> dict:
        return post_json(args.comlink_url, "player", {"playerId": player_id})

    with ThreadPoolExecutor(max_workers=max(1, min(args.workers, 10))) as pool:
        futures = {pool.submit(fetch_member, pid): pid for pid in remaining}
        for future in as_completed(futures):
            pid = futures[future]
            try:
                player = future.result()
                if not player.get("rosterUnit"):
                    raise RuntimeError("profile response has no rosterUnit")
                players.append(normalize_player(player, pid))
                print(f"OK {len(players)}/{len(player_ids)}: {player.get('name', pid)}")
            except Exception as exc:
                failures.append({"player_id": pid, "error": str(exc)})
                print(f"FAILED {pid}: {exc}", file=sys.stderr)

    # Require a complete import; a partial guild would produce misleading assignments.
    if failures or len(players) != len(player_ids):
        print(f"Import incomplete: {len(players)}/{len(player_ids)} profiles; {len(failures)} failures.", file=sys.stderr)
        print("No output file written. Retry the workflow to avoid planning from incomplete data.", file=sys.stderr)
        return 2

    output = {
        "schema_version": 1,
        "imported_at": datetime.now(timezone.utc).isoformat(),
        "guild": {
            "guild_id": guild_id,
            "name": (guild.get("profile") or {}).get("name") or guild.get("name") or seed.get("guildName") or "",
            "member_count": len(player_ids),
        },
        "source": {"service": "SWGOH Comlink", "seed_player_id": seed_player_id},
        "members": sorted(players, key=lambda p: (p["name"].casefold(), p["player_id"] or "")),
        "import_complete": True,
    }
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Complete guild import: {len(players)} members; saved {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
