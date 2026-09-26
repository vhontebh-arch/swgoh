"""
SWGOH mod analyzer.
Input: mods.csv from generate_mods.py
Output: mod_analysis.csv and mod_analysis.md
"""

import csv
import os

INPUT_FILE = "mods.csv"
OUTPUT_CSV = "mod_analysis.csv"
OUTPUT_MD = "mod_analysis.md"

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

def integer(value, default=0):
    try: return int(value)
    except (TypeError, ValueError): return default

def number(value, default=0.0):
    try: return float(str(value).replace("%",""))
    except (TypeError, ValueError): return default

def rolls(row, i):
    stat = row.get("secondary{}Stat".format(i), "").strip()
    if not stat: return None
    count = integer(row.get("secondary{}Rolls".format(i), ""))
    value = number(row.get("secondary{}Value".format(i), ""))
    raw = row.get("secondary{}RawRolls".format(i), "")
    values = []
    for item in raw.split("|"):
        if not item: continue
        try: raw_value = float(item)
        except ValueError: continue
        if stat in {"Health","Protection","Offense","Defense","Speed"}:
            values.append(raw_value / 10000.0)
        else:
            values.append(raw_value / 100.0)
    if not values and count:
        values = [value / count] * count
    return stat, value, count, values

# Secondary-stat value weights are deliberately generic. Character-specific
# profiles are layered on top when targets/profiles are available.
STAT_VALUE = {
    "Speed": 1.00,
    "Offense %": 0.92,
    "Offense": 0.82,
    "Health %": 0.72,
    "Protection %": 0.70,
    "Health": 0.48,
    "Protection": 0.48,
    "Defense %": 0.42,
    "Defense": 0.34,
    "Potency %": 0.34,
    "Tenacity %": 0.30,
    "Critical Chance %": 0.25,
    "Critical Damage %": 0.25,
    "Critical Avoidance %": 0.20,
    "Speed %": 0.15,
}

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
    q = quality(stat, value, count, values, dots)
    return q * STAT_VALUE.get(stat, 0.10)

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
    # For the generic model, future rolls go to the most valuable existing
    # secondary. Character-specific optimization can override this later.
    if not sec_stats:
        return 0.0
    return max(STAT_VALUE.get(x[0], 0.10) for x in sec_stats)

def next_action(row, secs, current_quality, current_value, potential):
    dots = integer(row.get("dots"))
    tier = integer(row.get("tier"))
    level = integer(row.get("level"))
    speed = next((x for x in secs if x[0] == "Speed"), None)
    speed_rolls = speed[2] if speed else 0

    if level < 12:
        return ("UPGRADE", "nieujawnione wszystkie secondary")

    if level < 15:
        if current_value >= 35 or speed:
            return ("UPGRADE", "dokończenie do 15 ma dodatnią wartość oczekiwaną")
        return ("KEEP", "zbyt słaby profil przed 15")

    if dots == 5 and tier < 5:
        if speed_rolls >= 2 or (current_value >= 43 and potential >= 58):
            return ("SLICE", "wartość secondary uzasadnia kolejny roll")
        if current_value >= 35 and potential >= 52:
            return ("KEEP", "obserwuj przed wydaniem materiałów")
        return ("KEEP", "wartość secondary zbyt niska")

    if dots == 5 and tier == 5:
        six_e = projected_6e_quality(secs)
        if speed_rolls >= 2 or six_e >= 50 or (current_value >= 45 and len(secs) >= 3):
            return ("SLICE_6E", "5A ma wystarczającą wartość do 6E")
        return ("KEEP", "5A nie uzasadnia kosztu 6E")

    if dots == 6 and tier < 5:
        if speed_rolls >= 3 or (current_value >= 52 and potential >= 65):
            return ("SLICE", "6-dot ma dobry profil do kolejnego rolla")
        return ("KEEP", "brak wystarczającej wartości do kolejnego slice")

    if dots == 6 and tier == 5:
        if speed_rolls >= 3 or current_value >= 58:
            return ("CALIBRATE", "6A ma wartość uzasadniającą calibration")
        return ("KEEP", "6A nie wymaga obecnie inwestycji")

    return ("KEEP", "brak dalszej inwestycji")

