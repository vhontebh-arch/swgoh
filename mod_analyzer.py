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
    five_roll_stats = sum(1 for x in secs if x[2] >= 5)
    calibration_hit_chance = 33.3 if five_roll_stats else 25.0
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
        "calibrationHitChancePct": calibration_hit_chance if calibration_max else 0.0,
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
    path = "swgoh_972824625.json"
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            player = json.load(f)
    except Exception:
        return {}

    aliases = {}
    for unit in player.get("rosterUnit", []):
        definition = str(unit.get("definitionId", "") or "")
        base_id = definition.split(":", 1)[0]
        unit_id = str(unit.get("id", "") or "")
        for value in (base_id, unit_id, definition):
            if value:
                aliases[value] = base_id
    return aliases

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
            secs.append((q * 100.0, pref, count))

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

def apply_replacements(rows, target_base_ids):
    equipped_by_target_slot = {}
    for row in rows:
        if not row.get("equipped"):
            continue
        target = row.get("fitTarget", "")
        if target in target_base_ids:
            key = (target, row.get("slot", ""))
            current = equipped_by_target_slot.get(key)
            if current is None or float(row.get("fitScore", 0)) > float(current.get("fitScore", 0)):
                equipped_by_target_slot[key] = row

    for row in rows:
        if row.get("characterFit") != "CANDIDATE":
            continue
        if integer(row.get("level")) < 15 or integer(row.get("dots")) < 5:
            continue
        target = row.get("fitTarget", "")
        current = equipped_by_target_slot.get((target, row.get("slot", "")))
        if current is None:
            continue
        gain = float(row.get("fitScore", 0)) - float(current.get("fitScore", 0))
        row["replacementGain"] = round(gain, 1)
        row["replacesModId"] = current.get("id", "")
        if gain >= 8.0:
            row["recommendedAction"] = "REPLACE"
            row["reason"] = "kandydat jest wyraźnie lepszy od obecnego moda na tym samym slocie"

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

    apply_replacements(rows, {t.get("baseId") for t in targets})

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        fields = list(rows[0].keys())
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    order = {"REPLACE":0,"CALIBRATE":1,"SLICE_6E":2,"SLICE":3,"UPGRADE":4,"KEEP":5}
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
        "- REPLACE: **{}**".format(counts.get("REPLACE",0)),
        "- KEEP: **{}**".format(counts.get("KEEP",0)), "",
        "## Najważniejsi kandydaci", "",
        "| Akcja | Mod | Set | Tier | Lvl | Quality | Value | Fit | 6E proj. | Speed | Potencjał | Inwestycja |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|"
    ]

    for r in rows[:75]:
        mod = "{} {} {}".format(r["slot"], r["primaryStat"], r["primaryValue"])
        lines.append(
            "| {} | {} | {} | {}{} | {} | {:.1f}% | {:.1f}% | {:.1f}% | {:.1f}% | {:.1f}% | {:.1f}% | {} |".format(
                r["recommendedAction"], mod, r["set"], r["dots"], r["tierName"],
                r["level"], float(r["modQuality"]), float(r["modValue"]),
                float(r.get("fitScore",0)), float(r["projected6EQuality"]),
                float(r["speedQuality"]), float(r["potentialCeiling"]), r["nextInvestment"]
            )
        )

    lines += [
        "", "## Definicje", "",
        "- **Quality** — jakość wykonanych rolli względem zakresu dla 5-dot/6-dot.",
        "- **Value** — jakość rolla pomnożona przez ogólną, niezależną od postaci użyteczność statystyki.",
        "- **Fit** — dopasowanie moda do profilu konkretnej postaci; dla nieprzypisanych modów pokazuje najlepszego aktywnego kandydata.",
        "- **Potential** — sufit wartości przy idealnych przyszłych rollach; nie jest prognozą RNG.",
        "- **REPLACE** — niezałożony mod jest wyraźnie lepszy od obecnego moda tej samej postaci i slotu.",
        "- **UPGRADE** — mod nie jest jeszcze na 15.",
        "- **SLICE** — kolejny tier ma uzasadnienie jakościowe lub profilowe.",
        "- **SLICE_6E** — 5A jest oceniane również przez projekcję jakości po wzroście statystyk do 6E.",
        "- **CALIBRATE** — 6A jest na końcu slicing i może korzystać z calibration.",
        "- **Calibration hit chance** — model pomocniczy; nie oznacza gwarancji konkretnego wyniku.",
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
    for action in ("UPGRADE","SLICE","SLICE_6E","CALIBRATE","KEEP"):
        print("{:<12}: {}".format(action, counts.get(action,0)))
    print("CSV:", OUTPUT_CSV)
    print("REPORT:", OUTPUT_MD)

if __name__ == "__main__":
    main()
