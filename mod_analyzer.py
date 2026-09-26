"""
SWGOH mod analyzer.
Input: mods.csv from generate_mods.py
Output: mod_analysis.csv and mod_analysis.md
"""

import csv
import json
import os

INPUT_FILE = "mods.csv"
OUTPUT_CSV = "mod_analysis.csv"
OUTPUT_MD = "mod_analysis.md"
PROFILE_FILE = "mod_profiles.json"
ANALYZER_VERSION = "2026-09-26-fast-global-chain-optimization"

R5 = {
    "Critical Chance %": (1.125, 2.25), "Defense": (4.9, 9.8),
    "Defense %": (0.85, 1.70), "Health": (214.3, 428.6),
    "Health %": (0.563, 1.125), "Offense": (22.8, 45.6),
    "Offense %": (0.281, 0.563), "Potency %": (1.125, 2.25),
    "Protection": (415.3, 830.6), "Protection %": (1.125, 2.25),
    "Speed": (3.0, 6.0), "Tenacity %": (1.125, 2.25),
}
R6 = {
    "Critical Chance %": (1.175, 2.35), "Defense": (8.0, 16.0),
    "Defense %": (2.0, 4.0), "Health": (270.0, 540.0),
    "Health %": (1.0, 2.0), "Offense": (25.0, 50.0),
    "Offense %": (0.85, 1.70), "Potency %": (1.5, 3.0),
    "Protection": (460.0, 920.0), "Protection %": (1.5, 3.0),
    "Speed": (3.0, 6.0), "Tenacity %": (1.5, 3.0),
}
TOTAL = {(5,1):4,(5,2):5,(5,3):6,(5,4):7,(5,5):8,
         (6,1):8,(6,2):9,(6,3):10,(6,4):11,(6,5):12}
TIER = {1:"E",2:"D",3:"C",4:"B",5:"A"}

STAT_VALUE = {
    "Speed": 1.00, "Offense %": 0.92, "Offense": 0.82,
    "Health %": 0.72, "Protection %": 0.70, "Health": 0.48,
    "Protection": 0.48, "Defense %": 0.42, "Defense": 0.34,
    "Potency %": 0.34, "Tenacity %": 0.30,
    "Critical Chance %": 0.25, "Critical Damage %": 0.25,
    "Critical Avoidance %": 0.20, "Speed %": 0.15,
}
CAL_ATTEMPTS = {(6,1):1,(6,2):2,(6,3):3,(6,4):4,(6,5):6}
CAL_COST = {1:15,2:25,3:40,4:75,5:100,6:150}

def is_true(value):
    return str(value).strip().lower() in {"1", "true", "yes", "y"}

