"""
SWGOH mod analyzer.
Input: mods.csv from generate_mods.py
Output: mod_analysis.csv and mod_analysis.md
"""

import argparse
import csv
import json
import os

from update_mod_profiles import ensure_profiles

INPUT_FILE = "mods.csv"
OUTPUT_CSV = "mod_analysis.csv"
OUTPUT_MD = "mod_analysis.md"
PROFILE_FILE = "mod_profiles.json"
ANALYZER_VERSION = "2026-11-12-profile-combo-weighted-v1"

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

SET_RULES = {
    "Critical Chance": ("Critical Chance %", 2, 4.0, 8.0),
    "Critical Damage": ("Critical Damage %", 4, 15.0, 30.0),
    "Defense": ("Defense %", 2, 12.5, 25.0),
    "Health": ("Health %", 2, 5.0, 10.0),
    "Offense": ("Offense %", 4, 7.5, 15.0),
    "Potency": ("Potency %", 2, 7.5, 15.0),
    "Speed": ("Speed", 4, 5.0, 10.0),
    "Tenacity": ("Tenacity %", 2, 10.0, 20.0),
}

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

def _normalize_set_name(name):
    aliases = {"Crit Damage": "Critical Damage", "Crit Chance": "Critical Chance"}
    value = str(name or "").strip()
    return aliases.get(value, value)


def profile_set_preference(profile, set_name):
    """Read set preference using canonical game names and SWGOH.GG aliases."""
    canonical = _normalize_set_name(set_name)
    preferences = profile.get("set_preferences", {}) or {}
    values = []
    for raw_name, raw_value in preferences.items():
        if _normalize_set_name(raw_name) != canonical:
            continue
        try:
            values.append(max(0.0, float(raw_value or 0.0)))
        except (TypeError, ValueError):
            continue
    return max(values, default=0.0)


def _canonical_set_combo_from_counts(counts):
    if sum(int(value) for value in counts.values()) != 6:
        return None
    tokens = []
    for raw_name, raw_count in counts.items():
        name = _normalize_set_name(raw_name)
        rule = SET_RULES.get(name)
        if not rule:
            return None
        required, count = int(rule[1]), int(raw_count)
        if required <= 0 or count % required:
            return None
        groups = count // required
        if groups not in (1, 2, 3):
            return None
        prefix = "" if groups == 1 else ("Double " if groups == 2 else "Triple ")
        tokens.append((-count, name, prefix + name))
    return " + ".join(label for _groups, _name, label in sorted(tokens))



def canonical_set_combo_from_mods(mods):
    counts = {}
    for mod in mods or []:
        name = _normalize_set_name(mod.get("set", ""))
        if not name or name not in SET_RULES:
            return None
        counts[name] = counts.get(name, 0) + 1
    return _canonical_set_combo_from_counts(counts)



def _canonical_set_combo_from_profile_label(label):
    counts = {}
    for raw_token in str(label or "").split("+"):
        token = raw_token.strip()
        groups = 1
        for prefix, multiplier in (("Double ", 2), ("Triple ", 3)):
            if token.startswith(prefix):
                token = token[len(prefix):].strip()
                groups = multiplier
                break
        name = _normalize_set_name(token)
        rule = SET_RULES.get(name)
        if not rule:
            return None
        counts[name] = counts.get(name, 0) + groups * int(rule[1])
    return _canonical_set_combo_from_counts(counts)



def profile_set_combo_match(profile, mods):
    """Exact observed combo frequency, normalized to the most common combo."""
    target_key = canonical_set_combo_from_mods(mods)
    combinations = profile.get("set_combinations", {}) or {}
    if not target_key or not isinstance(combinations, dict) or not combinations:
        return None
    frequencies = {}
    for label, raw_frequency in combinations.items():
        key = _canonical_set_combo_from_profile_label(label)
        if not key:
            continue
        try:
            frequency = max(0.0, float(raw_frequency or 0.0))
        except (TypeError, ValueError):
            continue
        frequencies[key] = frequencies.get(key, 0.0) + frequency
    if target_key not in frequencies:
        return None
    maximum = max(frequencies.values(), default=0.0)
    if maximum <= 0:
        return None
    frequency = frequencies[target_key]
    return {"key": target_key, "frequency": round(frequency, 4),
            "preference": round(frequency / maximum, 6)}


def profile_set_combo_alignment_score(profile, mods):
    """Bounded score for how closely a complete build matches observed set combos."""
    match = profile_set_combo_match(profile, mods)
    if not match:
        return 0.0, None
    score = float(match.get("preference", 0.0)) * PROFILE_COMBO_ALIGNMENT_POINTS
    return score, match



def append_donor_combo_report(lines, validation, affected_owners):
    """Append the exact donor set-combination audit used by the Markdown report."""
    lines += ["", "### Dokładna kombinacja setów dawców", "",
              "| Postać | Przed | Częstość | Po | Częstość |",
              "|---|---|---:|---|---:|"]
    for item in validation:
        if item.get("owner") not in affected_owners:
            continue
        before_key = item.get("beforeComboKey") or "brak w profilu"
        after_key = item.get("afterComboKey") or "brak w profilu"
        before_freq = item.get("beforeComboFrequency")
        after_freq = item.get("afterComboFrequency")
        before_pct = "—" if before_freq is None else "{:.1f}%".format(float(before_freq))
        after_pct = "—" if after_freq is None else "{:.1f}%".format(float(after_freq))
        lines.append("| {} | {} | {} | {} | {} |".format(
            item["name"], before_key, before_pct, after_key, after_pct))
    if not affected_owners:
        lines.append("| — | — | — | — | — |")
    return lines


def mod_description(row):
    """Human-searchable mod identification; never relies on the current owner."""
    secondary = []
    for i in range(1, 5):
        stat = str(row.get("secondary{}Stat".format(i), "") or "").strip()
        value = str(row.get("secondary{}Value".format(i), "") or "").strip()
        if stat:
            secondary.append("{} {}".format(stat, value))
    return "{} / {} / {} {} / secondary: {} / {}★ {} lvl{}".format(
        row.get("slot",""),
        row.get("set",""),
        row.get("primaryStat",""),
        row.get("primaryValue",""),
        ", ".join(secondary) if secondary else "brak",
        row.get("dots",""),
        row.get("tierName",""),
        row.get("level","")
    )

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

def load_targets(target_overrides=None):
    """Load mod-analysis targets without mutating the shared farming targets.json.

    Explicit CLI targets replace the targets used by the mod analyzer only.
    With no override, preserve the existing targets.json behavior.
    """
    if target_overrides:
        target_ids = []
        for value in target_overrides:
            target_ids.extend(
                part.strip().upper()
                for part in str(value or "").split(",")
                if part.strip()
            )
        return [{"baseId": target_id} for target_id in dict.fromkeys(target_ids)]

    if not os.path.exists("targets.json"):
        return []
    try:
        with open("targets.json", encoding="utf-8") as f:
            return json.load(f).get("targets", [])
    except Exception:
        return []

PROTECTED_OWNERS_FILE = "protected_owners.json"

# Account-level donor exclusions from MOD_OPTIMIZATION_RULES.md.
# These are mandatory policy constraints, separate from the user-editable list.
MANDATORY_PROTECTED_DONOR_BASE_IDS = {
    "JARJARBINKS",
    "GRANDINQUISITOR",
    "SECONDSISTER",
    "THIRDSISTER",
    "FIFTHBROTHER",
    "SEVENTHSISTER",
    "EIGHTHBROTHER",
    "NINTHSISTER",
    "GRANDMOFFTARKIN",
    "HONDO",
}

def load_protected_owners():
    configured = set()
    if os.path.exists(PROTECTED_OWNERS_FILE):
        try:
            with open(PROTECTED_OWNERS_FILE, encoding="utf-8") as f:
                data = json.load(f)
            configured = {
                str(x).strip() for x in data.get("protectedOwners", [])
                if str(x).strip()
            }
        except Exception:
            configured = set()
    return configured | MANDATORY_PROTECTED_DONOR_BASE_IDS

def load_profiles():
    if not os.path.exists(PROFILE_FILE):
        return {}
    try:
        with open(PROFILE_FILE, encoding="utf-8") as f:
            return json.load(f).get("profiles", {})
    except Exception:
        return {}


def merge_profiles(existing, additional):
    """Add newly requested donor profiles without dropping target profiles."""
    merged = dict(existing or {})
    merged.update(additional or {})
    return merged


def unavailable_profile_ids(status):
    """Owners without a cached profile cannot be treated as safe mod donors."""
    return {
        str(base_id) for base_id, result in (status or {}).items()
        if str(result).strip().lower() == "unavailable"
    }


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


PROFILE_PRIMARY_MAX_6DOT = {
    "Offense": 8.50, "Defense": 20.0, "Health": 16.0,
    "Protection": 24.0, "Speed": 32.0, "Accuracy": 30.0,
    "Critical Avoidance": 35.0, "Critical Chance": 20.0,
    "Critical Damage": 42.0, "Potency": 30.0, "Tenacity": 35.0,
}
PROFILE_PRIMARY_POINTS = 40.0
PROFILE_SECONDARY_POINTS = 60
# Exact six-mod set-combination alignment is worth up to 15 points on the
# same 100-point scale: strong enough to distinguish a dominant observed
# profile combo without making it an unconditional hard constraint.
PROFILE_COMBO_ALIGNMENT_POINTS = 15.0
PROFILE_MAX_ROLLS = 24.0


def profile_mod_score_components(row, profile):
    """Shared 40/60 per-mod scoring used by both build search and donor fit."""
    slot = str(row.get("slot", "") or "")
    primary = str(row.get("primaryStat", "") or "")
    primary_pref = max(0.0, min(1.0, float(
        profile.get("primary_preferences", {}).get(slot, {}).get(primary, 0.0)
    )))
    primary_value = number(row.get("primaryValue", 0), 0.0)
    primary_base = primary.replace("%", "").strip()
    primary_ceiling = PROFILE_PRIMARY_MAX_6DOT.get(primary_base, 0.0)
    primary_quality = (
        max(0.0, min(1.0, primary_value / primary_ceiling))
        if primary_ceiling > 0 else 1.0
    )
    primary_fit = primary_pref * primary_quality

    weighted_rolls = 0.0
    for index in range(1, 5):
        stat_data = rolls(row, index)
        if stat_data is None:
            continue
        stat, value, count, values = stat_data
        if count <= 0:
            continue
        q = quality(stat, value, count, values, integer(row.get("dots")))
        pref = max(0.0, float(profile.get("secondary_preferences", {}).get(stat, 0.0)))
        weighted_rolls += q * pref * count

    primary_points = primary_fit * PROFILE_PRIMARY_POINTS / 6.0
    secondary_points = weighted_rolls * PROFILE_SECONDARY_POINTS / PROFILE_MAX_ROLLS
    return {
        "fitScore": primary_points + secondary_points,
        "primaryFit": primary_fit * 100.0,
        "secondaryFit": min(100.0, weighted_rolls * 100.0 / PROFILE_MAX_ROLLS),
        "primaryPoints": primary_points,
        "secondaryPoints": secondary_points,
    }


def score_profile(row, profile):
    components = profile_mod_score_components(row, profile)
    set_name = row.get("set", "")
    set_fit = profile_set_preference(profile, set_name) * 100.0
    # Set bonuses are evaluated only once at complete-build level.
    return {
        "fitScore": round(components["fitScore"], 2),
        "primaryFit": round(components["primaryFit"], 1),
        "secondaryFit": round(components["secondaryFit"], 1),
        "primaryPoints": round(components["primaryPoints"], 2),
        "secondaryPoints": round(components["secondaryPoints"], 2),
        "setFit": round(set_fit, 1),
    }


