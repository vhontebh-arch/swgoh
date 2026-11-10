#!/usr/bin/env python3
"""
Refresh mod_profiles.json from the live SWGOH.GG Best Mods pages.

GitHub Actions runners receive HTTP 403 from SWGOH.GG/Cloudflare. The updater
therefore uses proxy readers and parses the resulting text. Nothing is written
until every configured profile and both source slices pass validation.
"""

import argparse
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import quote, urlsplit, urlunsplit
from urllib.request import Request, urlopen

PROFILE_FILE = Path("mod_profiles.json")
TIMEOUT = 20
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
    parsed = urlsplit(url)
    target_path = parsed.path.lstrip("/")
    translate_query = (
        ("?" + parsed.query if parsed.query else "")
        + ("&" if parsed.query else "?")
        + "_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=en"
    )
    translate_endpoint = (
        "https://swgoh-gg.translate.goog/"
        + target_path
        + translate_query
    )

    encoded = quote(url, safe="")
    candidates = [
        translate_endpoint,
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


def clean(text):
    text = re.sub(r"\r", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


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
    positions = [window.find("\nArrow"), window.find("\n### Arrow"), window.find("\n## Arrow")]
    positions = [p for p in positions if p >= 0]
    if positions:
        window = window[:min(positions)]

    set_name = r"(?: " + "|".join(re.escape(x) for x in KNOWN_SETS) + r")".replace(" ", "")
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
    for stat in STAT_NAMES:
        pattern = re.compile(
            r"\b" + re.escape(stat) +
            r"\b\s*(?:\||:|–|—|-)?\s*"
            r"(?:\d[\d,]*\s*(?:\||:|–|—|-)?\s*)?"
            r"(\d+(?:\.\d+)?)\s*%"
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
    sets = average_maps(sources[0]["set_combinations"], sources[1]["set_combinations"])

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
            set_preference_raw[set_name] = set_preference_raw.get(set_name, 0.0) + prevalence
    max_set = max(set_preference_raw.values(), default=1.0)
    set_preferences = {key: round(value / max_set, 4) for key, value in set_preference_raw.items()}

    primary_preferences = {}
    for slot, values in primary.items():
        total = sum(values.values()) or 1.0
        primary_preferences[slot] = {key: round(value / total, 4) for key, value in values.items()}

    focus_values = {key: value["focus_pct"] for key, value in secondary.items()}
    max_focus = max(focus_values.values(), default=1.0)
    secondary_preferences = {key: round(value / max_focus, 4) for key, value in focus_values.items()}
    for stat in STAT_NAMES:
        secondary_preferences.setdefault(stat, 0.0)

    return {
        "name": existing.get("name", "Unknown"),
        "role": existing.get("role", ""),
        "source_model": {
            "method": "live SWGOH.GG Best Mods pages via proxy readers; equal-weight average of configured slices",
            "refreshed_at_utc": datetime.now(timezone.utc).isoformat(),
            "sources": sources,
        },
        "set_combinations": sets,
        "set_preferences": set_preferences,
        "primary_preferences": primary_preferences,
        "secondary_preferences": secondary_preferences,
    }


def validate_profile(profile):
    set_preferences = profile.get("set_preferences", {})
    if not set_preferences or max((float(v) for v in set_preferences.values()), default=0) <= 0:
        raise RuntimeError("profil: brak użytecznych preferencji setów")

    for slot in SLOTS:
        values = profile.get("primary_preferences", {}).get(slot, {})
        if not values or max((float(v) for v in values.values()), default=0) <= 0:
            raise RuntimeError(f"profil: brak użytecznych primary dla {slot}")

    secondary = profile.get("secondary_preferences", {})
    if not secondary or max((float(v) for v in secondary.values()), default=0) <= 0:
        raise RuntimeError("profil: brak użytecznych preferencji secondary")



CACHE_MAX_AGE_DAYS = 90


def read_roster_names():
    names = {}
    path = Path("roster.csv")
    if path.exists():
        with path.open(newline="", encoding="utf-8-sig") as handle:
            for row in csv.DictReader(handle):
                base_id = str(row.get("baseId", "") or "").strip()
                name = str(row.get("name", "") or "").strip()
                if base_id and name:
                    names[base_id] = name
    return names


def profile_is_fresh(profile, max_age_days=CACHE_MAX_AGE_DAYS, now=None):
    stamp = profile.get("source_model", {}).get("refreshed_at_utc", "")
    try:
        fetched = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        if fetched.tzinfo is None:
            fetched = fetched.replace(tzinfo=timezone.utc)
        current = now or datetime.now(timezone.utc)
        return current - fetched <= timedelta(days=max_age_days)
    except (TypeError, ValueError):
        return False


def profile_source_urls(name, existing):
    configured = existing.get("source_model", {}).get("sources", [])
    if len(configured) >= 2 and all(item.get("url") for item in configured[:2]):
        return configured[:2]
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if not slug:
        raise RuntimeError("nie można utworzyć adresu SWGOH.GG bez nazwy postaci")
    base = "https://swgoh.gg/units/{}/best-mods/".format(slug)
    return [
        {"name": "Top 1000 Kyber GAC", "url": base},
        {"name": "Top 100 Guilds", "url": base + "?s=GUILDTOP100"},
    ]


def atomic_save(data):
    path = PROFILE_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def refresh_one(base_id, name, existing):
    source_cfg = profile_source_urls(name, existing)
    sources = []
    for source in source_cfg[:2]:
        url = source["url"]
        label = source.get("name", url)
        print("Pobieranie {}: {}".format(base_id, label))
        parsed = normalize_source(url, label)
        previous_secondary = source.get("secondary_focus_avg", {})
        for stat, value in previous_secondary.items():
            parsed["secondary_focus_avg"].setdefault(stat, value)
        sources.append(parsed)
        print("  sety={}, primary={}, secondary={}".format(
            len(parsed["set_combinations"]),
            sum(len(v) for v in parsed["primary_pct"].values()),
            len(parsed["secondary_focus_avg"]),
        ))
    profile = build_profile(existing, sources)
    profile["name"] = name or profile.get("name") or base_id
    validate_profile(profile)
    return profile


def ensure_profiles(base_ids, names=None, max_age_days=CACHE_MAX_AGE_DAYS):
    """Load cached profiles and refresh only requested missing/stale units.

    A failed or incomplete fetch never replaces an existing valid cached profile.
    Successful profiles are atomically persisted one by one. Network work is
    limited to three concurrent profile refreshes.
    """
    if PROFILE_FILE.exists():
        data = json.loads(PROFILE_FILE.read_text(encoding="utf-8"))
    else:
        data = {}
    profiles = data.setdefault("profiles", {})
    statuses = data.setdefault("profile_status", {})
    names = names or read_roster_names()
    result = {}
    pending = {}

    for base_id in sorted(set(str(x).strip() for x in base_ids if str(x).strip())):
        existing = profiles.get(base_id, {})
        name = names.get(base_id) or existing.get("name") or base_id
        cache_valid = False
        if existing:
            try:
                validate_profile(existing)
                cache_valid = True
            except Exception:
                cache_valid = False
        if cache_valid and profile_is_fresh(existing, max_age_days):
            result[base_id] = "cached"
        else:
            pending[base_id] = (name, existing)

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(refresh_one, base_id, name, existing): base_id
            for base_id, (name, existing) in pending.items()
        }
        for future in as_completed(futures):
            base_id = futures[future]
            name, existing = pending[base_id]
            try:
                refreshed = future.result()
                profiles[base_id] = refreshed
                statuses[base_id] = {
                    "status": "refreshed",
                    "checked_at_utc": datetime.now(timezone.utc).isoformat(),
                    "fetched_at_utc": refreshed["source_model"]["refreshed_at_utc"],
                    "source": "SWGOH.GG",
                }
                result[base_id] = "refreshed"
                atomic_save(data)
            except Exception as exc:
                # Keep an older valid profile untouched; record the failed attempt separately.
                statuses[base_id] = {
                    "status": "stale_fallback" if existing else "unavailable",
                    "checked_at_utc": datetime.now(timezone.utc).isoformat(),
                    "fetched_at_utc": existing.get("source_model", {}).get("refreshed_at_utc"),
                    "source": "local_cache" if existing else "none",
                    "error": "{}: {}".format(type(exc).__name__, exc),
                }
                result[base_id] = statuses[base_id]["status"]
                atomic_save(data)
                print("UWAGA {}: {}".format(base_id, exc), file=sys.stderr)

    if result:
        atomic_save(data)
    return profiles, result


def main():
    parser = argparse.ArgumentParser(description="Odśwież lokalną bazę profili SWGOH.GG.")
    parser.add_argument("--units", default="", help="Lista baseId oddzielona przecinkami; puste = wszystkie zapisane profile.")
    parser.add_argument("--max-age-days", type=int, default=CACHE_MAX_AGE_DAYS)
    args = parser.parse_args()

    if args.units.strip():
        requested = [item.strip() for item in args.units.split(",") if item.strip()]
    else:
        if not PROFILE_FILE.exists():
            raise RuntimeError("Brak mod_profiles.json")
        data = json.loads(PROFILE_FILE.read_text(encoding="utf-8"))
        requested = list(data.get("profiles", {}).keys())

    if not requested:
        raise RuntimeError("Nie wskazano postaci do odświeżenia.")

    profiles, statuses = ensure_profiles(
        requested, read_roster_names(), max_age_days=max(0, args.max_age_days)
    )
    for base_id, status in statuses.items():
        print("{}: {}".format(base_id, status))
    unavailable = [base_id for base_id, status in statuses.items() if status == "unavailable"]
    if unavailable:
        print("UWAGA: nie udało się pobrać profili: {}".format(", ".join(unavailable)))
        print("Poprawnie pobrane profile i statusy błędów zostały zachowane w lokalnej bazie.")
    print("OK: lokalna baza zawiera {} profili".format(len(profiles)))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