def integer(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

def number(value, default=0.0):
    try:
        return float(str(value).replace("%",""))
    except (TypeError, ValueError):
        return default

def rolls(row, i):
    stat = row.get("secondary{}Stat".format(i), "").strip()
    if not stat:
        return None
    count = integer(row.get("secondary{}Rolls".format(i), ""))
    value = number(row.get("secondary{}Value".format(i), ""))
    raw = row.get("secondary{}RawRolls".format(i), "")
    values = []
    for item in raw.split("|"):
        if not item:
            continue
        try:
            raw_value = float(item)
        except ValueError:
            continue
        if stat in {"Health","Protection","Offense","Defense","Speed"}:
            values.append(raw_value / 10000.0)
        else:
            values.append(raw_value / 100.0)
    if not values and count:
        values = [value / count] * count
    return stat, value, count, values

def quality(stat, value, count, values, dots):
    if not count:
        return 0.0
    low_high = (R6 if dots >= 6 else R5).get(stat)
    if not low_high:
        return 0.0
    low, high = low_high
    if values:
        q = [max(0.0, min(1.0, (v-low)/(high-low))) for v in values]
        return sum(q) / len(q)
    per = value / count
    return max(0.0, min(1.0, (per-low)/(high-low)))

def roll_value(stat, value, count, values, dots):
    return quality(stat, value, count, values, dots) * STAT_VALUE.get(stat, 0.10)

def projected_6e_quality(secs):
    if not secs:
        return 0.0
    weighted = 0.0
    total = 0
    for stat, value, count, values in secs:
        if count <= 0:
            continue
        r5 = R5.get(stat)
        r6 = R6.get(stat)
        if not r5 or not r6:
            continue
        projected_value = value * (r6[1] / r5[1])
        low6, high6 = r6
        per_roll = projected_value / count
        q = max(0.0, min(1.0, (per_roll-low6)/(high6-low6)))
        weighted += q * count
        total += count
    return 100.0 * weighted / total if total else 0.0

def quality_metrics(secs, dots):
    total = sum(x[2] for x in secs)
    if not total:
        return 0.0, 0.0
    quality_pct = 100.0 * sum(quality(*x, dots) * x[2] for x in secs) / total
    value_pct = 100.0 * sum(roll_value(*x, dots) * x[2] for x in secs) / total
    return quality_pct, value_pct

def best_future_roll(sec_stats, dots):
    if not sec_stats:
        return 0.0
    return max(STAT_VALUE.get(x[0], 0.10) for x in sec_stats)

def investment(row):
    dots = integer(row.get("dots"))
    tier = integer(row.get("tier"))
    level = integer(row.get("level"))
    if level < 15:
        return "upgrade"
    if dots == 5 and tier < 5:
        return "slice"
    if dots == 5 and tier == 5:
        return "6-dot"
    if dots == 6 and tier < 5:
        return "slice"
    if dots == 6 and tier == 5:
        return "calibration"
    return "none"

def next_action(row, secs, current_quality, current_value, potential, fit_score=0.0):
    dots = integer(row.get("dots"))
    tier = integer(row.get("tier"))
    level = integer(row.get("level"))
    speed = next((x for x in secs if x[0] == "Speed"), None)
    speed_rolls = speed[2] if speed else 0

    if level < 12:
        return ("UPGRADE", "nieujawnione wszystkie secondary")

    if level < 15:
        if current_value >= 35 or speed or fit_score >= 70:
            return ("UPGRADE", "dokończenie do 15 ma dodatnią wartość dla jakości lub profilu postaci")
        return ("KEEP", "zbyt słaby profil przed 15")

    if dots == 5 and tier < 5:
        if speed_rolls >= 2 or fit_score >= 70 or (current_value >= 43 and potential >= 58):
            return ("SLICE", "wartość moda lub dopasowanie do postaci uzasadnia kolejny roll")
        if current_value >= 35 and potential >= 52:
            return ("KEEP", "obserwuj przed wydaniem materiałów")
        return ("KEEP", "wartość secondary zbyt niska")

    if dots == 5 and tier == 5:
        six_e = projected_6e_quality(secs)
        if speed_rolls >= 2 or fit_score >= 72 or six_e >= 50 or (current_value >= 45 and len(secs) >= 3):
            return ("SLICE_6E", "5A ma wystarczającą wartość lub dopasowanie do postaci")
        return ("KEEP", "5A nie uzasadnia kosztu 6E")

    if dots == 6 and tier < 5:
        if speed_rolls >= 3 or fit_score >= 72 or (current_value >= 52 and potential >= 65):
            return ("SLICE", "6-dot ma dobry profil do kolejnego rolla")
        return ("KEEP", "brak wystarczającej wartości do kolejnego slice")

    if dots == 6 and tier == 5:
        if speed_rolls >= 3 or fit_score >= 75 or current_value >= 58:
            return ("CALIBRATE", "6A ma wartość lub dopasowanie uzasadniające calibration")
        return ("KEEP", "6A nie wymaga obecnie inwestycji")

    return ("KEEP", "brak dalszej inwestycji")

def analyze(row):
    dots = integer(row.get("dots"))
    tier = integer(row.get("tier"))
    secs = [x for i in range(1, 5) if (x := rolls(row, i)) is not None]
    total = sum(x[2] for x in secs)
    current_quality, current_value = quality_metrics(secs, dots)
    target_total = TOTAL.get((dots, tier), total)
    remaining = max(0, target_total-total)

    best_weight = best_future_roll(secs, dots)
    future_value = (current_value / 100.0) * total + remaining * best_weight
    potential_value = 100.0 * future_value / max(1, total + remaining)

    calibration_max = CAL_ATTEMPTS.get((dots, tier), 0)
    calibration_used = integer(row.get("rerolledCount"))
    calibration_remaining = max(0, calibration_max-calibration_used)
    calibration_next_cost = CAL_COST.get(calibration_used+1, 0) if calibration_remaining else 0

    six_e_quality = projected_6e_quality(secs) if dots == 5 and tier == 5 else 0.0
    speed = next((x for x in secs if x[0] == "Speed"), None)
    speed_value = speed[1] if speed else 0.0
    speed_rolls = speed[2] if speed else 0
    speed_quality = min(100.0, 100.0*speed_value/(6.0*speed_rolls)) if speed_rolls else 0.0

    out = dict(row)
    out.update({
        "tierName": TIER.get(tier, "?"),
        "secondaryRollsTotal": total,
        "secondaryRollsMaxAtTier": target_total,
        "secondaryRollsRemainingAtTier": remaining,
        "modQuality": round(current_quality, 1),
        "modValue": round(current_value, 1),
        "speedQuality": round(speed_quality, 1),
        "potentialCeiling": round(potential_value, 1),
        "potentialGain": round(max(0, potential_value-current_value), 1),
        "projected6EQuality": round(six_e_quality, 1),
        "nextInvestment": investment(row),
        "calibrationAttemptsMax": calibration_max,
        "calibrationAttemptsUsed": calibration_used,
        "calibrationAttemptsRemaining": calibration_remaining,
        "calibrationNextCost": calibration_next_cost,
    })
    return out

def load_targets():
    if not os.path.exists("targets.json"):
        return []
    try:
        with open("targets.json", encoding="utf-8") as f:
            return json.load(f).get("targets", [])
    except Exception:
        return []

def load_profiles():
    if not os.path.exists(PROFILE_FILE):
        return {}
    try:
        with open(PROFILE_FILE, encoding="utf-8") as f:
            return json.load(f).get("profiles", {})
    except Exception:
        return {}


def load_player_aliases():
    aliases = {}

    # Prefer the generated roster.csv because it is built directly from
    # player rosterUnit and is guaranteed to contain unit-id -> baseId mapping.
    roster_path = "roster.csv"
    if os.path.exists(roster_path):
        try:
            with open(roster_path, newline="", encoding="utf-8-sig") as f:
                for item in csv.DictReader(f):
                    base_id = str(item.get("baseId", "") or "")
                    definition = str(item.get("definitionId", "") or "")
                    unit_id = str(item.get("id", "") or "")
                    if not base_id and definition:
                        base_id = definition.split(":", 1)[0]
                    if base_id:
                        for value in (base_id, unit_id, definition):
                            if value:
                                aliases[value] = base_id
        except Exception:
            pass

    # Also accept the raw player snapshot when available.
    path = "swgoh_972824625.json"
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                player = json.load(f)
            for unit in player.get("rosterUnit", []):
                definition = str(unit.get("definitionId", "") or "")
                base_id = definition.split(":", 1)[0]
                unit_id = str(unit.get("id", "") or "")
                if base_id:
                    for value in (base_id, unit_id, definition):
                        if value:
                            aliases[value] = base_id
        except Exception:
            pass

    return aliases

def load_player_names():
    names = {}
    roster_path = "roster.csv"
    if os.path.exists(roster_path):
        try:
            with open(roster_path, newline="", encoding="utf-8-sig") as f:
                for item in csv.DictReader(f):
                    name = str(item.get("name", "") or "").strip()
                    base_id = str(item.get("baseId", "") or "").strip()
                    definition = str(item.get("definitionId", "") or "").strip()
                    unit_id = str(item.get("id", "") or "").strip()
                    if base_id and name:
                        names[base_id] = name
                    for value in (unit_id, definition):
                        if value and name:
                            names[value] = name
        except Exception:
            pass
    return names

def source_label(row, aliases, names):
    if not is_true(row.get("equipped")):
        return "MAGAZYN"
    assigned = str(row.get("assignedTo", "") or "").strip()
    base_id = aliases.get(assigned, assigned)
    name = names.get(assigned) or names.get(base_id)
    if name:
        return "POSTAĆ: " + name
    if base_id:
        return "POSTAĆ: " + base_id
    return "POSTAĆ: nieznana"


def score_profile(row, profile):
    primary = row.get("primaryStat", "")
    slot = row.get("slot", "")
    primary_pref = profile.get("primary_preferences", {}).get(slot, {})
    primary_fit = float(primary_pref.get(primary, 0.0)) * 100.0

    secs = []
    for i in range(1, 5):
        x = rolls(row, i)
        if x is not None:
            stat, value, count, values = x
            q = quality(stat, value, count, values, integer(row.get("dots")))
            pref = float(profile.get("secondary_preferences", {}).get(stat, 0.0))
            secs.append((q, pref, count))

    # q is already normalized to 0..1. Convert to 0..100 only once
    # after weighting; the previous version multiplied by 100 twice.
    weighted = sum(q * pref * max(1, count) for q, pref, count in secs)
    max_weight = sum(max(1, count) for q, pref, count in secs) or 1
    secondary_fit = 100.0 * weighted / max_weight
    set_name = row.get("set", "")
    set_fit = float(profile.get("set_preferences", {}).get(set_name, 0.0)) * 100.0

    fit_score = 0.20 * primary_fit + 0.15 * set_fit + 0.65 * secondary_fit
    return {
        "fitScore": round(fit_score, 1),
        "primaryFit": round(primary_fit, 1),
        "secondaryFit": round(secondary_fit, 1),
        "setFit": round(set_fit, 1)
    }

def character_fit(row, targets, profiles, aliases):
    assigned = row.get("assignedTo", "")
    target_ids = {t.get("baseId") for t in targets}
    assigned_base = aliases.get(assigned, assigned)

    if assigned_base in profiles:
        result = score_profile(row, profiles[assigned_base])
        result["characterFit"] = "TARGET" if assigned_base in target_ids else "PROFILED"
        result["fitTarget"] = assigned_base
        return result

    candidates = [(tid, profiles.get(tid)) for tid in target_ids if profiles.get(tid)]
    if not candidates:
        return {"characterFit": "GENERAL", "fitScore": 0.0, "primaryFit": 0.0, "secondaryFit": 0.0, "setFit": 0.0, "fitTarget": ""}

    best = None
    for tid, profile in candidates:
        result = score_profile(row, profile)
        result["fitTarget"] = tid
        if best is None or result["fitScore"] > best["fitScore"]:
            best = result

    best["characterFit"] = "CANDIDATE"
    return best

def apply_replacements(rows, target_base_ids, profiles=None, aliases=None, names=None):
    """Fast recursive same-slot allocation with bounded candidate search and memoized chains."""
    slots = ("Square", "Diamond", "Circle", "Arrow", "Triangle", "Cross")
    targets = set(target_base_ids)
    profiles = profiles or {}
    aliases = aliases or {}
    names = names or {}

    def rid(r):
        return str(r.get("id", "") or "")

    def base(r):
        owner = str(r.get("assignedTo", "") or "")
        return aliases.get(owner, owner)

    def pname(owner):
        base_id = aliases.get(owner, owner)
        return names.get(owner) or names.get(base_id) or base_id or "nieznana"

    def score(r, who):
        profile = profiles.get(who)
        if profile:
            return float(score_profile(r, profile)["fitScore"])
        return float(r.get("modValue", 0) or 0)

    # Only relevant, fully developed mods participate in exchanges.
    eq = {}
    target = {}
    inventory = {}
    byslot = {}
    for r in rows:
        if integer(r.get("level")) < 15 or integer(r.get("dots")) < 5:
            continue
        slot = str(r.get("slot", "") or "")
        if not slot:
            continue
        if is_true(r.get("equipped")):
            owner = str(r.get("assignedTo", "") or "")
            eq[(owner, slot)] = r
            byslot.setdefault(slot, []).append(r)
            if base(r) in targets:
                target[(base(r), slot)] = r
        else:
            inventory.setdefault(slot, []).append(r)

    # Rank candidates once per owner/slot. A bounded top-K keeps the recursive
    # search fast while preserving the strongest useful alternatives.
    MAX_DEPTH = 8
    MAX_BRANCH = 8
    candidate_cache = {}

    def ranked_candidates(owner, slot, forbidden):
        key = (owner, slot)
        if key not in candidate_cache:
            current = eq.get((owner, slot))
            current_id = rid(current) if current else ""
            who = base(current) if current else owner
            pool = list(inventory.get(slot, [])) + list(byslot.get(slot, []))
            ranked = []
            seen_ids = set()
            for r in pool:
                mod_id = rid(r)
                if not mod_id or mod_id == current_id or mod_id in seen_ids:
                    continue
                if is_true(r.get("equipped")):
                    other_owner = str(r.get("assignedTo", "") or "")
                    if not other_owner or other_owner == owner or base(r) in targets:
                        continue
                seen_ids.add(mod_id)
                ranked.append(r)
            ranked.sort(key=lambda r: score(r, who), reverse=True)
            candidate_cache[key] = ranked[:MAX_BRANCH]
        return [r for r in candidate_cache[key] if rid(r) not in forbidden]

    memo = {}

    def repair(owner, slot, forbidden, seen, depth):
        if depth >= MAX_DEPTH:
            return None
        state = (owner, slot, tuple(sorted(seen)))
        if state in memo:
            cached = memo[state]
            if cached is None:
                return None
            used = {rid(cached["replacement"]), rid(cached["removed"])}
            for step in cached.get("steps", []):
                used.add(rid(step["replacement"]))
                used.add(rid(step["removed"]))
            if used & forbidden:
                return None
            return cached

        current = eq.get((owner, slot))
        if current is None:
            memo[state] = None
            return None
        who = base(current)
        current_score = score(current, who)
        best = None

        for replacement in ranked_candidates(owner, slot, forbidden):
            replacement_id = rid(replacement)
            direct_gain = score(replacement, who) - current_score
            if direct_gain <= -80:
                continue

            step = {
                "owner": owner,
                "name": pname(owner),
                "removed": current,
                "replacement": replacement,
                "gain": direct_gain,
                "steps": []
            }

            if is_true(replacement.get("equipped")):
                next_owner = str(replacement.get("assignedTo", "") or "")
                if not next_owner or next_owner in seen:
                    continue
                next_forbidden = set(forbidden)
                next_forbidden.update((replacement_id, rid(current)))
                sub = repair(next_owner, slot, next_forbidden, seen | {next_owner}, depth + 1)
                if sub is None:
                    continue
                step["steps"] = [sub] + sub.get("steps", [])
                step["gain"] = direct_gain + sub["gain"]

            if best is None or step["gain"] > best["gain"]:
                best = step

        memo[state] = best
        return best

    def flatten(step):
        if not step:
            return []
        out = [{
            "owner": step["owner"],
            "name": step["name"],
            "removed": step["removed"],
            "replacement": step["replacement"],
            "gain": step["gain"]
        }]
        child = step.get("steps", [])
        if child:
            out.extend(flatten(child[0]))
        return out

    proposals = []
    for target_id in targets:
        for slot in slots:
            current = target.get((target_id, slot))
            current_score = score(current, target_id) if current else 0.0
            pool = list(inventory.get(slot, [])) + list(byslot.get(slot, []))

            # Direct inventory and equipped candidates are ranked by target gain.
            candidates = []
            seen_ids = set()
            for replacement in pool:
                mod_id = rid(replacement)
                if not mod_id or mod_id in seen_ids:
                    continue
                if current and mod_id == rid(current):
                    continue
                if is_true(replacement.get("equipped")) and base(replacement) in targets:
                    continue
                seen_ids.add(mod_id)
                candidates.append(replacement)
            candidates.sort(key=lambda r: score(r, target_id) - current_score, reverse=True)

            for replacement in candidates[:MAX_BRANCH]:
                target_gain = score(replacement, target_id) - current_score
                if current is not None and target_gain < 8:
                    continue
                if current is None and target_gain <= 0:
                    continue

                if not is_true(replacement.get("equipped")):
                    proposals.append({
                        "t": target_id, "s": slot, "r": replacement, "cur": current,
                        "tg": target_gain, "ag": target_gain, "steps": []
                    })
                    continue

                owner = str(replacement.get("assignedTo", "") or "")
                if not owner or eq.get((owner, slot)) is None:
                    continue
                chain = repair(owner, slot, {rid(replacement), rid(current) if current else ""}, {owner}, 0)
                if chain is None:
                    continue
                steps = flatten(chain)
                account_gain = target_gain + float(chain["gain"])
                # The first step is the source mod being moved to the target.
                # Subsequent steps are the repairs needed for the source chain.
                if account_gain <= 0:
                    continue
                proposals.append({
                    "t": target_id, "s": slot, "r": replacement, "cur": current,
                    "tg": target_gain, "ag": account_gain, "steps": steps
                })

    proposals.sort(key=lambda p: (p["ag"], p["tg"]), reverse=True)
    used_ids = set()
    used_target_slots = set()

    for proposal in proposals:
        target_slot = (proposal["t"], proposal["s"])
        if target_slot in used_target_slots:
            continue

        physical_ids = {rid(proposal["r"])}
        for step in proposal["steps"]:
            physical_ids.add(rid(step["removed"]))
            physical_ids.add(rid(step["replacement"]))
        physical_ids.discard("")
        if physical_ids & used_ids:
            continue

        used_target_slots.add(target_slot)
        used_ids.update(physical_ids)

        replacement = proposal["r"]
        replacement["replacementGain"] = round(proposal["tg"], 1)
        replacement["accountGain"] = round(proposal["ag"], 1)
        replacement["sourceLoss"] = round(max(0.0, proposal["tg"] - proposal["ag"]), 1)
        replacement["chainLength"] = 1 + len(proposal["steps"])
        replacement["chainId"] = "{}:{}".format(proposal["t"], proposal["s"])
        path = [proposal["t"]]
        for step in proposal["steps"]:
            path.append(step["name"])
        if proposal["steps"]:
            terminal = proposal["steps"][-1]["replacement"]
            if not is_true(terminal.get("equipped")):
                path.append("MAGAZYN")
        replacement["chainPath"] = " <- ".join(path)
        replacement["replacesModId"] = rid(proposal["cur"]) if proposal["cur"] else ""
        replacement["recommendedAction"] = "EQUIP" if proposal["cur"] is None else "REPLACE"
        replacement["reason"] = (
            "pełny łańcuch: {}; zysk celu +{:.1f}, bilans +{:.1f}"
        ).format(replacement["chainPath"], proposal["tg"], proposal["ag"])

        # Mark every source repair as PATCH. Inventory terminal remains the
        # actual hole-filler; it is not separately counted as another action.
        for index, step in enumerate(proposal["steps"], 1):
            patch = step["replacement"]
            patch["recommendedAction"] = "PATCH"
            patch["patchOwner"] = step["owner"]
            patch["patchOwnerName"] = step["name"]
            patch["patchSlot"] = proposal["s"]
            patch["accountGain"] = round(proposal["ag"], 1)
            patch["sourceLoss"] = round(max(0.0, -float(step["gain"])), 1)
            patch["chainLength"] = replacement["chainLength"]
            patch["chainStep"] = index
            patch["chainId"] = replacement["chainId"]
            patch["chainPath"] = replacement["chainPath"]
            patch["replacementGain"] = round(float(step["gain"]), 1)
            patch["replacesModId"] = rid(step["removed"])
            patch["reason"] = (
                "PATCH {} w łańcuchu {}; lokalna zmiana {:+.1f}, bilans +{:.1f}"
            ).format(step["name"], replacement["chainPath"], step["gain"], proposal["ag"])


def main():
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(INPUT_FILE)

    with open(INPUT_FILE, newline="", encoding="utf-8-sig") as f:
        source = list(csv.DictReader(f))
    if not source:
        raise RuntimeError("mods.csv jest pusty.")

    targets = load_targets()
    profiles = load_profiles()
    aliases = load_player_aliases()
    names = load_player_names()
    rows = [analyze(row) for row in source]

    for row in rows:
        fit = character_fit(row, targets, profiles, aliases)
        row.update(fit)
        secs = [x for i in range(1, 5) if (x := rolls(row, i)) is not None]
        action, reason = next_action(
            row, secs, float(row["modQuality"]), float(row["modValue"]),
            float(row["potentialCeiling"]), float(row.get("fitScore", 0.0))
        )
        row["recommendedAction"] = action
        row["reason"] = reason
        row["replacementGain"] = 0.0
        row["replacesModId"] = ""
        row["source"] = source_label(row, aliases, names)

    apply_replacements(rows, {t.get("baseId") for t in targets}, profiles, aliases, names)

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        fields = list(rows[0].keys())
        for row in rows[1:]:
            for key in row.keys():
                if key not in fields:
                    fields.append(key)
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    order = {"REPLACE":0,"EQUIP":1,"PATCH":2,"CALIBRATE":3,"SLICE_6E":4,"SLICE":5,"UPGRADE":6,"KEEP":7}
    rows.sort(key=lambda r: (
        order.get(r["recommendedAction"], 9),
        -float(r.get("fitScore", 0)),
        -float(r["potentialCeiling"]),
        -float(r["modQuality"])
    ))

    counts = {}
    for r in rows:
        counts[r["recommendedAction"]] = counts.get(r["recommendedAction"], 0) + 1

    lines = [
        "# Analiza modów", "",
        "Model rozdziela **jakość obecnych rolli**, **potencjał dalszego rozwoju**, "
        "**dopasowanie do postaci** i **rodzaj następnej inwestycji**.", "",
        "- Modów: **{}**".format(len(rows)),
        "- UPGRADE: **{}**".format(counts.get("UPGRADE",0)),
        "- SLICE: **{}**".format(counts.get("SLICE",0)),
        "- SLICE_6E: **{}**".format(counts.get("SLICE_6E",0)),
        "- CALIBRATE: **{}**".format(counts.get("CALIBRATE",0)),
        "- EQUIP: **{}**".format(counts.get("EQUIP",0)),
        "- REPLACE: **{}**".format(counts.get("REPLACE",0)),
        "- PATCH: **{}**".format(counts.get("PATCH",0)),
        "- KEEP: **{}**".format(counts.get("KEEP",0)), "",
        "## Najważniejsi kandydaci", "",
        "| Akcja | Mod | Źródło | Set | Tier | Lvl | Quality | Value | Fit | 6E proj. | Speed | Potencjał | Inwestycja |",
        "|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|"
    ]

    for r in rows[:75]:
        mod = "{} {} {}".format(r["slot"], r["primaryStat"], r["primaryValue"])
        lines.append(
            "| {} | {} | {} | {} | {}{} | {} | {:.1f}% | {:.1f}% | {:.1f}% | {:.1f}% | {:.1f}% | {:.1f}% | {} |".format(
                r["recommendedAction"], mod, r["source"], r["set"], r["dots"], r["tierName"],
                r["level"], float(r["modQuality"]), float(r["modValue"]),
                float(r.get("fitScore",0)), float(r["projected6EQuality"]),
                float(r["speedQuality"]), float(r["potentialCeiling"]), r["nextInvestment"]
            )
        )

    jar_rows = [r for r in rows if r.get("fitTarget") == "JARJARBINKS"]
    jar_rows.sort(key=lambda r: (
        0 if r.get("recommendedAction") == "REPLACE" else 1,
        -float(r.get("fitScore", 0)),
        -float(r.get("modValue", 0))
    ))
    lines += [
        "", "## Jar Jar Binks — kandydaci", "",
        "Analiza porównuje mody wyposażone z kandydatami z inventory dla każdego slotu.",
        "",
        "| Akcja | Mod | Źródło | Slot | Set | Tier | Lvl | Fit | Zysk celu | Bilans konta | Łańcuch |",
        "|---|---|---|---|---|---|---:|---:|---:|---:|---:|"
    ]
    for r in jar_rows[:18]:
        mod = "{} {} {}".format(r["slot"], r["primaryStat"], r["primaryValue"])
        lines.append(
            "| {} | {} | {} | {} | {} | {}{} | {} | {:.1f}% | {:.1f} | {:.1f} | {} |".format(
                r["recommendedAction"], mod, r["source"], r["slot"], r["set"],
                r["dots"], r["tierName"], r["level"],
                float(r.get("fitScore", 0)),
                float(r.get("replacementGain", 0)),
                float(r.get("accountGain", 0)),
                r.get("chainLength", 0)
            )
        )

    lines += [
        "", "## Definicje", "",
        "- **Quality** — jakość wykonanych rolli względem zakresu dla 5-dot/6-dot.",
        "- **Value** — jakość rolla pomnożona przez ogólną, niezależną od postaci użyteczność statystyki.",
        "- **Fit** — dopasowanie moda do aktywnego profilu celu; obecnie szczegółowy profil ma Jar Jar Binks.",
        "- **AccountGain** — bilans całej operacji przeniesienia i PATCH-a dla źródła; dla źródeł bez profilu używany jest globalny ModValue.",
        "- **Potential** — sufit wartości przy idealnych przyszłych rollach; nie jest prognozą RNG.",
        "- **Źródło MAGAZYN** — mod nie jest obecnie założony na żadnej postaci.",
        "- **Źródło POSTAĆ: [nazwa]** — mod jest obecnie założony na wskazanej postaci.",
        "- **EQUIP** — pusty slot celu; mod jest przydzielany tylko wtedy, gdy bilans całej operacji dla konta jest dodatni.",
        "- **PATCH** — mod z magazynu, który bezpośrednio zastępuje mod zabrany z innej postaci.",
        "- **REPLACE** — mod jest przenoszony do celu tylko wtedy, gdy poprawa celu i uwzględniona strata źródłowej postaci dają dodatni bilans dla konta.",
        "- **AccountGain** — zysk celu minus strata wartości źródłowej postaci; dzięki temu mod nie jest zabierany, jeśli operacja pogarsza cały roster. Dla postaci bez profilu strata jest liczona przez globalny ModValue.",
        "- **UPGRADE** — mod nie jest jeszcze na 15.",
        "- **SLICE** — kolejny tier ma uzasadnienie jakościowe lub profilowe.",
        "- **SLICE_6E** — 5A jest oceniane również przez projekcję jakości po wzroście statystyk do 6E.",
        "- **CALIBRATE** — 6A jest na końcu slicing i może korzystać z calibration.",
        "",
        "Calibration pozostaje losowe: wybrany roll jest usuwany z wybranego secondary, "
        "a nowy roll trafia losowo do dostępnych secondary. Analyzer wskazuje kandydatów, "
        "ale nie udaje, że zna wynik konkretnej próby."
    ]

    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print("="*80)
    print("SWGOH MOD ANALYZER")
    print("="*80)
    print("Modów:", len(rows))
    for action in ("EQUIP","REPLACE","PATCH","UPGRADE","SLICE","SLICE_6E","CALIBRATE","KEEP"):
        print("{:<12}: {}".format(action, counts.get(action,0)))
    print("CSV:", OUTPUT_CSV)
    print("REPORT:", OUTPUT_MD)

if __name__ == "__main__":
    main()
