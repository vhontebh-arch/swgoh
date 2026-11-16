#!/usr/bin/env python3
"""Fetch SWGOH.GG relic counts and release dates; build reusable ranking data."""
from __future__ import annotations

import csv
import json
import re
import sys
import time
from datetime import date, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import URLError
from urllib.parse import quote, urlsplit
from urllib.request import Request, urlopen

from character_ranking import rank_characters, load_character_data

RELIC_URL = "https://swgoh.gg/characters/relic-player-data/"
RELEASE_URL = "https://swgoh.gg/units/releases/"
USER_AGENT = "Mozilla/5.0 (compatible; SWGOHCharacterRanking/1.0)"
TODAY = date.today()


def normalize(value: str) -> str:
    value = value.casefold().replace("&", "and")
    return re.sub(r"[^a-z0-9]+", "", value)


class TableParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows = []
        self.row = None
        self.cell = None
        self.in_cell = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "tr":
            self.row = []
        elif tag in ("td", "th") and self.row is not None:
            self.cell = {"text": [], "hrefs": []}
            self.row.append(self.cell)
            self.in_cell = True
        elif tag == "a" and self.in_cell and self.cell is not None:
            href = attrs.get("href")
            if href:
                self.cell["hrefs"].append(href)

    def handle_endtag(self, tag):
        if tag in ("td", "th"):
            self.in_cell = False
            self.cell = None
        elif tag == "tr" and self.row is not None:
            if self.row:
                self.rows.append(self.row)
            self.row = None
            self.cell = None
            self.in_cell = False

    def handle_data(self, data):
        if self.in_cell and self.cell is not None:
            self.cell["text"].append(data)


def cell_text(cell):
    return " ".join(" ".join(cell["text"]).split())


def fetch_page(url: str) -> str:
    parsed = urlsplit(url)
    path = parsed.path.lstrip("/")
    translated = (
        "https://swgoh-gg.translate.goog/" + path
        + "?_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=en"
    )
    encoded = quote(url, safe="")
    candidates = [
        url,
        translated,
        "https://corsproxy.io/?url=" + encoded,
        "https://api.codetabs.com/v1/proxy?quest=" + encoded,
        "https://r.jina.ai/http://" + parsed.netloc + parsed.path,
        "https://api.allorigins.win/raw?url=" + encoded,
    ]
    errors = []
    for endpoint in candidates:
        try:
            request = Request(endpoint, headers={"User-Agent": USER_AGENT})
            with urlopen(request, timeout=60) as response:
                body = response.read().decode("utf-8", errors="replace")
            if len(body) < 5000:
                raise RuntimeError("response unexpectedly short")
            if "SWGOH.GG" not in body and "relic-player-data" not in body and "Unit Releases" not in body:
                # Some proxy readers return plain text, which is still acceptable
                # when the expected table heading is present.
                expected = "Relic Player Data" if "relic-player-data" in url else "Unit Releases"
                if expected not in body:
                    raise RuntimeError("expected SWGOH.GG page marker not found")
            print(f"Fetched {url} via {urlsplit(endpoint).netloc}: {len(body)} bytes")
            return body
        except Exception as exc:
            errors.append(f"{urlsplit(endpoint).netloc}: {exc}")
    raise RuntimeError("Unable to fetch page: " + "; ".join(errors))


def parse_rows(html: str):
    parser = TableParser()
    parser.feed(html)
    return parser.rows


def unit_slug(row) -> str | None:
    for cell in row:
        for href in cell["hrefs"]:
            match = re.search(r"/units/([^/]+)/?", href)
            if match:
                return match.group(1)
    return None


def parse_release_dates(html: str):
    dates = {}
    names = {}
    for row in parse_rows(html):
        if len(row) < 2:
            continue
        slug = unit_slug(row)
        if not slug:
            continue
        name = cell_text(row[0])
        released = cell_text(row[1])
        if not name or not released:
            continue
        match = re.search(r"([A-Z][a-z]{2})\s+(\d{1,2}),\s+(\d{4})", released)
        if match:
            parsed = date.fromisoformat(
                f"{match.group(3)}-{datetime.strptime(match.group(1), '%b').month:02d}-{int(match.group(2)):02d}"
            )
            if parsed <= TODAY:
                dates[slug] = parsed.isoformat()
                names[slug] = name
        elif "At launch" in released:
            dates[slug] = None
            names[slug] = name
    if len(dates) < 150:
        raise RuntimeError(f"Release table validation failed: only {len(dates)} dated/launch units")
    return dates, names


def parse_relic_counts(html: str):
    rows = parse_rows(html)
    header = None
    result = {}
    for row in rows:
        labels = [cell_text(cell).strip().lower() for cell in row]
        if "unit" in labels and "r5" in labels and "r10" in labels:
            header = labels
            continue
        if not header or len(row) < len(header):
            continue
        slug = unit_slug(row)
        if not slug:
            continue
        values = {header[i]: cell_text(row[i]) for i in range(min(len(header), len(row)))}
        counts = {}
        for tier in range(1, 11):
            key = f"r{tier}"
            raw = values.get(key, "").replace(",", "").replace(" ", "")
            if not raw.isdigit():
                counts = {}
                break
            counts[key] = int(raw)
        if counts:
            result[slug] = {
                "name": cell_text(row[0]),
                "counts": counts,
            }
    if len(result) < 150:
        raise RuntimeError(f"Relic table validation failed: only {len(result)} character rows")
    return result


def localized_name(unit, localization):
    key = unit.get("nameKey") or unit.get("name_key")
    if not key:
        return None
    value = localization.get(key)
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        for candidate in ("text", "value", "name"):
            if isinstance(value.get(candidate), str):
                return value[candidate]
    return None