def analyze(row):
    dots = integer(row.get("dots"))
    tier = integer(row.get("tier"))
    level = integer(row.get("level"))
    secs = [x for i in range(1, 5) if (x := rolls(row, i)) is not None]

    total = sum(x[2] for x in secs)
    current_quality, current_value = quality_metrics(secs, dots)
    target_total = TOTAL.get((dots, tier), total)
    remaining = max(0, target_total-total)

    # Potential ceiling is now value-aware: perfect future rolls are assigned
    # to the strongest currently present secondary.
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

    action, reason = next_action(
        row, secs, current_quality, current_value, potential_value
    )

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
        "recommendedAction": action,
        "reason": reason,
        "nextInvestment": investment(row),
        "calibrationAttemptsMax": calibration_max,
        "calibrationAttemptsUsed": calibration_used,
        "calibrationAttemptsRemaining": calibration_remaining,
        "calibrationHitChancePct": calibration_hit_chance if calibration_max else 0.0,
        "calibrationNextCost": calibration_next_cost,
    })
    return out

def main():
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(INPUT_FILE)
    with open(INPUT_FILE,newline="",encoding="utf-8-sig") as f:
        source = list(csv.DictReader(f))
    if not source: raise RuntimeError("mods.csv jest pusty.")

    rows = [analyze(row) for row in source]

    with open(OUTPUT_CSV,"w",newline="",encoding="utf-8-sig") as f:
        fields = list(rows[0].keys())
        writer = csv.DictWriter(f,fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

    order = {"CALIBRATE":0,"SLICE_6E":1,"SLICE":2,"UPGRADE":3,"KEEP":4}
    rows.sort(key=lambda r:(order.get(r["recommendedAction"],9),
                            -float(r["potentialCeiling"]),
                            -float(r["modQuality"])))
    counts = {}
    for r in rows: counts[r["recommendedAction"]] = counts.get(r["recommendedAction"],0)+1

    lines = [
        "# Analiza modów","",
        "Model rozdziela **jakość obecnych rolli**, **potencjał dalszego rozwoju** "
        "i **rodzaj następnej inwestycji**.","",
        "- Modów: **{}**".format(len(rows)),
        "- UPGRADE: **{}**".format(counts.get("UPGRADE",0)),
        "- SLICE: **{}**".format(counts.get("SLICE",0)),
        "- SLICE_6E: **{}**".format(counts.get("SLICE_6E",0)),
        "- CALIBRATE: **{}**".format(counts.get("CALIBRATE",0)),
        "- KEEP: **{}**".format(counts.get("KEEP",0)),"",
        "## Najważniejsi kandydaci","",
        "| Akcja | Mod | Set | Tier | Lvl | Quality | Value | 6E proj. | Speed | Potencjał | Inwestycja |",
        "|---|---|---|---|---:|---:|---:|---:|---|"
    ]
    for r in rows[:75]:
        mod = "{} {} {}".format(r["slot"],r["primaryStat"],r["primaryValue"])
        lines.append("| {} | {} | {} | {}{} | {} | {:.1f}% | {:.1f}% | {:.1f}% | {} |".format(
            r["recommendedAction"],mod,r["set"],r["dots"],r["tierName"],
            r["level"],float(r["modQuality"]),float(r["modValue"]),float(r["projected6EQuality"]),
            float(r["speedQuality"]),float(r["potentialCeiling"]),r["nextInvestment"]))
    lines += [
        "","## Definicje","",
        "- **Quality** — jakość wykonanych rolli względem zakresu dla 5-dot/6-dot.",
        "- **Value** — jakość rolla pomnożona przez ogólną użyteczność statystyki; oddziela „dobry roll” od „dobrego secondary”.",
        "- **Potential** — sufit wartości przy idealnych przyszłych rollach; nie jest prognozą RNG.",
        "- **UPGRADE** — mod nie jest jeszcze na 15.",
        "- **SLICE** — kolejny tier ma uzasadnienie jakościowe.",
        "- **SLICE_6E** — 5A jest oceniane również przez projekcję jakości po wzroście statystyk do 6E.",
        "- **CALIBRATE** — 6A jest na końcu slicing i może korzystać z calibration.",
        "- **Calibration hit chance** — 25% normalnie; 33,3%, gdy jeden secondary ma już 5 rolli i nie może dostać kolejnego.",
        "",
        "Calibration pozostaje losowe: wybrany roll jest usuwany z wybranego secondary, "
        "a nowy roll trafia losowo do dostępnych secondary. Analyzer wskazuje "
        "kandydatów, ale nie udaje, że zna wynik konkretnej próby."
    ]
    with open(OUTPUT_MD,"w",encoding="utf-8") as f:
        f.write("\\n".join(lines)+"\\n")

    print("="*80)
    print("SWGOH MOD ANALYZER")
    print("="*80)
    print("Modów:",len(rows))
    for action in ("UPGRADE","SLICE","SLICE_6E","CALIBRATE","KEEP"):
        print("{:<12}: {}".format(action,counts.get(action,0)))
    print("CSV:",OUTPUT_CSV)
    print("REPORT:",OUTPUT_MD)

if __name__ == "__main__":
    main()
