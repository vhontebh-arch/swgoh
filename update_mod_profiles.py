#!/usr/bin/env python3
"""
Refresh mod_profiles.json from the live SWGOH.GG Best Mods pages.

GitHub Actions runners receive HTTP 403 from SWGOH.GG/Cloudflare. The updater
therefore uses Jina Reader as a fetch proxy and parses the resulting text.
Nothing is written until every configured profile and both source slices pass
validation, so a failed refresh leaves the last known-good profile untouched.
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

PROFILE_FILE = Path("mod_profiles.json")
TIMEOUT = 45
USER_AGENT = "Mozilla/5.0 (compatible; Vhonte-SWGOH-Mod-Analyzer/1.0)"

SLOTS = {
    "Arrow": "Best Arrow Mod",
    "Triangle": "Best Triangle Mod",
    "Circle": "Best Circle Mod",
    "Cross": "Best Cross Mod",
}

STAT_NAMES = [
    "Speed", "Potency", "Protection", "Protection %", "Health", "Health %",
    "Offense", "Offense %", "Defense", "Defense %", "Tenacity %",
    "Critical Chance %", "Critical Damage %", "Critical Avoidance %", "Accuracy",
]

KNOWN_SETS = [
    "Critical Chance", "Critical Damage", "Defense", "Health", "Offense",
    "Potency", "Speed", "Tenacity",
]


def fetch(url):
    # SWGOH.GG blocks GitHub-hosted runners directly. Use several public
    # read-through proxies; the first working response wins.
    encoded = quote(url, safe="")
    candidates = [
        "https://swgoh-gg.translate.goog/" + url.split("swgoh.gg/", 1)[1]
        + "?_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=en",
        "https://api.allorigins.win/raw?url=" + encoded,
        "https://corsproxy.io/?url=" + encoded,
        "https://r.jina.ai/" + url,
        "https://r.jina.ai/http://" + url.split("://", 1)[1],
    ]
    last_error = None

    for endpoint in candidates:
        try:
            req = Request(endpoint, headers={"User-Agent": USER_AGENT})
            with urlopen(req, timeout=TIMEOUT) as response:
                raw = response.read().decode("utf-8", errors="replace")

            if len(raw) < 2000:
                raise RuntimeError(f"odpowiedź zbyt krótka ({len(raw)} B)")

            # Proxies may return HTML instead of Jina markdown.
            if "<html" in raw.lower() or "<body" in raw.lower():
                raw = re.sub(r"(?is)<script.*?</script>", " ", raw)
                raw = re.sub(r"(?is)<style.*?</style>", " ", raw)
                raw = re.sub(r"(?s)<[^>]+>", " ", raw)
                raw = re.sub(r"&nbsp;", " ", raw)
                raw = re.sub(r"&amp;", "&", raw)

            if "Best Mods" not in raw and "Specific Mod Sets" not in raw:
                raise RuntimeError("odpowiedź nie zawiera danych Best Mods")

            print(f"  źródło pobrania: {endpoint.split('/')[2]}")
            return raw

        except Exception as exc:
            last_error = exc
            print(f"  próba nieudana: {endpoint.split('/')[2]}: {exc}")

    raise RuntimeError(f"nie udało się pobrać {url}: {last_error}")


def pct(value):
    return float(str(value).replace(",", "."))


def extract_between(text, start_marker, end_markers):
    start = text.find(start_marker)
    if start < 0:
        return ""
    start += len(start_marker)
    end = len(text)
    for marker in end_markers:
        pos = text.find(marker, start)
        if pos >= 0:
            end = min(end, pos)
    return text[start:end]


def parse_set_combinations(text):
    start = text.find("Specific Mod Sets")
    if start < 0:
        start = text.find("Best Mod Set")
    if start < 0:
        raise RuntimeError("brak sekcji Specific Mod Sets")

    window = text[start:]
    # The primary-stat section starts at the first slot heading.
    positions = [window.find("\nArrow"), window.find("\n### Arrow"), window.find("\n## Arrow")]
    positions = [p for p in positions if p >= 0]
    if positions:
        window = window[:min(positions)]

    set_name = r"(?:" + "|".join(re.escape(x) for x in KNOWN_SETS) + r")"
    pattern = re.compile(
        r"((?:" + set_name + r")(?:\s*\+\s*(?:" + set_name + r")){1,2})"
        r"\s+(\d+(?:\.\d+)?)%"
    )

    result = {}
    for match in pattern.finditer(window):
        key = re.sub(r"\s*\+\s*", " + ", match.group(1)).strip()
        result[key] = pct(match.group(2))

    if not result:
        raise RuntimeError("nie odczytano kombinacji setów")
    return result


def parse_slot(text, slot):
    heading = SLOTS[slot]
    start = text.find(heading)
    if start < 0:
        # Jina may omit the exact heading prefix.
        start = text.find("### " + heading)
    if start < 0:
        raise RuntimeError(f"brak sekcji {heading}")

    end_markers = []
    for other in SLOTS:
        if other == slot:
            continue
        end_markers.extend([SLOTS[other], "### " + SLOTS[other]])

    window = extract_between(text, heading, end_markers)

    result = {}
    # Tables are normally rendered as:
    # Speed | 890 | 96.31%
    # Also accept plain text lines.
    for stat in STAT_NAMES:
        pattern = re.compile(
            r"\b" + re.escape(stat) +
            r"\s*(?:\||\s+)\s*(?:\d[\d,]*\s*(?:\||\s+))?"
            r"(\d+(?:\.\d+)?)%"
        )
        m = pattern.search(window)
        if m:
            result[stat] = pct(m.group(1))

    if not result:
        raise RuntimeError(f"{slot}: brak primary stats")
    return result


def parse_secondary(text):
    start = text.find("Secondary Stat Focus")
    if start < 0:
        raise RuntimeError("brak Secondary Stat Focus")

    end = text.find("Average Stats", start)
    if end < 0:
        end = len(text)
    window = text[start:end]

    result = {}
    for stat in STAT_NAMES:
        patterns = [
            re.compile(
                re.escape(stat) +
                r"\s*\+\s*(\d+(?:\.\d+)?)%?\s+avg\s+(\d+(?:\.\d+)?)%"
            ),
            re.compile(
                re.escape(stat) +
                r"\s*\|\s*\+?(\d+(?:\.\d+)?)%?\s*\|\s*(\d+(?:\.\d+)?)%"
            ),
        ]
        for pattern in patterns:
            m = pattern.search(window)
            if m:
                result[stat] = {
                    "average": pct(m.group(1)),
                    "focus_pct": pct(m.group(2)),
                }
                break

    if not result:
        raise RuntimeError("brak danych secondary")
    return result


def normalize_source(url, label):
    text = clean(fetch(url))

    if "Best Mods" not in text:
        raise RuntimeError(f"{label}: odpowiedź nie wygląda na stronę Best Mods")

    sets = parse_set_combinations(text)
    primary = {slot: parse_slot(text, slot) for slot in SLOTS}
    secondary = parse_secondary(text)

    return {
        "name": label,
        "url": url,
        "set_combinations": sets,
        "primary_pct": primary,
        "secondary_focus_avg": secondary,
    }


def average_maps(a, b):
    keys = set(a) | set(b)
    return {
        key: round((float(a.get(key, 0)) + float(b.get(key, 0))) / 2.0, 4)
        for key in keys
    }


def build_profile(existing, sources):
    sets = average_maps(
        sources[0]["set_combinations"],
        sources[1]["set_combinations"],
    )

    primary = {}
    for slot in SLOTS:
        primary[slot] = average_maps(
            sources[0]["primary_pct"].get(slot, {}),
            sources[1]["primary_pct"].get(slot, {}),
        )

    secondary = {}
    for stat in set(sources[0]["secondary_focus_avg"]) | set(sources[1]["secondary_focus_avg"]):
        a = sources[0]["secondary_focus_avg"].get(stat, {})
        b = sources[1]["secondary_focus_avg"].get(stat, {})
        secondary[stat] = {
            "average": round((a.get("average", 0) + b.get("average", 0)) / 2.0, 4),
            "focus_pct": round((a.get("focus_pct", 0) + b.get("focus_pct", 0)) / 2.0, 4),
        }

    set_preference_raw = {}
    for combo, prevalence in sets.items():
        for set_name in combo.split(" + "):
            set_preference_raw[set_name] = (
                set_preference_raw.get(set_name, 0.0) + prevalence
            )
    max_set = max(set_preference_raw.values(), default=1.0)
    set_preferences = {
        key: round(value / max_set, 4)
        for key, value in set_preference_raw.items()
    }

    primary_preferences = {}
    for slot, values in primary.items():
        total = sum(values.values()) or 1.0
        primary_preferences[slot] = {
            key: round(value / total, 4)
            for key, value in values.items()
        }

    focus_values = {
        key: value["focus_pct"] for key, value in secondary.items()
    }
    max_focus = max(focus_values.values(), default=1.0)
    secondary_preferences = {
        key: round(value / max_focus, 4)
        for key, value in focus_values.items()
    }
    for stat in STAT_NAMES:
        secondary_preferences.setdefault(stat, 0.0)

    return {
        "name": existing.get("name", "Unknown"),
        "role": existing.get("role", ""),
        "source_model": {
            "method": "live SWGOH.GG Best Mods pages via Jina Reader; equal-weight average of configured slices",
            "refreshed_at_utc": datetime.now(timezone.utc).isoformat(),
            "sources": sources,
        },
        "set_combinations": sets,
        "set_preferences": set_preferences,
        "primary_preferences": primary_preferences,
        "secondary_preferences": secondary_preferences,
    }


def validate_profile(profile):
    required_sets = {"Speed", "Potency"}
    if not required_sets.intersection(profile.get("set_preferences", {})):
        raise RuntimeError("profil nie zawiera oczekiwanych setów Speed/Potency")

    for slot in SLOTS:
        values = profile.get("primary_preferences", {}).get(slot, {})
        if not values or max(values.values()) <= 0:
            raise RuntimeError(f"profil: brak użytecznych primary dla {slot}")

    secondary = profile.get("secondary_preferences", {})
    if secondary.get("Speed", 0) <= 0:
        raise RuntimeError("profil: brak preferencji Speed")


def main():
    if not PROFILE_FILE.exists():
        raise RuntimeError("Brak mod_profiles.json")

    data = json.loads(PROFILE_FILE.read_text(encoding="utf-8"))
    profiles = data.get("profiles", {})
    if not profiles:
        raise RuntimeError("Brak profili")

    new_profiles = {}

    for base_id, existing in profiles.items():
        source_cfg = existing.get("source_model", {}).get("sources", [])
        if len(source_cfg) < 2:
            raise RuntimeError(f"{base_id}: profil wymaga dwóch źródeł SWGOH.GG")

        sources = []
        for source in source_cfg[:2]:
            url = source["url"]
            label = source.get("name", url)
            print(f"Pobieranie {base_id}: {label}")
            parsed = normalize_source(url, label)
            sources.append(parsed)
            print(
                f"  sety={len(parsed['set_combinations'])}, "
                f"primary={sum(len(v) for v in parsed['primary_pct'].values())}, "
                f"secondary={len(parsed['secondary_focus_avg'])}"
            )

        profile = build_profile(existing, sources)
        validate_profile(profile)
        new_profiles[base_id] = profile

    # Atomic write only after ALL profiles pass. A failed refresh therefore
    # leaves the previous file exactly as it was.
    new_data = dict(data)
    new_data["profiles"] = new_profiles
    rendered = json.dumps(new_data, ensure_ascii=False, indent=2) + "\n"

    PROFILE_FILE.write_text(rendered, encoding="utf-8")
    print("OK: mod_profiles.json odświeżony")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