def profiled_build_score(mods, profile):
    """Score a fixed equipped build with the same mod and set model as the optimizer."""
    base_score = sum(profile_mod_score_components(mod, profile)["fitScore"] for mod in mods)
    grouped = {}
    for mod in mods:
        name = str(mod.get("set", "") or "")
        if name in SET_RULES:
            grouped.setdefault(name, []).append(mod)

    secondary_prefs = profile.get("secondary_preferences", {})
    set_score = 0.0
    set_max_roll = {
        "Critical Chance %": 2.25, "Critical Damage %": 36.0,
        "Defense %": 1.70, "Health %": 1.125, "Offense %": 0.563,
        "Potency %": 2.25, "Speed": 6.0, "Tenacity %": 2.25,
    }
    for name, members in grouped.items():
        stat, required, small_bonus, max_bonus = SET_RULES[name]
        count = len(members)
        full_groups = sum(1 for m in members if integer(m.get("level")) >= 15) // required
        half_groups = (count - full_groups * required) // required
        if not full_groups and not half_groups:
            continue
        set_pref = profile_set_preference(profile, name)
        profile_stat = {
            "Health %": "Health", "Defense %": "Defense",
            "Offense %": "Offense", "Potency %": "Potency",
            "Tenacity %": "Tenacity",
        }.get(stat, stat)
        stat_pref = max(0.0, float(secondary_prefs.get(stat, 0.0)),
                        float(secondary_prefs.get(profile_stat, 0.0)))
        max_roll = R5.get(stat, (0.0, 0.0))[1] or set_max_roll.get(stat)
        # A set explicitly favored by the profile remains valuable even when
        # its bonus stat is not among SWGOH.GG's top secondary-focus stats.
        stat_pref = max(stat_pref, set_pref)
        if not max_roll or not stat_pref:
            continue
        if stat == "Speed":
            base_speed = number(profile.get("base_stats", {}).get("Speed", 150.0), 150.0)
            full_units = max_bonus * base_speed / 100.0
            half_units = small_bonus * base_speed / 100.0
        else:
            full_units, half_units = max_bonus, small_bonus
        equivalents = (full_groups * full_units + half_groups * half_units) / max_roll
        set_weight = 0.10 + 0.90 * min(1.0, set_pref)
        set_score += equivalents * stat_pref * set_weight * PROFILE_SECONDARY_POINTS / PROFILE_MAX_ROLLS
    combo_score, _combo_match = profile_set_combo_alignment_score(profile, mods)
    return base_score + set_score + combo_score


