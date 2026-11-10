#!/usr/bin/env python3
"""Read-only guard for a single, explicitly declared SWGOH mod-optimizer run.

This tool never fetches profiles, edits files, or expands the requested character
set. The caller must provide one target and zero or more actual chain donors.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BRANCH = "optimizer-v2"
TTL = timedelta(days=5)
REQUIRED_DOCS = (
    "OPTIMIZER_WORK_PROTOCOL.md",
    "MOD_OPTIMIZATION_RULES.md",
    "MOD_PROFILE_REFRESH.md",
    "GRANDIVORY_METHOD_REVIEW.md",
)


def normalize(value: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", str(value).upper())


def current_branch() -> str:
    env_branch = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME")
    if env_branch:
        return env_branch
    try:
        return subprocess.check_output(
            ["git", "branch", "--show-current"], cwd=ROOT, text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def parse_time(value):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except (TypeError, ValueError):
        return None


def profile_is_complete(profile: dict) -> tuple[bool, str]:
    if not isinstance(profile, dict):
        return False, "brak rekordu profilu"
    for key in ("set_preferences", "primary_preferences", "secondary_preferences"):
        if not isinstance(profile.get(key), dict) or not profile[key]:
            return False, "brak/niekompletne pole " + key
    source_model = profile.get("source_model") or {}
    sources = source_model.get("sources")
    if not isinstance(sources, list) or len(sources) < 2:
        return False, "brak dwóch surowych źródeł"
    for index, source in enumerate(sources[:2], start=1):
        if not isinstance(source, dict):
            return False, f"źródło {index}: nieprawidłowy rekord"
        if not (source.get("set_combinations_pct") or source.get("set_combinations")):
            return False, f"źródło {index}: brak kombinacji setów"
        if not isinstance(source.get("primary_pct"), dict) or not source["primary_pct"]:
            return False, f"źródło {index}: brak primary stats"
        focus = source.get("secondary_focus") or source.get("secondary_focus_avg")
        if not isinstance(focus, dict) or len(focus) < 4:
            return False, f"źródło {index}: brak TOP 4 secondary focus"
    return True, "kompletny"


def inspect_profiles(names: list[str], path: Path, now=None) -> list[str]:
    now = now or datetime.now(timezone.utc)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"FAIL: nie można odczytać {path.name}: {exc}"]

    profiles = data.get("profiles", {})
    statuses = data.get("profile_status", {})
    if not isinstance(profiles, dict) or not isinstance(statuses, dict):
        return ["FAIL: nieprawidłowa struktura profiles/profile_status"]

    profile_index = {normalize(k): (k, v) for k, v in profiles.items()}
    status_index = {normalize(k): v for k, v in statuses.items()}
    errors = []
    for name in names:
        key = normalize(name)
        match = profile_index.get(key)
        if not match:
            errors.append(f"FAIL: {name}: brak profilu (wymaga odczytu obu źródeł)")
            continue
        stored_key, profile = match
        complete, reason = profile_is_complete(profile)
        if not complete:
            errors.append(f"FAIL: {name}: {reason} (wymaga uzupełnienia obu źródeł)")
            continue

        status = status_index.get(key, {})
        source_model = profile.get("source_model") or {}
        timestamp = (
            status.get("fetched_at_utc")
            or source_model.get("fetched_at_utc")
            or source_model.get("refreshed_at_utc")
        )
        fetched = parse_time(timestamp)
        if fetched is None:
            errors.append(f"FAIL: {name}: brak poprawnego fetched_at_utc/refreshed_at_utc")
            continue
        age = now - fetched
        if age > TTL:
            errors.append(
                f"FAIL: {name}: profil starszy niż 5 dni "
                f"(pobrano {fetched.isoformat()}; checked_at_utc nie odnawia TTL)"
            )
            continue
        errors.append(f"PASS: {name}: {stored_key}, świeży i kompletny")
    return errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Read-only SWGOH optimizer preflight")
    parser.add_argument("--target", required=True, help="jedna postać docelowa tej analizy")
    parser.add_argument(
        "--donor", action="append", default=[],
        help="rzeczywisty dawca w bieżącym łańcuchu; można podać wielokrotnie",
    )
    parser.add_argument("--profiles", default=str(ROOT / "mod_profiles.json"))
    args = parser.parse_args(argv)

    names = [args.target, *args.donor]
    if any(not name.strip() for name in names):
        print("FAIL: puste nazwy postaci")
        return 2
    if len({normalize(name) for name in names}) != len(names):
        print("FAIL: cel/dawca powtórzony; zakres musi być jednoznaczny")
        return 2

    failures = 0
    branch = current_branch()
    if branch != BRANCH:
        print(f"FAIL: branch={branch or '(nieznany)'}; wymagany {BRANCH}")
        failures += 1
    else:
        print(f"PASS: branch={branch}")

    for doc in REQUIRED_DOCS:
        if (ROOT / doc).is_file():
            print(f"PASS: dokument {doc}")
        else:
            print(f"FAIL: brak dokumentu {doc}")
            failures += 1

    print("Zakres profili: " + ", ".join(names))
    results = inspect_profiles(names, Path(args.profiles))
    for result in results:
        print(result)
        if result.startswith("FAIL:"):
            failures += 1

    if failures:
        print(f"PRE-FLIGHT BLOCKED: {failures} kontrola/e niezaliczona/e.")
        return 1
    print("PRE-FLIGHT PASS: można rozpocząć analizę; narzędzie nie zmieniło żadnych danych.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
