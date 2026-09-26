#!/usr/bin/env python3
"""
Refresh character mod profiles from the live SWGOH.GG Best Mods pages.

The file keeps the source URLs and a normalized snapshot so the analyzer never
depends on manually-entered SWGOH.GG numbers. The workflow refreshes this file
before every mod analysis run.
"""

import json
import re
import sys
from html import unescape
from pathlib import Path
from urllib.request import Request, urlopen

PROFILE_FILE = Path("mod_profiles.json")
USER_AGENT = "Mozilla/5.0 (compatible; Vhonte-SWGOH-Mod-Analyzer/1.0)"

STAT_NAMES = [
    "Speed", "Potency", "Protection", "Protection %", "Health", "Health %",
    "Offense", "Offense %", "Defense", "Defense %", "Tenacity %",
    "Critical Chance %", "Critical Damage %", "Critical Avoidance %", "Speed %",
]

SLOTS = {
    "Arrow": "Best Arrow Mod",
    "Triangle": "Best Triangle Mod",
    "Circle": "Best Circle Mod",
    "Cross": "Best Cross Mod",
}


def fetch(url):
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=30) as response:
        raw = response.read().decode("utf-8", errors="replace")
    # Strip scripts/styles before extracting visible text.
    raw = re.sub(r"<script\\b[^>]*>.*?</script>", " ", raw, flags=re.I | re.S)
    raw = re.sub(r"<style\\b[^>]*>.*?</style>", " ", raw, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", raw)
    text = unescape(text)
    return re.sub(r"\\s+", " ", text).strip()


def pct(value):
    try:
        return float(value)
    except ValueError:
        return 0.0


def section(text, heading, next_headings):
    start = text.find(heading)
    if start < 0:
        return ""
    start += len(heading)
    end = len(text)
    for h in next_headings:
        pos = text.find(h, start)
        if pos >= 0:
            end = min(end, pos)
    return text[start:end]


def parse_pairs(text, names):
    escaped = "|".join(re.escape(x) for x in sorted(names, key=len, reverse=True))
    pattern = re.compile(r"(" + escaped + r")\\s+([0-9]+(?:\\.[0-9]+)?)%")
    result = {}
    for match in pattern.finditer(text):
        result[match.group(1)] = pct(match.group(2))
    return result


def parse_primary(text, slot):
    headings = list(SLOTS.values())
    current = SLOTS[slot]
    window = section(text, current, [h for h in headings if h != current])
    # The heading is followed by the explanatory sentence and then the table.
    pairs = parse_pairs(window, STAT_NAMES)
    return pairs


def parse_set_combinations(text):
    start = text.find("Specific Mod Sets")
    if start < 0:
        start = text.find("Best Mod Set")
    if start < 0:
        return {}

    end = text.find("Arrow", start)
    if end < 0:
        end = min(len(text), start + 7000)
    window = text[start:end]

    # Set names can contain '+'. Restrict to the set names currently present
    # in the game and retain the first occurrence of each combination.
    known = [
        "Speed", "Potency", "Health", "Protection", "Offense", "Defense",
        "Tenacity", "Critical Chance", "Critical Damage"
    ]
    name = r"(?:" + "|".join(re.escape(x) for x in known) + r")"
    combo = re.compile(r"((?:" + name + r")(?:\\s*\\+\\s*(?:" + name + r")){1,2})\\s+([0-9]+(?:\\.[0-9]+)?)%")
    result = {}
    for match in combo.finditer(window):
        key = re.sub(r"\\s*\\+\\s*", " + ", match.group(1))
        if key not in result:
            result[key] = pct(match.group(2))
    return result


def parse_secondary(text):
    start = text.find("Secondary Stat Focus")
    if start < 0:
        return {}
    end = text.find("Average Stats", start)
    if end < 0:
        end = min(len(text), start + 6000)
    window = text[start:end]
    result = {}
    for stat in STAT_NAMES:
        # SWGOH.GG presents e.g. 'Speed +20.1 avg 20.9%' or
        # 'Potency +5.64% avg 10.72%'.
        pat = re.compile(
            re.escape(stat) +
            r"\\s+\\+?([0-9]+(?:\\.[0-9]+)?)%?\\s+avg\\s+([0-9]+(?:\\.[0-9]+)?)%"
        )
        m = pat.search(window)
        if m:
            result[stat] = {"average": pct(m.group(1)), "focus_pct": pct(m.group(2))}
            continue
        pat2 = re.compile(
            re.escape(stat) +
            r"\\s+\\+?([0-9]+(?:\\.[0-9]+)?)\\s+avg\\s+([0-9]+(?:\\.[0-9]+)?)%"
        )
        m = pat2.search(window)
        if m:
            result[stat] = {"average": pct(m.group(1)), "focus_pct": pct(m.group(2))}
    return result


def normalize_source(url, label):
    text = fetch(url)
    if "Best Mods" not in text and "Player Data" not in text:
        raise RuntimeError(f"{label}: nie rozpoznano strony SWGOH.GG")

    sets = parse_set_combinations(text)
    primaries = {slot: parse_primary(text, slot) for slot in SLOTS}
    secondary = parse_secondary(text)

    if not sets:
        raise RuntimeError(f"{label}: nie odczytano żadnych kombinacji setów")
    if not all(primaries.values()):
        missing = [k for k, v in primaries.items() if not v]
        raise RuntimeError(f"{label}: brak primary dla {missing}")
    if not secondary:
        raise RuntimeError(f"{label}: brak Secondary Stat Focus")

    return {
        "name": label,
        "url": url,
        "set_combinations": sets,
        "primary_pct": primaries,
        "secondary_focus_avg": secondary,
    }


def average_dict(a, b):
    keys = set(a) | set(b)
    return {k: round((float(a.get(k, 0)) + float(b.get(k, 0))) / 2.0, 4) for k in keys}


def build_profile(existing, sources):
    set_combinations = average_dict(
        sources[0]["set_combinations"], sources[1]["set_combinations"]
    )

    primary = {}
    for slot in SLOTS:
        primary[slot] = average_dict(
            sources[0]["primary_pct"].get(slot, {}),
            sources[1]["primary_pct"].get(slot, {}),
        )

    secondary_raw = {}
    for stat in set(sources[0]["secondary_focus_avg"]) | set(sources[1]["secondary_focus_avg"]):
        a = sources[0]["secondary_focus_avg"].get(stat, {})
        b = sources[1]["secondary_focus_avg"].get(stat, {})
        secondary_raw[stat] = {
            "average": round((a.get("average", 0) + b.get("average", 0)) / 2.0, 4),
            "focus_pct": round((a.get("focus_pct", 0) + b.get("focus_pct", 0)) / 2.0, 4),
        }

    # Keep the analyzer weights normalized to the observed prevalence. This
    # makes the values comparable between refreshes instead of hard-coding
    # subjective weights.
    set_preferences = {}
    for combo, prevalence in set_combinations.items():
        for set_name in combo.split(" + "):
            set_preferences[set_name] = set_preferences.get(set_name, 0.0) + prevalence
    max_set = max(set_preferences.values(), default=1.0)
    set_preferences = {k: round(v / max_set, 4) for k, v in set_preferences.items()}

    primary_preferences = {}
    for slot, values in primary.items():
        total = sum(values.values()) or 1.0
        primary_preferences[slot] = {
            k: round(v / total, 4) for k, v in values.items()
        }

    focus_values = {k: v["focus_pct"] for k, v in secondary_raw.items()}
    max_focus = max(focus_values.values(), default=1.0)
    secondary_preferences = {
        k: round(v / max_focus, 4) for k, v in focus_values.items()
    }

    # Preserve zero entries for known stats so analyzer output stays stable.
    for stat in STAT_NAMES:
        secondary_preferences.setdefault(stat, 0.0)

    return {
        "name": existing.get("name", "Unknown"),
        "role": existing.get("role", ""),
        "source_model": {
            "method": "live SWGOH.GG Best Mods pages; equal-weight average of the two configured slices",
            "refreshed_at_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
            "sources": sources,
        },
        "set_combinations": set_combinations,
        "set_preferences": set_preferences,
        "primary_preferences": primary_preferences,
        "secondary_preferences": secondary_preferences,
    }


def main():
    if not PROFILE_FILE.exists():
        raise RuntimeError("Brak mod_profiles.json")

    data = json.loads(PROFILE_FILE.read_text(encoding="utf-8"))
    profiles = data.get("profiles", {})
    if not profiles:
        raise RuntimeError("Brak profili")

    for base_id, profile in profiles.items():
        source_cfg = profile.get("source_model", {}).get("sources", [])
        if len(source_cfg) < 2:
            raise RuntimeError(f"{base_id}: profil nie ma dwóch źródeł SWGOH.GG")

        urls = [s["url"] for s in source_cfg[:2]]
        labels = [s.get("name", f"source-{i+1}") for i, s in enumerate(source_cfg[:2])]
        print(f"Odświeżanie profilu {base_id}...")
        sources = [normalize_source(url, label) for url, label in zip(urls, labels)]
        profiles[base_id] = build_profile(profile, sources)

    data["profiles"] = profiles
    PROFILE_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print("OK: mod_profiles.json odświeżony z live SWGOH.GG")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