def build_base_id_map(game_path: Path, localization_path: Path):
    game = json.loads(game_path.read_text(encoding="utf-8"))
    localization = json.loads(localization_path.read_text(encoding="utf-8"))
    units = game.get("units", [])
    mapping = {}
    for unit in units:
        if unit.get("combatType") != 1:
            continue
        base_id = unit.get("baseId")
        name = localized_name(unit, localization)
        if base_id and name:
            key = normalize(name)
            if key in mapping and mapping[key] != base_id:
                raise RuntimeError(f"Ambiguous game-data name: {name}")
            mapping[key] = base_id
    if len(mapping) < 200:
        raise RuntimeError(f"Game-data name map unexpectedly small: {len(mapping)}")
    return mapping


# Known display-name differences between SWGOH.GG and game localization.
NAME_ALIASES = {
    "garazebzeborrelios": "zeborrelios",
    "ahsokatano(snips)": "ahsokatano",
    "chirrutimwe": "chirrutimwe",
    "ct210408echo": "echo",
    "ct7567rex": "rex",
    "ct5555fives": "fives",
    "cc2224cody": "cody",
    "themandalorianbeskararmor": "themandalorianbeskararmor",
}


def main():
    relic_html = fetch_page(RELIC_URL)
    release_html = fetch_page(RELEASE_URL)
    relic = parse_relic_counts(relic_html)
    release_dates, release_names = parse_release_dates(release_html)
    name_to_base = build_base_id_map(Path("data.json"), Path("localization.json"))

    output = []
    unmatched = []
    for slug, item in relic.items():
        key = normalize(item["name"])
        release_date = release_dates.get(key)
        if key not in release_dates:
            # Some pages use slightly different display strings; try the
            # release-page slug mapping when the row has a profile link.
            release_key = next((candidate for candidate, name in release_names.items()
                                if normalize(name) == key), None)
            if release_key is None:
                unmatched.append((slug, item["name"], "no release-date row"))
                continue
            key = release_key
            release_date = release_dates[key]
        key = NAME_ALIASES.get(key, key)
        base_id = name_to_base.get(key)
        if not base_id:
            # Try the relic table's display name as a second exact key.
            base_id = name_to_base.get(normalize(item["name"]))
        release_name = release_names.get(key, item["name"])
        if not base_id:
            unmatched.append((slug, release_name, "no game-data baseId match"))
            continue

        counts = item["counts"]
        r5 = sum(counts[f"r{i}"] for i in range(5, 11))
        r7 = sum(counts[f"r{i}"] for i in range(7, 11))
        r9 = sum(counts[f"r{i}"] for i in range(9, 11))
        output.append({
            "baseId": base_id,
            "name": release_name,
            "release_date": release_date or "",
            "global_relic_r5_plus_players": r5,
            "global_relic_r7_plus_players": r7,
            "global_relic_r9_plus_players": r9,
            "swgoh_gg_slug": slug,
            "source_updated": datetime.now().astimezone().isoformat(timespec="seconds"),
        })

    if len(output) < 150:
        raise RuntimeError(f"Too few matched characters: {len(output)}")
    if len(unmatched) > max(10, int(len(relic) * 0.08)):
        sample = "; ".join(f"{slug}:{name} ({why})" for slug, name, why in unmatched[:20])
        raise RuntimeError(f"Too many unmatched characters ({len(unmatched)}): {sample}")

    fields = list(output[0])
    with Path("character_counts.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(output)

    metadata = {
        "source": {
            "relic_player_data": RELIC_URL,
            "release_dates": RELEASE_URL,
            "retrieved_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "r5_plus_definition": "R5 + R6 + R7 + R8 + R9 + R10",
            "r7_plus_definition": "R7 + R8 + R9 + R10",
            "r9_plus_definition": "R9 + R10",
        },
        "characters": {
            row["baseId"]: {"release_date": row["release_date"] or None,
                            "swgoh_gg_slug": row["swgoh_gg_slug"]}
            for row in output
        },
        "unmatched_rows": [
            {"slug": slug, "name": name, "reason": reason}
            for slug, name, reason in unmatched
        ],
    }
    Path("character_release_dates.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    rows = load_character_data("character_counts.csv", "character_release_dates.json")
    ranking = rank_characters(rows, as_of=TODAY)
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "sources": metadata["source"],
        "method": {
            "global_weight": 0.55,
            "age_adjusted_weight": 0.45,
            "cohort_days": 365,
            "minimum_cohort_size": 5,
            "tier_weights": {"r5_plus": 0.50, "r7_plus": 0.30, "r9_plus": 0.20},
        },
        "characters": ranking,
        "unmatched_rows": metadata["unmatched_rows"],
    }
    Path("character_ranking.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Matched characters: {len(output)}")
    print(f"Unmatched relic rows: {len(unmatched)}")
    print(f"Age-adjusted: {sum(1 for item in ranking if item['age_adjustment_applied'])}")
    print("Top 20:")
    for item in ranking[:20]:
        print(f"{item['rank']:>3}. {item['name']:<34} {item['rank_score']:>7.2f} "
              f"(global {item['global_score']:>6.2f}, cohort {item['age_adjusted_score']})")
    print("Recent releases:")
    recent = sorted((item for item in ranking if item["release_date"]),
                    key=lambda item: item["release_date"], reverse=True)[:20]
    for item in recent:
        print(f"{item['release_date']} {item['name']:<34} {item['rank_score']:>7.2f} "
              f"rank {item['rank']}")


if __name__ == "__main__":
    main()