def compare_profiled_builds(before_mods, after_mods, profile):
    """Return a comparable full-build score delta, or None without a profile."""
    if not isinstance(profile, dict) or not profile:
        return None
    before_score = profiled_build_score(before_mods, profile)
    after_score = profiled_build_score(after_mods, profile)
    return {
        "before": round(before_score, 2),
        "after": round(after_score, 2),
        "delta": round(after_score - before_score, 2),
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

    # Set bonuses are percentages of the character's base stat, not
    # secondary-stat rolls.  We therefore value them separately from
    # STAT_VALUE.  For non-speed percentage stats we normalize the set bonus
    # against the maximum 5A secondary roll for the same stat.  Speed uses a
    # 150 base-speed reference (10% = 15 speed), because the roster export
    # does not contain per-character pre-mod base stats.
    SET_REFERENCE_BASE_SPEED = 150.0
    SET_BONUS_MAX_SECONDARY = {
        "Critical Chance %": 2.25,
        "Defense %": 1.70,
        "Health %": 1.125,
        "Offense %": 0.563,
        "Potency %": 2.25,
        "Tenacity %": 2.25,
        "Critical Damage %": 36.0,
    }

    def set_bonus_score(mods):
        # A set bonus is earned by complete groups of the required size.
        # If there are more mods of the same set than one group needs, the
        # strongest (highest-level) mods are the ones that form the complete
        # groups. An extra incomplete mod does not downgrade a complete group.
        total = 0.0
        grouped = {}
        for mod in mods:
            set_name = str(mod.get("set", "") or "")
            if set_name in SET_RULES:
                grouped.setdefault(set_name, []).append(mod)

        for set_name, members in grouped.items():
            stat, required, minimum, maximum = SET_RULES[set_name]
            members = sorted(
                members,
                key=lambda m: integer(m.get("level")),
                reverse=True,
            )

            complete_groups = len(members) // required
            for group_index in range(complete_groups):
                start = group_index * required
                group = members[start:start + required]

                # SWGOH.GG's current mod calculator documents that a set with
                # any mod short of max level receives half the set bonus.
                bonus = (
                    maximum
                    if all(integer(m.get("level")) >= 15 for m in group)
                    else minimum
                )

                if stat == "Speed":
                    effective_units = (bonus / 100.0) * SET_REFERENCE_BASE_SPEED
                    reference_units = 6.0
                else:
                    reference_units = SET_BONUS_MAX_SECONDARY.get(stat)
                    if not reference_units:
                        continue
                    effective_units = bonus / reference_units

                total += effective_units * STAT_VALUE.get(stat, 0.10)

        return total
    def owner_mods(owner):
        return [r for (o, _slot), r in eq.items() if o == owner]

    def set_delta(owner, slot, replacement):
        before = set_bonus_score(owner_mods(owner))
        current = eq.get((owner, slot))
        after_mods = [r for r in owner_mods(owner) if r is not current]
        after_mods.append(replacement)
        return set_bonus_score(after_mods) - before

    # Only relevant, fully developed mods participate in exchanges.
    eq = {}
    target = {}
    target_owner = {}
    inventory = {}
    byslot = {}
    for r in rows:
        slot = str(r.get("slot", "") or "")
        if not slot:
            continue

        # Occupancy must include every equipped mod, even an unfinished
        # low-level mod. Otherwise a partially equipped target is incorrectly
        # reported as having an empty slot and gets an EQUIP instead of a
        # replacement recommendation.
        if is_true(r.get("equipped")):
            owner = str(r.get("assignedTo", "") or "")
            eq[(owner, slot)] = r
            if base(r) in targets:
                target[(base(r), slot)] = r
                target_owner[base(r)] = owner

            # Only mature mods are eligible to be used as replacement/source
            # candidates in the account optimizer.
            if integer(r.get("level")) >= 15 and integer(r.get("dots")) >= 5:
                byslot.setdefault(slot, []).append(r)
        elif integer(r.get("level")) >= 15 and integer(r.get("dots")) >= 5:
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
        state = (owner, slot, tuple(sorted(seen)), tuple(sorted(forbidden)))
        if state in memo:
            return memo[state]

        current = eq.get((owner, slot))
        if current is None:
            memo[state] = None
            return None
        who = base(current)
        current_score = score(current, who)
        best = None

        for replacement in ranked_candidates(owner, slot, forbidden)[:4]:
            replacement_id = rid(replacement)
            direct_gain = (
                score(replacement, who)
                - current_score
                + set_delta(owner, slot, replacement)
            )
            if direct_gain <= -80:
                continue

            step = {
                "owner": owner,
                "name": pname(owner),
                "removed": current,
                "replacement": replacement,
                "gain": direct_gain,
                "total_gain": direct_gain,
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
                step["steps"] = [sub]
                step["total_gain"] = direct_gain + sub["total_gain"]

            if best is None or step["total_gain"] > best["total_gain"]:
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
            # gain is deliberately LOCAL to this PATCH step. total_gain
            # belongs to the nested chain and must not be summed again.
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
                target_gain = (
                    score(replacement, target_id)
                    - current_score
                    + set_delta(target_owner.get(target_id, ""), slot, replacement)
                )
                if current is not None and target_gain < 8:
                    continue
                if current is None and target_gain <= 0:
                    continue

                set_bonus_delta = set_delta(
                    target_owner.get(target_id, ""), slot, replacement
                )
                target_fit_after_set = score(replacement, target_id) + set_bonus_delta

                if not is_true(replacement.get("equipped")):
                    proposals.append({
                        "t": target_id, "s": slot, "r": replacement, "cur": current,
                        "tg": target_gain, "ag": target_gain, "steps": [],
                        "set_bonus_delta": set_bonus_delta,
                        "target_fit_after_set": target_fit_after_set
                    })
                    continue

                owner = str(replacement.get("assignedTo", "") or "")
                if not owner or eq.get((owner, slot)) is None:
                    continue
                chain = repair(owner, slot, {rid(replacement), rid(current) if current else ""}, {owner}, 0)
                if chain is None:
                    continue
                steps = flatten(chain)
                # Target gain plus each PATCH's LOCAL gain. Do not use the
                # nested total_gain here: that would double-count deeper steps.
                account_gain = target_gain + sum(
                    float(step["gain"]) for step in steps
                )
                # The first step is the source mod being moved to the target.
                # Subsequent steps are the repairs needed for the source chain.
                if account_gain <= 0:
                    continue
                proposals.append({
                    "t": target_id, "s": slot, "r": replacement, "cur": current,
                    "tg": target_gain, "ag": account_gain, "steps": steps,
                    "set_bonus_delta": set_bonus_delta,
                    "target_fit_after_set": target_fit_after_set
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
        replacement["setBonusDelta"] = round(proposal.get("set_bonus_delta", 0.0), 2)
        replacement["targetFitAfterSet"] = round(proposal.get("target_fit_after_set", score(replacement, proposal["t"])), 1)
        replacement["sourceLoss"] = round(proposal["tg"] - proposal["ag"], 1)
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
            patch["sourceLoss"] = round(-float(step["gain"]), 1)
            patch["chainLength"] = replacement["chainLength"]
            patch["chainStep"] = index
            patch["chainId"] = replacement["chainId"]
            patch["chainPath"] = replacement["chainPath"]
            patch["replacementGain"] = round(float(step["gain"]), 1)
            patch["replacesModId"] = rid(step["removed"])
            patch["reason"] = (
                "PATCH {} w łańcuchu {}; lokalna zmiana {:+.1f}, bilans +{:.1f}"
            ).format(step["name"], replacement["chainPath"], step["gain"], proposal["ag"])





def apply_optimizer_replacements(rows, optimizer, target_base_ids, profiles=None, aliases=None, names=None, protected_owners=None):
    """Plan physical same-slot mod transfers and report every affected owner's balance."""
    profiles = profiles or {}
    aliases = aliases or {}
    names = names or {}
    targets = set(target_base_ids)
    protected_owners = set(protected_owners or set())

    def rid(r): return str(r.get("id", "") or "") if r else ""
    def owner(r): return str(r.get("assignedTo", "") or "")
    def base(r): return aliases.get(owner(r), owner(r))
    def pname(o): return names.get(o) or names.get(aliases.get(o, o)) or aliases.get(o, o) or "nieznana"
    def fit(r, who):
        profile = profiles.get(who)
        return float(score_profile(r, profile)["fitScore"]) if profile else float(r.get("modValue", 0) or 0)

    def exact_combo_frequency(profile, mods):
        match = profile_set_combo_match(profile or {}, mods)
        return float(match.get("frequency", 0.0)) if match else 0.0
    def set_counts(mods):
        out = {}
        for m in mods:
            s = str(m.get("set", "") or "")
            if s in SET_RULES: out[s] = out.get(s, 0) + 1
        return out

    eq = {}
    working_eq = {}
    inventory = []
    for r in rows:
        slot = str(r.get("slot", "") or "")
        if not slot: continue
        if is_true(r.get("equipped")):
            eq[(owner(r), slot)] = r
        else:
            # Unfinished mods are valid physical candidates too; upgrade cost
            # remains a separate investment from the build-fit score.
            inventory.append(r)

    working_eq = dict(eq)

    def resolve_target_owner(target_id):
        existing = next((o for (o, _slot), r in eq.items() if base(r) == target_id), None)
        if existing:
            return existing
        # aliases includes unit-instance-id -> baseId for the full roster,
        # including characters that currently have no equipped mods.
        return next((
            key for key, value in aliases.items()
            if value == target_id and key != target_id and ":" not in key
        ), None)
    selected_ids = {rid(m) for opt in optimizer.values() for m in opt.get("mods", [])}
    def set_groups(mods):
        counts={}
        for m in mods:
            s=str(m.get("set","") or "")
            if s in SET_RULES:
                counts[s]=counts.get(s,0)+1
        return {s: counts.get(s,0)//SET_RULES[s][1] for s in SET_RULES}

    def completed_set_delta(hole_owner, current, replacement):
        before=[r for (o,_s),r in working_eq.items() if o==hole_owner]
        after=[r for r in before if rid(r)!=rid(current)] + [replacement]
        bg=set_groups(before); ag=set_groups(after)
        return sum(ag[s]-bg[s] for s in SET_RULES)

    def find_chain(selected_mod, target_id, target_owner, target_current, used_ids):
        slot = str(selected_mod.get("slot", "") or "")
        src = owner(selected_mod)
        if not src:
            # Inventory -> target is a direct equip; no source slot needs repair.
            return {"moves": [], "gain": 0.0, "set_delta": 0, "mod_value_delta": 0.0}

        # Exact breadth-first search by chain length. At the first depth with
        # terminal inventory solutions, compare EVERY such solution instead of
        # accepting the first candidate encountered. Longer chains are only
        # considered when no shorter physically executable chain exists.
        queue=[(src,{src},set(selected_ids)|set(used_ids)|{rid(selected_mod)},[],True)]
        candidate_inventory = list(inventory)
        if target_current and rid(target_current) not in selected_ids and rid(target_current) not in used_ids:
            recycled = dict(target_current)
            recycled["equipped"] = "False"
            recycled["assignedTo"] = ""
            candidate_inventory.append(recycled)

        while queue:
            next_queue=[]
            terminal_solutions=[]
            for hole_owner,seen,forbidden,moves,initial_hole in queue:
                current=selected_mod if initial_hole else working_eq.get((hole_owner,slot))
                if current is None:
                    continue
                who=base(current) or hole_owner
                candidates=[]
                for r in candidate_inventory:
                    if rid(r) in forbidden or rid(r) in selected_ids:
                        continue
                    if str(r.get("slot","")) == slot:
                        candidates.append((0,r))
                for (other_owner,other_slot),r in working_eq.items():
                    if other_slot != slot or other_owner == hole_owner or other_owner == target_owner or other_owner in seen:
                        continue
                    if base(r) in protected_owners:
                        continue
                    if rid(r) in forbidden or rid(r) in selected_ids:
                        continue
                    candidates.append((1,r))

                for kind,replacement in candidates:
                    replacement_id=rid(replacement)
                    donor_profile = profiles.get(aliases.get(hole_owner, hole_owner), {}) or {}
                    before_mods = [r for (o, _slot), r in working_eq.items() if o == hole_owner]
                    after_mods = [r for r in before_mods if rid(r) != rid(current)] + [replacement]
                    if donor_profile:
                        # Compare the donor's complete fixed build before/after,
                        # not an isolated mod score. Missing slots remain missing.
                        local_gain = profiled_build_score(after_mods, donor_profile) - profiled_build_score(before_mods, donor_profile)
                    else:
                        local_gain = fit(replacement,who)-fit(current,who)
                    set_delta=completed_set_delta(hole_owner,current,replacement)
                    combo_delta = exact_combo_frequency(donor_profile, after_mods) - exact_combo_frequency(donor_profile, before_mods)
                    move={"owner":hole_owner,"name":pname(hole_owner),
                          "removed":None if initial_hole else current,
                          "replacement":replacement,"gain":local_gain,
                          "set_delta":set_delta,"combo_delta":combo_delta}
                    new_moves=moves+[move]
                    next_forbidden=forbidden|{rid(current),replacement_id}
                    if kind==0:
                        mod_value_delta=0.0
                        for item in new_moves:
                            removed=item.get("removed")
                            removed_value=(float(removed.get("modValue",0) or 0)
                                           if removed else float(selected_mod.get("modValue",0) or 0))
                            mod_value_delta += float(item["replacement"].get("modValue",0) or 0)-removed_value
                        terminal_solutions.append({
                            "moves":new_moves,
                            "gain":sum(x["gain"] for x in new_moves),
                            "combo_delta":sum(x.get("combo_delta", 0.0) for x in new_moves),
                            "set_delta":sum(x["set_delta"] for x in new_moves),
                            "mod_value_delta":mod_value_delta
                        })
                    else:
                        next_owner=owner(replacement)
                        if next_owner and next_owner not in seen:
                            next_queue.append((
                                next_owner,
                                seen|{next_owner},
                                next_forbidden,
                                new_moves,False
                            ))
            if terminal_solutions:
                # Lexicographic objective: shortest executable chain (BFS layer),
                # then preserve the donor exact set-combination frequency,
                # followed by donor profile-fit gain, set transition, and modValue.
                # Exact combo preservation is a preference, not a hard constraint.
                terminal_solutions.sort(key=lambda solution: (
                    solution.get("combo_delta", 0.0),
                    solution["gain"],
                    solution["set_delta"],
                    solution["mod_value_delta"],
                    tuple(rid(m["replacement"]) for m in solution["moves"])
                ), reverse=True)
                return terminal_solutions[0]
            queue=next_queue
        return None

    plans, failed, used_ids = [], [], set()
    for target_id, opt in optimizer.items():
        target_owner = resolve_target_owner(target_id)
        if not target_owner:
            failed.append((target_id, "brak identyfikatora postaci w roster.csv")); continue
        for mod in opt.get("mods", []):
            slot = str(mod.get("slot",""))
            current = working_eq.get((target_owner, slot))
            if current is not None and rid(current) == rid(mod): continue
            plan = find_chain(mod, target_id, target_owner, current, used_ids)
            if plan is None:
                failed.append((target_id, "brak wykonalnego łańcucha dla {} / {}".format(slot,mod.get("set","")))); continue
            physical = {rid(mod)}
            for move in plan["moves"]:
                physical.update((rid(move["removed"]), rid(move["replacement"])))
            # The first PATCH fills the physical hole left by MOD and has no
            # removed mod. Empty IDs are sentinels, not shared resources.
            physical.discard("")
            if physical & used_ids:
                failed.append((target_id, "konflikt modów dla {} / {}".format(slot,mod.get("set","")))); continue
            used_ids.update(physical)
            plans.append({"target":target_id,"target_owner":target_owner,"mod":mod,
                          "target_current":current,"moves":plan["moves"],"chain_gain":plan["gain"],
                          "chain_set_delta":plan.get("set_delta",0),
                          "chain_mod_value_delta":plan.get("mod_value_delta",0.0)})

            old_owner = owner(mod)
            if old_owner and (old_owner,slot) in working_eq and rid(working_eq[(old_owner,slot)]) == rid(mod):
                working_eq.pop((old_owner,slot),None)
            for move in plan["moves"]:
                key=(move["owner"],slot)
                if key in working_eq and rid(working_eq[key]) == rid(move["removed"]):
                    working_eq.pop(key,None)
                working_eq[key]=move["replacement"]
            working_eq[(target_owner,slot)]=mod

    final_eq = dict(working_eq)

    # Independent physical replay: do not trust the planner's mutable working_eq.
    # Every step must consume a mod from its actual current location and leave
    # exactly one copy in exactly one place.
    simulated_slots = {(o, slot): rid(mod) for (o, slot), mod in eq.items()}
    simulated_inventory = {rid(mod) for mod in inventory}
    physical_errors = []

    def take_mod(mod_id, expected_owner=None, expected_slot=None):
        if expected_owner:
            key = (expected_owner, expected_slot) if expected_slot else next(
                (k for k, value in simulated_slots.items()
                 if k[0] == expected_owner and value == mod_id), None)
            if key is None or simulated_slots.get(key) != mod_id:
                physical_errors.append(
                    "mod {} nie znajduje się w slocie {} postaci {}".format(
                        mod_id, expected_slot or "dowolnym", expected_owner))
                return False
            simulated_slots.pop(key)
            return True
        if mod_id in simulated_inventory:
            simulated_inventory.remove(mod_id)
            return True
        key = next((k for k, value in simulated_slots.items() if value == mod_id), None)
        if key is not None:
            simulated_slots.pop(key)
            return True
        physical_errors.append("mod {} nie istnieje w aktualnym stanie symulacji".format(mod_id))
        return False

    for plan in plans:
        selected = plan["mod"]
        selected_id = rid(selected)
        selected_source = owner(selected)
        target_owner = plan["target_owner"]
        slot = str(selected.get("slot", "") or "")
        if selected_source:
            if not take_mod(selected_id, selected_source, slot):
                continue
        elif not take_mod(selected_id):
            continue

        target_key = (target_owner, slot)
        displaced_id = simulated_slots.pop(target_key, None)
        if displaced_id:
            simulated_inventory.add(displaced_id)
        simulated_slots[target_key] = selected_id

        for move in plan.get("moves", []):
            replacement = move["replacement"]
            replacement_id = rid(replacement)
            replacement_slot = str(replacement.get("slot", "") or "")
            destination = (move["owner"], slot)
            if replacement_slot != slot:
                physical_errors.append("PATCH {} używa slotu {}, wymagany {}".format(
                    replacement_id, replacement_slot, slot))
                continue
            if not take_mod(replacement_id):
                continue
            removed_id = simulated_slots.pop(destination, None)
            expected_removed_id = rid(move.get("removed"))
            if removed_id != (expected_removed_id or None):
                physical_errors.append("PATCH {}: w slocie {} postaci {} oczekiwano {}, znaleziono {}".format(
                    replacement_id, slot, move["owner"], expected_removed_id or "PUSTO", removed_id or "PUSTO"))
            if removed_id:
                simulated_inventory.add(removed_id)
            simulated_slots[destination] = replacement_id

    expected_slots = {(o, slot): rid(mod) for (o, slot), mod in final_eq.items()}
    if simulated_slots != expected_slots:
        physical_errors.append("końcowy stan slotów po symulacji różni się od stanu zaplanowanego")
    initial_ids = [rid(mod) for mod in eq.values()] + [rid(mod) for mod in inventory]
    all_simulated_ids = list(simulated_slots.values()) + list(simulated_inventory)
    if len(all_simulated_ids) != len(set(all_simulated_ids)):
        physical_errors.append("ten sam mod występuje jednocześnie w kilku miejscach")
    if set(all_simulated_ids) != set(initial_ids) or len(all_simulated_ids) != len(initial_ids):
        physical_errors.append("końcowy stan zgubił lub dodał mod względem pełnego stanu wejściowego")
    if physical_errors:
        safe = False
        failed.extend(("walidacja fizyczna", error) for error in physical_errors)

    affected = {p["target_owner"] for p in plans}
    affected.update(owner(p["mod"]) for p in plans if owner(p["mod"]))
    affected.update(m["owner"] for p in plans for m in p["moves"])
    validation=[]; safe=not failed
    all_owners={o for o,_s in eq}|{o for o,_s in final_eq}|affected
    for o in sorted(all_owners):
        before=[r for (oo,_s),r in eq.items() if oo==o]
        after=[r for (oo,_s),r in final_eq.items() if oo==o]
        if not before and not after: continue
        bc,ac=set_counts(before),set_counts(after)
        bg=set_groups(before); ag=set_groups(after)
        before_value=sum(float(r.get("modValue",0) or 0) for r in before)
        after_value=sum(float(r.get("modValue",0) or 0) for r in after)
        before_counts=set_counts(before)
        after_counts=set_counts(after)
        set_changes=[]
        for set_name in SET_RULES:
            required=SET_RULES[set_name][1]
            before_count=before_counts.get(set_name,0)
            after_count=after_counts.get(set_name,0)
            before_full=bg.get(set_name,0)
            after_full=ag.get(set_name,0)
            if before_count != after_count or before_full != after_full:
                if after_full > before_full:
                    status="UKOŃCZONO"
                elif before_full > after_full:
                    status="ROZBITO"
                elif after_count > before_count:
                    status="BUDOWANY"
                else:
                    status="OSŁABIONY"
                set_changes.append({
                    "set":set_name,"status":status,
                    "beforeCount":before_count,"afterCount":after_count,
                    "required":required,"beforeFull":before_full,"afterFull":after_full
                })
        donor_profile = profiles.get(aliases.get(o, o), {}) or {}
        profile_score = compare_profiled_builds(before, after, donor_profile)
        before_combo = profile_set_combo_match(donor_profile, before)
        after_combo = profile_set_combo_match(donor_profile, after)
        validation.append({
            "owner":o,"name":pname(o),"before":bc,"after":ac,
            "beforeComboKey":before_combo.get("key", "") if before_combo else "",
            "beforeComboFrequency":before_combo.get("frequency") if before_combo else None,
            "afterComboKey":after_combo.get("key", "") if after_combo else "",
            "afterComboFrequency":after_combo.get("frequency") if after_combo else None,
            "beforeCounts":before_counts,"afterCounts":after_counts,
            "setChanges":set_changes,
            "beforeGroups":bg,"afterGroups":ag,
            "beforeModValue":round(before_value,1),
            "afterModValue":round(after_value,1),
            "modValueDelta":round(after_value-before_value,1),
            "beforeProfileScore":profile_score["before"] if profile_score else None,
            "afterProfileScore":profile_score["after"] if profile_score else None,
            "profileScoreDelta":profile_score["delta"] if profile_score else None,
            "profileScoreAvailable":profile_score is not None,
            "ok":True
        })

    for target_id,opt in optimizer.items():
        target_owner=resolve_target_owner(target_id)
        for mod in opt.get("mods",[]):
            placed=final_eq.get((target_owner,str(mod.get("slot","")))) if target_owner else None
            if not placed or rid(placed)!=rid(mod):
                safe=False; failed.append((target_id,"optimizer mod nie trafił na miejsce: {}".format(mod.get("slot",""))))

    if safe:
        for plan in plans:
            mod=plan["mod"]; slot=str(mod.get("slot",""))
            target_slot_was_empty = (plan["target_owner"], str(mod.get("slot",""))) not in eq
            mod["recommendedAction"]="EQUIP" if target_slot_was_empty else "REPLACE"
            mod["chainStatus"]="VALIDATED"
            mod["chainId"]="{}:{}".format(plan["target"],slot)
            mod["chainLength"]=1+len(plan["moves"]); mod["chainGain"]=round(plan["chain_gain"],1)
            mod["chainSetDelta"]=plan.get("chain_set_delta",0)
            mod["chainModValueDelta"]=round(plan.get("chain_mod_value_delta",0.0),1)
            # Physical execution starts with the selected mod, then repairs the vacated slot.
            # Every PATCH is a separate mod transfer; the selected mod never travels through
            # another character.
            selected_source = pname(owner(mod)) if owner(mod) else "MAGAZYN"
            selected_path = "{} -> {}".format(selected_source, pname(plan["target_owner"]))
            repair_path = []
            for move in plan["moves"]:
                replacement = move["replacement"]
                replacement_source = pname(owner(replacement)) if is_true(replacement.get("equipped")) else "MAGAZYN"
                repair_path.append("PATCH: {} -> {}".format(replacement_source, move["name"]))
            mod["chainPath"] = "MOD: " + selected_path + (("; " + "; ".join(repair_path)) if repair_path else "")
            mod["reason"]="ŁAŃCUCH WYKONALNY; najpierw MOD bezpośrednio do celu, potem PATCH-y w kolejności zależności"
            for idx,move in enumerate(plan["moves"],1):
                patch=move["replacement"]
                patch_row=next((r for r in rows if rid(r)==rid(patch)),patch)
                patch_row["recommendedAction"]="PATCH"; patch_row["chainStatus"]="VALIDATED"
                patch_row["patchOwner"]=move["owner"]; patch_row["patchOwnerName"]=move["name"]; patch_row["patchSlot"]=slot
                patch_row["chainId"]=mod["chainId"]; patch_row["chainStep"]=idx; patch_row["chainLength"]=mod["chainLength"]
                patch_row["chainPath"]=mod["chainPath"]; patch_row["replacesModId"]=rid(move["removed"])
                patch_row["replacementGain"]=round(move["gain"],1); patch_row["accountGain"]=round(move["gain"],1)
                patch_row["chainSetDelta"]=mod.get("chainSetDelta",0)
                patch_row["chainModValueDelta"]=mod.get("chainModValueDelta",0.0)
                patch_row["reason"]="PATCH {}; zmiana pełnych setów {:+d}".format(move["name"],move["set_delta"])
    else:
        for r in rows:
            if r.get("optimizerTarget"): r["chainStatus"]="BLOCKED"

    return {"safe":safe,"plans":plans,"validation":validation,"failed":failed}




def project_mod_for_build(row, profile):
    """
    Optimistic, explicitly separate projection:
    - complete the rolls available at the current tier up to level 15;
    - for a 5-dot 5A mod, project existing rolls to 6-dot 6E values.
    Missing rolls are assigned to the highest-priority secondary in the profile.
    This is a potential ceiling, not a prediction of RNG outcomes.
    """
    projected = dict(row)
    dots = integer(row.get("dots"))
    tier = integer(row.get("tier"))
    current_level = integer(row.get("level"))
    entries = []

    for index in range(1, 5):
        data = rolls(row, index)
        if data is None:
            continue
        stat, value, count, values = data
        if count <= 0:
            continue
        if not values:
            values = [value / count] * count
        entries.append({"stat": stat, "values": list(values)})

    current_rolls = sum(len(item["values"]) for item in entries)
    max_rolls = TOTAL.get((dots, tier), current_rolls)
    missing_rolls = max(0, max_rolls - current_rolls)

    preferences = profile.get("secondary_preferences", {})
    candidates = [
        (float(weight), stat)
        for stat, weight in preferences.items()
        if stat in (R6 if dots >= 6 else R5) and float(weight) > 0
    ]
    candidates.sort(key=lambda item: (item[0], STAT_VALUE.get(item[1], 0.0)), reverse=True)

    if missing_rolls and candidates:
        best_stat = candidates[0][1]
        existing = next((item for item in entries if item["stat"] == best_stat), None)
        low, high = (R6 if dots >= 6 else R5)[best_stat]
        assumed_roll = (low + high) / 2.0
        if existing is None and len(entries) < 4:
            existing = {"stat": best_stat, "values": []}
            entries.append(existing)
        if existing is not None:
            existing["values"].extend([assumed_roll] * missing_rolls)

    # A 5A -> 6E slice preserves roll count while increasing the value of
    # each secondary roll according to the corresponding 6-dot roll range.
    projected_dots = dots
    if dots == 5 and tier == 5 and current_level >= 15:
        projected_dots = 6
        for item in entries:
            old_range = R5.get(item["stat"])
            new_range = R6.get(item["stat"])
            if old_range and new_range and old_range[1]:
                ratio = new_range[1] / old_range[1]
                item["values"] = [value * ratio for value in item["values"]]

    # Re-serialize projected secondaries in the same schema consumed by rolls().
    for index in range(1, 5):
        projected["secondary{}Stat".format(index)] = ""
        projected["secondary{}Value".format(index)] = ""
        projected["secondary{}Rolls".format(index)] = ""
        projected["secondary{}RawRolls".format(index)] = ""
    for index, item in enumerate(entries[:4], 1):
        stat = item["stat"]
        values = item["values"]
        scale = 10000.0 if stat in {"Health", "Protection", "Offense", "Defense", "Speed"} else 100.0
        projected["secondary{}Stat".format(index)] = stat
        projected["secondary{}Value".format(index)] = str(sum(values))
        projected["secondary{}Rolls".format(index)] = str(len(values))
        projected["secondary{}RawRolls".format(index)] = "|".join(
            str(int(round(value * scale))) for value in values
        )

    projected["dots"] = str(projected_dots)
    projected["level"] = "15"
    projected["projectionLevel"] = 15
    projected["projectionDots"] = projected_dots
    projected["projectionAssumedRolls"] = missing_rolls
    projected["projectionType"] = (
        "15 + 6E" if projected_dots == 6 else "15"
    )
    return projected


def optimize_target_build(rows, target_base_ids, profiles=None, aliases=None, names=None, protected_owners=None):
    """Independently implemented full-build optimizer inspired by Grandivory."""
    profiles = profiles or {}
    aliases = aliases or {}
    names = names or {}
    protected_owners = set(protected_owners or set())
    slots = ("Square", "Diamond", "Circle", "Arrow", "Triangle", "Cross")
    primary_points, secondary_points, max_rolls = PROFILE_PRIMARY_POINTS, PROFILE_SECONDARY_POINTS, PROFILE_MAX_ROLLS
    speed_reference = 150.0
    set_max_roll = {
        "Critical Chance %": 2.25, "Critical Damage %": 36.0,
        "Defense %": 1.70, "Health %": 1.125, "Offense %": 0.563,
        "Potency %": 2.25, "Speed": 6.0, "Tenacity %": 2.25,
    }

    def rid(row):
        return str(row.get("id", "") or "")

    def base(row):
        owner_id = str(row.get("assignedTo", "") or "")
        return aliases.get(owner_id, owner_id)

    def mod_score(row, profile):
        return profile_mod_score_components(row, profile)["fitScore"]

    def set_bonus_score(mods, profile):
        grouped = {}
        for mod in mods:
            name = str(mod.get("set", "") or "")
            if name in SET_RULES:
                grouped.setdefault(name, []).append(mod)

        total, preference_tiebreak, breakdown = 0.0, 0.0, {}
        secondary_prefs = profile.get("secondary_preferences", {})
        for name, members in grouped.items():
            stat, required, small_bonus, max_bonus = SET_RULES[name]
            count = len(members)
            max_count = sum(1 for m in members if integer(m.get("level")) >= 15)
            full_groups = max_count // required
            half_groups = (count - full_groups * required) // required
            if not full_groups and not half_groups:
                continue

            set_pref = profile_set_preference(profile, name)
            preference_tiebreak += (full_groups + half_groups) * set_pref
            profile_stat = {
                "Health %": "Health",
                "Defense %": "Defense",
                "Offense %": "Offense",
                "Potency %": "Potency",
                "Tenacity %": "Tenacity",
            }.get(stat, stat)
            stat_pref = max(
                0.0,
                float(secondary_prefs.get(stat, 0.0)),
                float(secondary_prefs.get(profile_stat, 0.0)),
            )
            max_roll = R5.get(stat, (0.0, 0.0))[1] or set_max_roll.get(stat)
            # The profile's set preference is independent evidence that the
            # set bonus is useful, even when its stat is absent from the top
            # secondary-focus list.
            stat_pref = max(stat_pref, set_pref)
            if not max_roll or not stat_pref:
                continue

            if stat == "Speed":
                base_speed = number(profile.get("base_stats", {}).get("Speed", speed_reference), speed_reference)
                full_units = max_bonus * base_speed / 100.0
                half_units = small_bonus * base_speed / 100.0
            else:
                # The set and secondary are both expressed in percentage points.
                full_units, half_units = max_bonus, small_bonus

            equivalents = (full_groups * full_units + half_groups * half_units) / max_roll
            # Profile alignment is the primary objective. A set absent from
            # the profile retains only a small 10% floor; a fully preferred
            # set receives full weight. Existing ownership is only a tie-break.
            set_weight = 0.10 + 0.90 * min(1.0, set_pref)
            points = equivalents * stat_pref * set_weight * secondary_points / max_rolls
            total += points
            breakdown[name] = {
                "fullGroups": full_groups, "halfGroups": half_groups,
                "stat": stat, "equivalentRolls": equivalents, "score": points,
            }
        return total, preference_tiebreak, breakdown

    def build_score(mods, profile, projected=False):
        scored_mods = [
            project_mod_for_build(m, profile) if projected else m
            for m in mods
        ]
        base_score = sum(mod_score(m, profile) for m in scored_mods)
        set_score, set_pref, breakdown = set_bonus_score(scored_mods, profile)
        combo_score, combo_match = profile_set_combo_alignment_score(profile, scored_mods)
        return {
            "total": base_score + set_score + combo_score, "base": base_score,
            "setBonus": set_score, "setPreference": set_pref,
            "setComboAlignment": combo_score, "setComboMatch": combo_match,
            "setComboKey": combo_match.get("key") if combo_match else None,
            "setComboFrequency": combo_match.get("frequency") if combo_match else None,
            "setComboMode": "weighted" if combo_match else "none",
            "setBreakdown": breakdown,
        }

    results = {}
    for target_id in sorted(set(target_base_ids)):
        profile = profiles.get(target_id)
        if not profile:
            continue

        current = [r for r in rows if is_true(r.get("equipped")) and base(r) == target_id]
        current_by_slot = {str(r.get("slot", "")): r for r in current}
        current_score = build_score(current, profile)
        current_projected_score = build_score(current, profile, projected=True)

        # For a fixed slot and set, only the highest-scoring candidate can win:
        # every such candidate has the same set-bonus effect. This is an exact
        # reduction, unlike the old arbitrary top-12/top-48 candidate limits.
        pools = {}
        for slot in slots:
            best_by_set = {}
            for row in rows:
                if str(row.get("slot", "")) != slot:
                    continue
                if integer(row.get("dots")) < 5:
                    continue
                if is_true(row.get("equipped")) and base(row) in protected_owners:
                    continue
                name = str(row.get("set", "") or "")
                unchanged = slot in current_by_slot and rid(current_by_slot[slot]) == rid(row)
                key = (
                    mod_score(project_mod_for_build(row, profile), profile), 1 if unchanged else 0,
                    float(row.get("potentialCeiling", 0) or 0),
                    float(row.get("modValue", 0) or 0),
                )
                if name not in best_by_set or key > best_by_set[name][0]:
                    best_by_set[name] = (key, row, unchanged)
            pools[slot] = [(v[1], v[2]) for v in best_by_set.values()]

        if any(not pools[slot] for slot in slots):
            continue

        # Exact DP over set counts. Two-piece sets may complete three groups;
        # four-piece sets may complete one. No beam truncation is used.
        set_names = tuple(SET_RULES.keys())
        caps = {
            name: SET_RULES[name][1] * (len(slots) // SET_RULES[name][1])
            for name in set_names
        }
        states = {(0,) * len(set_names): (0.0, 0, [])}
        for slot in slots:
            next_states = {}
            for counts, (score_so_far, unchanged_so_far, chosen) in states.items():
                for row, unchanged in pools[slot]:
                    name = str(row.get("set", "") or "")
                    new_counts = list(counts)
                    if name in caps:
                        index = set_names.index(name)
                        new_counts[index] = min(caps[name], new_counts[index] + 1)
                    new_counts = tuple(new_counts)
                    projected_row = project_mod_for_build(row, profile)
                    candidate = (
                        score_so_far + mod_score(projected_row, profile),
                        unchanged_so_far + (1 if unchanged else 0),
                        chosen + [row],
                    )
                    old = next_states.get(new_counts)
                    if old is None or candidate[0] > old[0] + 1e-9 or (
                        abs(candidate[0] - old[0]) <= 1e-9 and candidate[1] > old[1]
                    ):
                        next_states[new_counts] = candidate
            states = next_states

        best = None
        for _counts, (base_score, unchanged_count, chosen) in states.items():
            projected_chosen = [project_mod_for_build(m, profile) for m in chosen]
            set_score, set_pref, breakdown = set_bonus_score(projected_chosen, profile)
            combo_score, combo_match = profile_set_combo_alignment_score(profile, projected_chosen)
            total = base_score + set_score + combo_score
            # An observed complete set combination is a categorical profile
            # preference, not a small additive bonus. Compare its normalized
            # frequency before raw mod quality so a high-scoring but unobserved
            # set mix cannot defeat the dominant profile combination.
            combo_preference = float(combo_match.get("preference", 0.0)) if combo_match else 0.0
            key = (combo_preference, total, set_pref, unchanged_count)
            if best is None or key > best["key"]:
                best = {
                    "key": key, "totalScore": total, "baseScore": base_score,
                    "setBonusScore": set_score, "setPreferenceScore": set_pref,
                    "setBreakdown": breakdown,
                    "setComboAlignmentScore": combo_score,
                    "setComboPreference": combo_preference,
                    "setComboMatch": combo_match,
                    "setComboKey": combo_match.get("key") if combo_match else None,
                    "setComboFrequency": combo_match.get("frequency") if combo_match else None,
                    "setComboMode": "profile_priority" if combo_match else "none",
                    "unchangedCount": unchanged_count,
                    "mods": chosen,
                }
        if not best:
            continue

        for mod in best["mods"]:
            projected_mod = project_mod_for_build(mod, profile)
            mod["optimizerTarget"] = target_id
            mod["optimizerScore"] = round(mod_score(mod, profile), 2)
            mod["optimizerProjectedScore"] = round(mod_score(projected_mod, profile), 2)
            mod["optimizerProjection"] = projected_mod.get("projectionType", "15")
            mod["optimizerProjectionAssumedRolls"] = projected_mod.get("projectionAssumedRolls", 0)
            mod["optimizerTotalScore"] = round(best["totalScore"], 2)
            mod["optimizerBaseScore"] = round(best["baseScore"], 2)
            mod["optimizerSetBonusScore"] = round(best["setBonusScore"], 2)
            mod["optimizerSetPreferenceScore"] = round(best["setPreferenceScore"], 3)
            mod["optimizerSetComboAlignmentScore"] = round(best["setComboAlignmentScore"], 3)
            mod["optimizerCurrentScore"] = round(current_score["total"], 2)
            mod["optimizerCurrentProjectedScore"] = round(current_projected_score["total"], 2)
            mod["optimizerGain"] = round(best["totalScore"] - current_projected_score["total"], 2)
            mod["optimizerSource"] = source_label(mod, aliases, names)

        results[target_id] = {
            "mods": best["mods"], "totalScore": best["totalScore"],
            "baseScore": best["baseScore"], "setBonusScore": best["setBonusScore"],
            "setPreferenceScore": best["setPreferenceScore"],
            "setComboAlignmentScore": best["setComboAlignmentScore"],
            "setComboMatch": best["setComboMatch"],
            "setComboKey": best["setComboKey"],
            "setComboFrequency": best["setComboFrequency"],
            "setComboMode": best["setComboMode"],
            "setBreakdown": best["setBreakdown"], "unchangedCount": best["unchangedCount"],
            "currentScore": current_score["total"],
            "currentProjectedScore": current_projected_score["total"],
            "currentBaseScore": current_score["base"],
            "currentSetBonusScore": current_score["setBonus"],
            "gain": best["totalScore"] - current_projected_score["total"],
        }
    return results


def profile_set_combo_support(profile, set_name):
    """Percentage of observed builds whose set combination contains set_name."""
    combinations = profile.get("set_combinations", {}) or {}
    if not combinations:
        return None
    total = 0.0
    aliases = {"Crit Damage": "Critical Damage", "Crit Chance": "Critical Chance"}
    for combination, frequency in combinations.items():
        names = []
        for token in str(combination).split("+"):
            name = token.strip()
            for prefix in ("Double ", "Triple "):
                if name.startswith(prefix):
                    name = name[len(prefix):].strip()
                    break
            names.append(aliases.get(name, name))
        if set_name in names:
            try:
                total += float(frequency or 0.0)
            except (TypeError, ValueError):
                pass
    return min(100.0, total)

def account_balance_summary(validation, affected_owners, profiles, aliases):
    """Sum comparable unprojected full-build deltas for target and every donor."""
    items = [
        item for item in validation
        if item.get("owner") in affected_owners
    ]
    complete = bool(items) and all(
        item.get("profileScoreAvailable")
        and profiles.get(aliases.get(str(item.get("owner", "") or ""),
                                     str(item.get("owner", "") or "")))
        for item in items
    )
    if not complete:
        return items, None
    return items, round(sum(
        float(item.get("profileScoreDelta", 0.0) or 0.0)
        for item in items
    ), 2)


def render_user_report(rows, optimizer, chain_result, profiles, aliases, names,
                       target_ids, profile_fetch_status, display_name):
    """Create a short, executable report for the player; CSV remains technical."""
    if not optimizer:
        return "# Raport modów\n\n**STATUS: BLOKADA** — brak kompletnego buildu. Nie wykonuj przekładek.\n"

    def rid(row):
        return str(row.get("id", "") or "")

    def mod_owner(row):
        return str(row.get("assignedTo", "") or "") if is_true(row.get("equipped")) else ""

    def owner_base(row):
        owner_id = str(row.get("assignedTo", "") or "")
        return aliases.get(owner_id, owner_id)

    lines = [
        "# Raport modów — {}".format(", ".join(display_name(x) for x in sorted(optimizer))),
        "",
        "**Raport użytkowy.** Pokazuje wyłącznie docelowe mody, kolejność przekładek i wpływ na dawców.",
        "",
    ]
    affected_owners = set()
    for plan in chain_result.get("plans", []):
        if plan.get("target_owner"):
            affected_owners.add(plan["target_owner"])
        selected_owner = mod_owner(plan.get("mod", {}))
        if selected_owner:
            affected_owners.add(selected_owner)
        affected_owners.update(move.get("owner") for move in plan.get("moves", []) if move.get("owner"))

    donor_costs = []
    for item in chain_result.get("validation", []):
        if item.get("owner") in affected_owners and item.get("owner") not in {
            next((str(r.get("assignedTo", "") or "") for r in rows
                  if is_true(r.get("equipped")) and owner_base(r) == target_id), target_id)
            for target_id in optimizer
        }:
            donor_costs.append(item)

    # Compare every affected character, including the target, with the same
    # unprojected profile-aware full-build scorer. Never mix the target's
    # optimistic projected gain with donors' actual before/after deltas.
    target_owners = {
        next((str(r.get("assignedTo", "") or "") for r in rows
              if is_true(r.get("equipped")) and owner_base(r) == target_id), target_id)
        for target_id in optimizer
    }
    account_items, account_delta = account_balance_summary(
        chain_result.get("validation", []), affected_owners, profiles, aliases
    )

    # A broken set is material only when it is a meaningful part of that
    # donor's observed SWGOH.GG build profile. 20% is the explicit threshold
    # for a common build pattern; below it the change remains informational.
    donor_assessments = {}
    donor_compromise = False
    for item in donor_costs:
        owner = str(item.get("owner", "") or "")
        base_id = aliases.get(owner, owner)
        profile = profiles.get(base_id, {})
        material_set_losses = []
        minor_set_changes = []
        for change in item.get("setChanges", []):
            if change.get("status") not in ("ROZBITO", "OSŁABIONY"):
                continue
            set_name = str(change.get("set", "") or "")
            support = profile_set_combo_support(profile, set_name) if profile else None
            if support is None or support >= 20.0:
                material_set_losses.append((set_name, support))
            else:
                minor_set_changes.append((set_name, support))
        profile_delta = item.get("profileScoreDelta")
        value_delta = float(item.get("modValueDelta", 0.0) or 0.0)
        # Prefer the donor's complete profile-aware build score. modValue is
        # only a fallback when no donor profile could be obtained.
        effective_delta = (
            float(profile_delta) if profile_delta is not None else value_delta
        )
        material = effective_delta < -0.05 or bool(material_set_losses)
        donor_assessments[owner] = {
            "material": material,
            "value_delta": effective_delta,
            "profile_score_available": profile_delta is not None,
            "material_set_losses": material_set_losses,
            "minor_set_changes": minor_set_changes,
        }
        donor_compromise = donor_compromise or material
    # For donors without a profile, move.gain is the explicitly labeled
    # single-mod fallback. Preserve that warning in the overall status.
    unavailable_profile_losses = any(
        not profiles.get(aliases.get(str(move.get("owner", "") or ""), str(move.get("owner", "") or "")))
        and float(move.get("gain", 0.0) or 0.0) < -0.05
        for plan in chain_result.get("plans", [])
        for move in plan.get("moves", [])
    )
    donor_compromise = donor_compromise or unavailable_profile_losses
    if not chain_result.get("safe"):
        assessment = "BLOKADA — nie wykonuj przekładek"
    elif account_delta is None:
        assessment = "BILANS NIEPEŁNY — brakuje porównywalnego profilu dla co najmniej jednej postaci"
    elif account_delta <= 0.05:
        assessment = "BILANS NIEDODATNI — nie rekomenduję wykonania łańcucha"
    elif donor_compromise:
        assessment = "KOMPROMIS — bilans rosteru dodatni, ale co najmniej jeden dawca traci"
    else:
        assessment = "REKOMENDACJA — dodatni bilans całego rosteru, bez wykrytej straty u dawców"

    lines += [
        "## Status",
        "",
        "- **Wykonalność fizyczna:** {}".format("POTWIERDZONA" if chain_result.get("safe") else "ZABLOKOWANA"),
        "- **Walidacja fizyczna całego łańcucha:** {}".format("POTWIERDZONA" if chain_result.get("safe") else "ZABLOKOWANA"),
        "- **Ocena:** {}".format(assessment),
        "- **Interpretacja:** bilans obejmuje cel i wszystkich dotkniętych dawców, liczony tą samą nieprojekcyjną punktacją pełnego buildu.",
        "- **Łączny bilans profilu rosteru:** {}".format(
            "NIEOBLICZALNY — brak profilu/oceny dla jednej z postaci"
            if account_delta is None else "{:+.2f} pkt".format(account_delta)
        ),
        "- **Liczba modów docelowych:** {}/6".format(
            min(6, max((len(opt.get("mods", [])) for opt in optimizer.values()), default=0))
        ),
        "",
    ]

    if account_items:
        lines += ["## Bilans całej operacji — ta sama punktacja przed/po", "",
                  "Wynik każdego buildu jest liczony bez projekcji przyszłych rolli i bez założeń o slice. Suma obejmuje cel oraz każdego dawcę bezpośredniego i pośredniego.", "",
                  "| Postać | Rola w łańcuchu | Wynik przed | Wynik po | Zmiana |",
                  "|---|---|---:|---:|---:|"]
        for item in account_items:
            owner_id = str(item.get("owner", "") or "")
            role = "CEL" if owner_id in target_owners else "DAWCA"
            if item.get("profileScoreAvailable"):
                lines.append("| {} | {} | {:.2f} | {:.2f} | {:+.2f} |".format(
                    item.get("name", display_name(owner_id)), role,
                    float(item.get("beforeProfileScore", 0.0) or 0.0),
                    float(item.get("afterProfileScore", 0.0) or 0.0),
                    float(item.get("profileScoreDelta", 0.0) or 0.0)))
            else:
                lines.append("| {} | {} | — | — | BRAK PROFILU |".format(
                    item.get("name", display_name(owner_id)), role))
        lines.append("")
        if account_delta is not None:
            lines.append("**ŁĄCZNA ZMIANA: {:+.2f} pkt.**".format(account_delta))
        else:
            lines.append("**ŁĄCZNA ZMIANA: NIEOBLICZALNA** — nie sumuję punktacji z fallbackiem modValue.")
        lines.append("")

    for target_id, opt in optimizer.items():
        target_owner = next(
            (str(r.get("assignedTo", "") or "") for r in rows
             if is_true(r.get("equipped")) and owner_base(r) == target_id),
            target_id,
        )
        target_name = display_name(target_owner)
        profile = profiles.get(target_id, {})
        sources = profile.get("source_model", {}).get("sources", [])
        lines += [
            "## Docelowy zestaw — {}".format(target_name),
            "",
            "### Profil SWGOH.GG",
            "",
        ]
        if sources:
            for source in sources:
                lines.append("- {} — {} postaci z kompletnymi 6 modami".format(
                    source.get("name", "Źródło"), source.get("units_fully_modded", "—")
                ))
        else:
            lines.append("- Brak kompletnego profilu celu.")
        combos = profile.get("set_combinations", {}) or {}
        if combos:
            top_combos = sorted(combos.items(), key=lambda item: float(item[1] or 0), reverse=True)[:3]
            lines.append("- Najczęstsze kombinacje: {}".format(
                "; ".join("{} ({:.1f}%)".format(k, float(v)) for k, v in top_combos)
            ))
        if opt.get("setComboMode") in {"exact", "tie_break", "weighted"}:
            if opt.get("setComboKey"):
                qualifier = "element punktacji ważonej" if opt.get("setComboMode") == "weighted" else ("kryterium rozstrzygające remis" if opt.get("setComboMode") == "tie_break" else "element punktacji")
                lines.append("- **Dopasowanie dokładnej kombinacji ({}):** {} — {:.2f}% profilu.".format(
                    qualifier, opt["setComboKey"], float(opt.get("setComboFrequency") or 0.0)
                ))
            else:
                lines.append("- **Dokładna kombinacja nieobecna w profilu:** brak dodatkowego kryterium; zachowano dotychczasowe preferencje pojedynczych setów.")
        secondary = profile.get("secondary_preferences", {}) or {}
        top_secondary = sorted(secondary.items(), key=lambda item: float(item[1] or 0), reverse=True)[:4]
        if top_secondary:
            lines.append("- Priorytet secondary: {}".format(
                ", ".join(k for k, _ in top_secondary)
            ))
        lines += ["", "### Sześć modów docelowych", ""]

        current_by_slot = {
            str(r.get("slot", "")): r for r in rows
            if is_true(r.get("equipped")) and owner_base(r) == target_id
        }
        selected_by_slot = {
            str(mod.get("slot", "")): mod for mod in opt.get("mods", [])
        }
        slot_order = ["Arrow", "Square", "Diamond", "Triangle", "Circle", "Cross"]
        for slot in slot_order:
            # The user-facing validator expects a distinct section for every
            # slot so it can verify current and proposed mods independently.
            lines.append("#### {}".format(slot))
            mod = selected_by_slot.get(slot)
            if not mod:
                lines.append("- **BRAK MODA W BUILDZIE**")
                continue
            current = current_by_slot.get(slot)
            unchanged = current is not None and rid(current) == rid(mod)
            source_id = mod_owner(mod)
            source_name = display_name(source_id) if source_id else "MAGAZYN"
            if unchanged:
                lines.append("- **Obecny mod:** {}".format(mod_description(current)))
                lines.append("- **Proponowany mod:** pozostaje bez zmian — {}".format(mod_description(mod)))
                lines.append("- **Korzyść:** zachowanie obecnej konfiguracji slotu.")
            else:
                lines.append("- **Obecny mod:** {}".format(mod_description(current) if current else "Pusty slot"))
                lines.append("- **Proponowany mod:** {}".format(mod_description(mod)))
                lines.append("- **Źródło:** {}".format(source_name))
                if current and profile:
                    before_fit = score_profile(current, profile)["fitScore"]
                    after_fit = score_profile(mod, profile)["fitScore"]
                    lines.append("  - Zmiana dopasowania do profilu: {:+.1f} pkt ({:.1f} → {:.1f}).".format(
                        after_fit - before_fit, before_fit, after_fit))

        gain = float(opt.get("gain", 0.0) or 0.0)
        lines += [
            "",
            "- **Zmiana potencjału buildu:** {:+.1f} pkt (optymistyczna projekcja do 15; brakujące rolle przypisane do najwyżej preferowanej secondary; dla 5A projekcja secondary do 6E; primary pozostaje bez zmian; bez slice i calibration).".format(gain),
            "",
        ]

        lines += ["## MOD — mody przenoszone na cel", ""]
        if chain_result.get("safe"):
            for plan in chain_result.get("plans", []):
                selected = plan.get("mod", {})
                source_owner = mod_owner(selected)
                source_name = display_name(source_owner) if source_owner else "MAGAZYN"
                lines.append("- **{} → {}:** {}".format(
                    source_name, display_name(plan.get("target_owner", "")), mod_description(selected)))
        else:
            lines.append("Brak zatwierdzonych transferów MOD.")
        lines += ["", "## PATCH — uzupełnienie dawców", ""]
        patch_count = 0
        if chain_result.get("safe"):
            for plan in chain_result.get("plans", []):
                for move in plan.get("moves", []):
                    replacement = move.get("replacement", {})
                    source_owner = mod_owner(replacement)
                    source_name = display_name(source_owner) if source_owner else "MAGAZYN"
                    lines.append("- **{} → {}:** {}".format(
                        source_name, move.get("name", display_name(move.get("owner", ""))),
                        mod_description(replacement)))
                    patch_count += 1
        if not patch_count:
            lines.append("Nie jest wymagany żaden PATCH.")
        lines.append("")
        if chain_result.get("safe"):
            lines += ["## Kolejność przekładania", ""]
            target_plans = [
                plan for plan in chain_result.get("plans", [])
                if plan.get("target") == target_id or plan.get("target_owner") == target_owner
            ]
            slot_order = ["Arrow", "Square", "Diamond", "Triangle", "Circle", "Cross"]
            target_plans.sort(key=lambda plan: (
                slot_order.index(str(plan.get("mod", {}).get("slot", "")))
                if str(plan.get("mod", {}).get("slot", "")) in slot_order else len(slot_order)
            ))

            # Phase 1: equip every selected mod on the main target first.
            step = 1
            for plan in target_plans:
                selected = plan["mod"]
                slot = str(selected.get("slot", ""))
                selected_source = mod_owner(selected)
                selected_source_name = display_name(selected_source) if selected_source else "MAGAZYN"
                lines.append("{}. **{} — załóż na {}** mod z {}: {}".format(
                    step, slot, target_name, selected_source_name, mod_description(selected)
                ))
                step += 1

            # Phase 2+: repair donors by dependency depth. A move at index 0
            # repairs a direct donor of the main target (level 1); its next
            # move repairs the donor that supplied that patch (level 2), etc.
            patch_levels = {}
            for plan in target_plans:
                for depth, move in enumerate(plan.get("moves", []), start=1):
                    patch_levels.setdefault(depth, []).append((plan, move))

            for depth in sorted(patch_levels):
                lines += ["", "### Uzupełnienie dawców — poziom {}".format(depth), ""]
                for plan, move in patch_levels[depth]:
                    replacement = move["replacement"]
                    displaced = plan.get("target_current")
                    if displaced and rid(replacement) == rid(displaced):
                        replacement_source = "MAGAZYN (mod automatycznie wyparty z {})".format(target_name)
                    elif is_true(replacement.get("equipped")):
                        replacement_source = display_name(mod_owner(replacement))
                    else:
                        replacement_source = "MAGAZYN (dostępny po wcześniejszym kroku)"
                    lines.append("{}. **PATCH — załóż na {}** mod z {}: {}".format(
                        step, move.get("name", display_name(move.get("owner", ""))),
                        replacement_source, mod_description(replacement)
                    ))
                    step += 1
            lines += ["", "Zakładanie moda automatycznie przenosi poprzedni mod ze slotu do magazynu. "
                      "Wszystkie powyższe kroki zostały sprawdzone na pełnym stanie slotów i magazynu.", ""]
        else:
            lines += [
                "## Kolejność przekładania",
                "",
                "**Nie wykonuj jeszcze żadnej przekładki.** Poniższy build jest wariantem roboczym; walidacja nie zatwierdziła pełnego łańcucha.",
                "",
                "### Co blokuje zatwierdzenie",
                "",
            ]
            failures = chain_result.get("failed", [])
            if failures:
                for category, reason in failures:
                    lines.append("- **{}:** {}".format(category, reason))
            else:
                lines.append("- Łańcuch nie przeszedł walidacji fizycznej.")

    if chain_result.get("validation"):
        lines += ["## Wpływ na postacie-dawców", ""]
        if donor_costs:
            for item in donor_costs:
                donor_name = item.get("name", display_name(item.get("owner", "")))
                profile_delta = item.get("profileScoreDelta")
                if profile_delta is not None:
                    lines.append("- **{} — wynik pełnego buildu wg profilu:** {:.2f} → {:.2f} ({:+.2f} pkt).".format(
                        donor_name,
                        float(item.get("beforeProfileScore", 0.0) or 0.0),
                        float(item.get("afterProfileScore", 0.0) or 0.0),
                        float(profile_delta),
                    ))
                else:
                    lines.append("- **{} — wynik pełnego buildu wg profilu:** niedostępny; użyto fallback modValue.".format(donor_name))
                lines.append("  - Σ modValue modów: {:.1f} → {:.1f} ({:+.1f}) — surowy wskaźnik jakości modów, nie wynik profilu.".format(
                    float(item.get("beforeModValue", 0.0) or 0.0),
                    float(item.get("afterModValue", 0.0) or 0.0),
                    float(item.get("modValueDelta", 0.0) or 0.0),
                ))
                before_combo_key = str(item.get("beforeComboKey", "") or "")
                after_combo_key = str(item.get("afterComboKey", "") or "")
                if before_combo_key or after_combo_key:
                    before_combo_frequency = item.get("beforeComboFrequency")
                    after_combo_frequency = item.get("afterComboFrequency")
                    before_label = before_combo_key or "kombinacja nieujęta w profilu"
                    after_label = after_combo_key or "kombinacja nieujęta w profilu"
                    before_pct = "—" if before_combo_frequency is None else "{:.1f}%".format(float(before_combo_frequency))
                    after_pct = "—" if after_combo_frequency is None else "{:.1f}%".format(float(after_combo_frequency))
                    lines.append("  - Kombinacja setów: {} ({}) → {} ({}).".format(
                        before_label, before_pct, after_label, after_pct
                    ))
                donor_moves = [
                    (str(plan.get("mod", {}).get("slot", "") or ""), float(move.get("gain", 0.0) or 0.0))
                    for plan in chain_result.get("plans", [])
                    for move in plan.get("moves", [])
                    if str(move.get("owner", "") or "") == str(item.get("owner", "") or "")
                ]
                if donor_moves:
                    base_id = aliases.get(str(item.get("owner", "") or ""), str(item.get("owner", "") or ""))
                    if profiles.get(base_id):
                        lines.append("  - Zmiana wyniku pełnego buildu po kolejnych PATCH-ach: {}.".format(
                            "; ".join("{} {:+.1f} pkt".format(slot, gain) for slot, gain in donor_moves)
                        ))
                    else:
                        lines.append("  - Fallback — zmiana dopasowania pojedynczego moda (bez profilu dawcy): {}.".format(
                            "; ".join("{} {:+.1f} pkt".format(slot, gain) for slot, gain in donor_moves)
                        ))
                assessment_detail = donor_assessments.get(str(item.get("owner", "") or ""), {})
                for change in item.get("setChanges", []):
                    lines.append("  - {}: {} pełnych setów ({} → {}).".format(
                        change.get("set", "set"),
                        change.get("status", "ZMIANA"),
                        change.get("beforeFull", 0),
                        change.get("afterFull", 0),
                    ))
                    if change.get("status") in ("ROZBITO", "OSŁABIONY"):
                        set_name = str(change.get("set", "") or "")
                        minor = next((x for x in assessment_detail.get("minor_set_changes", []) if x[0] == set_name), None)
                        major = next((x for x in assessment_detail.get("material_set_losses", []) if x[0] == set_name), None)
                        if major:
                            support = "brak profilu" if major[1] is None else "{:.1f}% kombinacji".format(major[1])
                            lines.append("    - ISTOTNA STRATA: set występuje w {} profilu SWGOH.GG.".format(support))
                        elif minor:
                            lines.append("    - ZMIANA NIEISTOTNA WG PROFILU: set występuje w {:.1f}% kombinacji SWGOH.GG.".format(minor[1]))
                if assessment_detail.get("value_delta", 0.0) < -0.05:
                    lines.append("  - ISTOTNY SPADEK wartości modów u dawcy.")
        else:
            lines.append("- Nie wykryto strat u dawców.")
        lines.append("")

    used_profile_ids = set(target_ids)
    for plan in chain_result.get("plans", []):
        selected_mod = plan.get("mod", {})
        if is_true(selected_mod.get("equipped")):
            selected_owner = str(selected_mod.get("assignedTo", "") or "")
            if selected_owner:
                used_profile_ids.add(aliases.get(selected_owner, selected_owner))
        for move in plan.get("moves", []):
            replacement = move.get("replacement", {})
            if is_true(replacement.get("equipped")):
                donor_owner = str(replacement.get("assignedTo", "") or "")
                if donor_owner:
                    used_profile_ids.add(aliases.get(donor_owner, donor_owner))
    if used_profile_ids:
        lines += ["## Kontrola profili użytych w łańcuchu", ""]
        for base_id in sorted(used_profile_ids):
            if base_id in profiles:
                source_count = len(profiles[base_id].get("source_model", {}).get("sources", []))
                lines.append("- {}: profil dostępny, {} źródła.".format(
                    display_name(base_id), source_count
                ))
            else:
                lines.append("- {}: brak profilu ({}).".format(
                    display_name(base_id), profile_fetch_status.get(base_id, "unavailable")
                ))
        lines.append("")

    lines += [
        "## Założenia projekcji",
        "",
        "- Poziom 15 jest traktowany jako osiągalny bez ograniczenia materiałami.",
        "- Brakujące secondary są liczone jako wartość średnia rolla, a nie maksymalna; ich przyszły przydział do statystyk jest uśredniony według profilu zamiast przypisywany do najlepszego secondary.",
        "- Slice i calibration nie wpływają na ranking ani wynik buildu. Mogą pojawić się wyłącznie jako osobne sugestie inwestycyjne i można je pominąć.",
        "- Primary pozostaje dokładnie na wartości z eksportu; zależy od obecnej liczby gwiazdek, a podniesienie moda do poziomu 15 go nie zmienia. Nie zakładamy slice 5★ → 6★.",
        "",
        "## Jak czytać opisy modów",
        "",
        "Każdy opis zawiera slot, set, primary, wszystkie dostępne secondary oraz gwiazdki, tier i poziom. "
        "Dzięki temu mod można znaleźć w grze bez korzystania z wewnętrznego ID.",
        "",
        "Plik CSV pozostaje technicznym zapleczem optymalizatora; nie jest instrukcją ręcznego przekładania.",
    ]
    return "\n".join(lines) + "\n"

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Analiza mody bez zmieniania konfiguracji farmy targets.json."
    )
    parser.add_argument(
        "--target",
        action="append",
        default=[],
        help="BASE_ID postaci do optymalizacji modów; można powtórzyć lub podać listę rozdzieloną przecinkami.",
    )
    args = parser.parse_args(argv)

    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(INPUT_FILE)

    with open(INPUT_FILE, newline="", encoding="utf-8-sig") as f:
        source = list(csv.DictReader(f))
    if not source:
        raise RuntimeError("mods.csv jest pusty.")

    targets = load_targets(args.target)
    profiles = load_profiles()
    aliases = load_player_aliases()
    names = load_player_names()
    protected_owners = load_protected_owners()
    protected_owners = {aliases.get(owner_id, owner_id) for owner_id in protected_owners}
    target_ids = {t.get("baseId") for t in targets if t.get("baseId")}
    known_roster_ids = {value for value in aliases.values() if value}
    unknown_target_ids = target_ids - known_roster_ids
    if unknown_target_ids:
        raise ValueError(
            "Nie znaleziono BASE_ID w aktualnym rosterze: {}".format(
                ", ".join(sorted(unknown_target_ids))
            )
        )
    target_source = "parametr --target" if args.target else "targets.json"
    profile_fetch_status = {}

    # Fetch target profiles first: without them the first full-build ranking
    # would be based on a fallback and could select the wrong mod slots.
    profiles, target_profile_status = ensure_profiles(target_ids, names)
    profile_fetch_status.update(target_profile_status)
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

    def display_name(owner_id):
        base_id = aliases.get(owner_id, owner_id)
        return names.get(owner_id) or names.get(base_id) or base_id or "nieznana"

    def rid(row):
        return str(row.get("id", "") or "")

    optimizer = optimize_target_build(rows, target_ids, profiles, aliases, names, protected_owners)

    # Resolve a provisional physical chain, fetch profiles only for owners
    # that actually appear in it, then re-run. Repeat if the improved ranking
    # selects a different donor. This avoids downloading profiles for the roster.
    attempted_profile_units = set(target_ids)
    while True:
        chain_result = apply_optimizer_replacements(
            rows, optimizer, target_ids, profiles, aliases, names, protected_owners
        )
        chain_donor_ids = set()

        # Inspect every selected source, not only successfully planned transfers.
        # A donor can be the reason a chain is blocked; it still needs a profile
        # check so an unavailable profile can trigger a safer alternative build.
        for opt in optimizer.values():
            for selected_mod in opt.get("mods", []):
                selected_owner = str(selected_mod.get("assignedTo", "") or "")
                if selected_owner:
                    chain_donor_ids.add(aliases.get(selected_owner, selected_owner))

        for plan in chain_result.get("plans", []):
            for move in plan.get("moves", []):
                replacement_mod = move.get("replacement", {})
                if is_true(replacement_mod.get("equipped")):
                    donor_owner = str(replacement_mod.get("assignedTo", "") or "")
                    if donor_owner:
                        chain_donor_ids.add(aliases.get(donor_owner, donor_owner))
        chain_donor_ids -= target_ids
        chain_donor_ids -= protected_owners
        missing_attempts = chain_donor_ids - attempted_profile_units
        if not missing_attempts:
            break

        additional_profiles, donor_profile_status = ensure_profiles(missing_attempts, names)
        profiles = merge_profiles(profiles, additional_profiles)
        profile_fetch_status.update(donor_profile_status)
        attempted_profile_units.update(missing_attempts)

        # Without a profile, donor impact cannot be evaluated. Protect that
        # owner for this run and rebuild the target from the remaining pool.
        newly_unavailable = unavailable_profile_ids(donor_profile_status) - protected_owners
        if newly_unavailable:
            protected_owners.update(newly_unavailable)
            labels = ", ".join(display_name(owner_id) for owner_id in sorted(newly_unavailable))
            print(
                "PROFILE GUARD: {} — brak profilu; postać wyłączona z puli dawców, "
                "ponowne wyszukiwanie modów.".format(labels)
            )

        # Re-score every mod and rebuild the target build with newly cached
        # donor profiles before validating the next physical chain.
        for row in rows:
            fit = character_fit(row, targets, profiles, aliases)
            row.update(fit)
        optimizer = optimize_target_build(rows, target_ids, profiles, aliases, names, protected_owners)

    # Mark the physical mods selected by the complete six-slot optimizer.
    # These values describe the full-build result, not a single-slot swap;
    # keeping that distinction prevents the Jar Jar candidate table from
    # displaying misleading zero gains for optimizer-selected mods.
    optimizer_selected = {}
    for target_id, opt in optimizer.items():
        for mod in opt.get("mods", []):
            optimizer_selected[str(mod.get("id", "") or "")] = {
                "target": target_id,
                "gain": float(opt.get("gain", 0.0)),
                "set_bonus": float(opt.get("setBonusScore", 0.0)),
                "mod_score": float(mod.get("optimizerScore", 0.0)),
            }
    for row in rows:
        selected = optimizer_selected.get(str(row.get("id", "") or ""))
        if selected:
            row["optimizerCandidate"] = True
            row["optimizerTarget"] = selected["target"]
            row["optimizerModScore"] = round(selected["mod_score"], 1)
            row["optimizerFullBuildGain"] = round(selected["gain"], 1)
            row["optimizerFullBuildSetBonus"] = round(selected["set_bonus"], 2)


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
        "W raportach przeznaczonych do ręcznego wykonania mod identyfikowany jest wyłącznie przez slot, set, primary, secondary, gwiazdki, tier i poziom; wewnętrzne ID nie są pokazywane.", "",
        "- Modów: **{}**".format(len(rows)),
        "- Cel(e) optymalizacji: **{}** (źródło: {})".format(
            ", ".join(sorted(target_ids)) or "brak", target_source
        ),
        "- UPGRADE: **{}**".format(counts.get("UPGRADE",0)),
        "- SLICE: **{}**".format(counts.get("SLICE",0)),
        "- SLICE_6E: **{}**".format(counts.get("SLICE_6E",0)),
        "- CALIBRATE: **{}**".format(counts.get("CALIBRATE",0)),
        "- EQUIP: **{}**".format(counts.get("EQUIP",0)),
        "- REPLACE: **{}**".format(counts.get("REPLACE",0)),
        "- PATCH: **{}**".format(counts.get("PATCH",0)),
        "- KEEP: **{}**".format(counts.get("KEEP",0)), "",
        "## Profile SWGOH.GG — lokalna baza", "",
        "Profile są przechowywane lokalnie i odświeżane tylko dla celu oraz dawców faktycznie wyznaczonego łańcucha transferów. Po pobraniu profili dawców łańcuch jest ponownie oceniany; jeśli zmieni się dawca, jego profil również zostanie sprawdzony. Cache jest uznawany za świeży przez 5 dni. Nieudane lub niepełne pobranie nie nadpisuje poprzedniego poprawnego profilu.", "",
        "| Postać (baseId) | Status |",
        "|---|---|",
        *["| {} | {} |".format(unit_id, status) for unit_id, status in sorted(profile_fetch_status.items())],
        "",
        "Dla dawców bez lokalnego profilu po próbie pobrania używany jest fallback modValue; nie jest to ocena dopasowania do indywidualnego profilu.", "",
        "## Globalny optimizer 6-slotowy", "",
        "Ocena kompletnego buildu: 40 pkt za statystyki główne, 60 pkt za maksymalnie 24 rolle secondary oraz bonusy setów ważone profilem postaci. Zgodność z profilem ma pierwszeństwo przed zachowaniem aktualnie założonych modów. Set nieobecny w profilu zachowuje 10% bazowej wagi bonusu; set z preferencją 100% otrzymuje pełną wagę. Zachowanie modów na celu jest dopiero końcowym tie-breakiem.", "",
        "Ranking kandydujących buildów używa oddzielnej projekcji: brakujące rolle do limitu aktualnego tieru są optymistycznie przypisywane do najwyżej preferowanej statystyki profilu; mod 5A na poziomie 15 jest dodatkowo przeliczany do 6E. To górna granica potencjału, nie prognoza RNG ani rzeczywiste statystyki moda. Primary pozostaje na wartości z eksportu, ponieważ nie mamy w danych tabeli jego przyrostu dla każdego poziomu. Raport pokazuje osobno wynik aktualny i wynik po projekcji.", "",
        "Bonus Speed Set używa bazowej szybkości 150, jeśli profil nie zawiera pola base_stats.Speed. Pozostałe bonusy procentowe są normalizowane względem maksymalnego rolla odpowiedniej statystyki.", "",
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

    for target_id, opt in optimizer.items():
        lines += [
            "", "### {} — najlepszy wirtualny build 6/6".format(target_id), "",
            "- Wynik buildu po projekcji: **{:.1f}** (lvl 15; 5A → 6E)".format(opt["totalScore"]),
            "- Aktualny build bez projekcji: **{:.1f}**".format(opt["currentScore"]),
            "- Aktualny build po tej samej projekcji: **{:.1f}**".format(opt["currentProjectedScore"]),
            "- Zmiana potencjału względem projekcji obecnego buildu: **{:+.1f}**".format(opt["gain"]),
            "- Bonus setów w ocenie: **{:.2f}**".format(opt["setBonusScore"]),
            "| Slot | Mod — parametry wyszukiwalne | Źródło | Fit |",
            "|---|---|---|---:|"
        ]
        for m in opt["mods"]:
            lines.append("| {} | {} | {} | {:.1f} |".format(
                m.get("slot",""), mod_description(m),
                source_label(m, aliases, names), score_profile(m, profiles[target_id])["fitScore"]))
    lines += ["", "## BEZPIECZNY ŁAŃCUCH — walidacja globalna", ""]
    if chain_result.get("safe"):
        lines.append("**STATUS: OK — transfery są fizycznie wykonalne i nie dublują modów.**")
        lines.append("Bilans pokazuje sumę modValue wyposażonych modów oraz pełne sety przed i po transferze. modValue jest wskaźnikiem jakości samych modów, a nie indywidualnym wynikiem buildu dawcy. Utrata wartości lub setu u dawcy nie blokuje ruchu; to jawna informacja do ręcznej decyzji.")
        lines.append("Wariant łańcucha wybierany jest na najkrótszym wykonalnym poziomie według fit profilu dawcy, następnie zmiany pełnych setów i sumy modValue. Istniejące sety nie są twardą ochroną. Każda zmiana liczby modów w secie i liczby pełnych grup jest wyszczególniona niżej dla każdej postaci w łańcuchu. Dla dawców bez własnego profilu fit korzysta z ogólnego modValue.")
    else:
        lines.append("**STATUS: BLOKADA — nie wygenerowano bezpiecznej listy ruchów.**")
        for target_id, reason in chain_result.get("failed", []):
            lines.append("- {}: {}".format(target_id, reason))
    lines += [
        "", "| Postać | Σ modValue przed | Σ modValue po | Δ modValue | Pełne sety przed | Pełne sety po |",
        "|---|---:|---:|---:|---|---|"
    ]
    affected_owners={p.get("target_owner") for p in chain_result.get("plans",[])}
    affected_owners.update(str(p["mod"].get("assignedTo","") or "") for p in chain_result.get("plans",[]) if p["mod"].get("assignedTo"))
    affected_owners.update(m.get("owner") for p in chain_result.get("plans",[]) for m in p.get("moves",[]))
    for item in chain_result.get("validation",[]):
        if item.get("owner") in affected_owners:
            before_groups = ", ".join("{}={}".format(k,v) for k,v in sorted(item["beforeGroups"].items()) if v) or "—"
            after_groups = ", ".join("{}={}".format(k,v) for k,v in sorted(item["afterGroups"].items()) if v) or "—"
            lines.append("| {} | {:.1f} | {:.1f} | {:+.1f} | {} | {} |".format(
                item["name"], item["beforeModValue"], item["afterModValue"],
                item["modValueDelta"], before_groups, after_groups))
    append_donor_combo_report(lines, chain_result.get("validation", []), affected_owners)
    lines += ["", "### Zmiany setów — każda postać w łańcuchu", "",
              "ROZBITO oznacza utratę co najmniej jednej pełnej grupy. BUDOWANY oznacza zwiększenie liczby modów danego setu bez ukończenia kolejnej grupy. UKOŃCZONO oznacza powstanie dodatkowej pełnej grupy. OSŁABIONY oznacza zmianę liczebności bez ukończenia lub rozbicia pełnej grupy.", "",
              "| Postać | Set | Zmiana liczby modów | Pełne sety | Status |",
              "|---|---|---:|---:|---|"]
    for item in chain_result.get("validation", []):
        if item.get("owner") not in affected_owners:
            continue
        for change in item.get("setChanges", []):
            lines.append("| {} | {} | {}/{} → {}/{} | {} → {} | {} |".format(
                item["name"], change["set"],
                change["beforeCount"], change["required"],
                change["afterCount"], change["required"],
                change["beforeFull"], change["afterFull"], change["status"]))
    if not any(item.get("setChanges") for item in chain_result.get("validation", []) if item.get("owner") in affected_owners):
        lines.append("| — | — | — | — | Bez zmian |")
    lines += ["", "### Ruchy — kolejność fizyczna", "",
              "**Ważne:** każdy mod jest przenoszony tylko raz. Najpierw właściwy mod z `Źródło` trafia **bezpośrednio** do celu. Dopiero potem wykonujemy PATCH-y. Ponieważ wyszukiwanie po postaci nie jest dostępne, każda operacja zawiera slot, set, primary, wszystkie dostępne secondary, liczbę gwiazdek, tier i poziom.", "",
              "| Krok | Typ | Operacja | Mod — parametry wyszukiwalne | Status |", "|---:|---|---|---|---|"]
    if (chain_result.get("safe")):
        step_no = 1
        for p in chain_result.get("plans",[]):
            m=p["mod"]
            source_id = str(m.get("assignedTo", "") or "")
            source_name = display_name(source_id) if source_id else "MAGAZYN"
            lines.append("| {} | MOD | {} → {} | {} | VALIDATED |".format(
                step_no, source_name, display_name(p["target_owner"]), mod_description(m)))
            step_no += 1
            patched_ids = {rid(move["replacement"]) for move in p.get("moves", [])}
            displaced = p.get("target_current")
            if displaced and rid(displaced) not in patched_ids:
                lines.append("| {} | RETURN | {} → MAGAZYN | {} | VALIDATED |".format(
                    step_no, display_name(p["target_owner"]), mod_description(displaced)))
                step_no += 1
            for move in p.get("moves", []):
                replacement = move["replacement"]
                src_name = display_name(str(replacement.get("assignedTo", "") or "")) if is_true(replacement.get("equipped")) else "MAGAZYN"
                lines.append("| {} | PATCH | {} → {} | {} | VALIDATED |".format(
                    step_no, src_name, move["name"], mod_description(replacement)))
                step_no += 1
    else:
        lines.append("| — | — | — | — | BLOCKED |")
    
    lines += [
        "", "## Definicje", "",
        "- **Quality** — jakość wykonanych rolli względem zakresu dla 5-dot/6-dot.",
        "- **Value** — jakość rolla pomnożona przez ogólną, niezależną od postaci użyteczność statystyki.",
        "- **Fit** — dopasowanie pojedynczego moda do aktywnego profilu celu; nie zawiera bonusu całego kompletu.",
        "- **SetBonusDelta** — zmiana rzeczywistego bonusu zestawów 6 modów celu po założeniu proponowanego moda.",
        "- **FitAfterSet** — Fit moda powiększony o SetBonusDelta; pokazuje wpływ kompletu bez mieszania go z jakością secondary.",
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

    user_report = render_user_report(
        rows, optimizer, chain_result, profiles, aliases, names,
        target_ids, profile_fetch_status, display_name
    )
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write(user_report if user_report.endswith("\n") else user_report + "\n")

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
