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

def quality(stat, value, count, values, dots):
    if not count: return 0.0
    low_high = (R6 if dots >= 6 else R5).get(stat)
    if not low_high: return 0.0
    low, high = low_high
    if values:
        q = [max(0.0,min(1.0,(v-low)/(high-low))) for v in values]
        return sum(q)/len(q)
    per = value/count
    return max(0.0,min(1.0,(per-low)/(high-low)))

def investment(row):
    dots,tier,level = integer(row.get("dots")),integer(row.get("tier")),integer(row.get("level"))
    if level < 15: return "level {}->15".format(level)
    if dots == 5 and tier < 5: return "5{}->5{}".format(TIER.get(tier,"?"),TIER.get(tier+1,"?"))
    if dots == 5 and tier == 5: return "5A->6E"
    if dots == 6 and tier < 5: return "6{}->6{}".format(TIER.get(tier,"?"),TIER.get(tier+1,"?"))
    return "calibration"

def analyze(row):
    dots = integer(row.get("dots"))
    tier = integer(row.get("tier"))
    level = integer(row.get("level"))
    secs = [x for i in range(1,5) if (x := rolls(row,i)) is not None]
    total = sum(x[2] for x in secs)
    current = 100.0 * sum(quality(*x,dots)*x[2] for x in secs)/total if total else 0.0
    target_total = TOTAL.get((dots,tier), total)
    remaining = max(0, target_total-total)
    potential = 100.0 * (current*total/100.0 + remaining) / max(1,total+remaining)

    speed = next((x for x in secs if x[0]=="Speed"), None)
    speed_value = speed[1] if speed else 0.0
    speed_rolls = speed[2] if speed else 0
    speed_quality = min(100.0,100.0*speed_value/(6.0*speed_rolls)) if speed_rolls else 0.0
    useful = {"Speed","Offense","Offense %","Health %","Protection %",
              "Potency %","Tenacity %","Defense","Defense %","Health",
              "Protection","Critical Chance %"}
    useful_count = sum(1 for x in secs if x[0] in useful)

    if level < 12:
        action = "UPGRADE" if speed or current >= 55 else "KEEP"
        reason = "ujawnij wszystkie secondary przed oceną"
    elif level < 15:
        action = "UPGRADE" if speed or current >= 52 else "KEEP"
        reason = "warto dokończyć do 15" if action=="UPGRADE" else "brak jakości do dalszej inwestycji"
    elif dots == 5 and tier < 5:
        if speed_rolls >= 2 or (current >= 58 and potential >= 72):
            action, reason = "SLICE", "sensowny kolejny slice"
        elif current >= 48 and potential >= 65 and useful_count >= 2:
            action, reason = "SLICE", "co najmniej dwa użyteczne secondary i dobry potencjał"
        else:
            action, reason = "KEEP", "potencjał zbyt niski na kolejny slice"
    elif dots == 5 and tier == 5:
        if current >= 58 or speed_rolls >= 2:
            action, reason = "SLICE_6E", "5A warte podbicia do 6E"
        else:
            action, reason = "KEEP", "5A bez wystarczającej jakości do 6E"
    elif dots == 6 and tier < 5:
        if speed_rolls >= 3 or (current >= 62 and potential >= 78):
            action, reason = "SLICE", "dobry kandydat do kolejnego 6-dot slice"
        else:
            action, reason = "KEEP", "brak jakości do kolejnego slice"
    elif dots == 6 and tier == 5:
        if speed_rolls >= 3 or (current >= 70 and len(secs) >= 3):
            action, reason = "CALIBRATE", "6A nadaje się do przenoszenia rolli"
        else:
            action, reason = "KEEP", "6A bez wystarczającej jakości do calibration"
    else:
        action, reason = "KEEP", "brak dalszej inwestycji"

    out = dict(row)
    out.update({
        "tierName": TIER.get(tier, "?"),
        "secondaryRollsTotal": total,
        "secondaryRollsMaxAtTier": target_total,
        "secondaryRollsRemainingAtTier": remaining,
        "modQuality": round(current,1),
        "speedQuality": round(speed_quality,1),
        "potentialCeiling": round(potential,1),
        "potentialGain": round(max(0,potential-current),1),
        "recommendedAction": action,
        "reason": reason,
        "nextInvestment": investment(row),
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
        "| Akcja | Mod | Set | Tier | Lvl | Quality | Speed | Potencjał | Inwestycja |",
        "|---|---|---|---|---:|---:|---:|---:|---|"
    ]
    for r in rows[:75]:
        mod = "{} {} {}".format(r["slot"],r["primaryStat"],r["primaryValue"])
        lines.append("| {} | {} | {} | {}{} | {} | {:.1f}% | {:.1f}% | {:.1f}% | {} |".format(
            r["recommendedAction"],mod,r["set"],r["dots"],r["tierName"],
            r["level"],float(r["modQuality"]),float(r["speedQuality"]),
            float(r["potentialCeiling"]),r["nextInvestment"]))
    lines += [
        "","## Definicje","",
        "- **Quality** — jakość wykonanych rolli względem zakresu dla 5-dot/6-dot.",
        "- **Potential** — sufit przy idealnych przyszłych rollach; nie jest prognozą RNG.",
        "- **UPGRADE** — mod nie jest jeszcze na 15.",
        "- **SLICE** — kolejny tier ma uzasadnienie jakościowe.",
        "- **SLICE_6E** — 5A ma sens do podbicia do 6E.",
        "- **CALIBRATE** — 6A jest na końcu slicing i może korzystać z calibration.",
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
