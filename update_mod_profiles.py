"""Read-only profile cache adapter used by mod_analyzer.

Profile refresh is deliberately manual: see MOD_PROFILE_REFRESH.md.
This module only returns requested cached profiles and never performs network
requests or writes to mod_profiles.json.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROFILE_FILE = Path("mod_profiles.json")


def profile_cache_status(profile, now=None, max_age_days=5):
    """Return fresh, stale, or incomplete using the agreed five-day/two-source rule."""
    if not isinstance(profile, dict):
        return "incomplete"
    model = profile.get("source_model", {}) or {}
    sources = model.get("sources", [])
    expected = {"Top 1000 Kyber GAC", "Top 100 Guilds"}
    if not isinstance(sources, list) or not expected.issubset({
        str(source.get("name", "")) for source in sources if isinstance(source, dict)
    }):
        return "incomplete"
    for source in sources:
        if not isinstance(source, dict):
            return "incomplete"
        combos = source.get("set_combinations_pct") or source.get("set_combinations")
        primary = source.get("primary_pct")
        secondary = source.get("secondary_focus") or source.get("secondary_focus_avg")
        if not isinstance(combos, dict) or not combos:
            return "incomplete"
        if not isinstance(primary, dict) or not primary:
            return "incomplete"
        if not isinstance(secondary, dict) or len(secondary) < 4:
            return "incomplete"
    for key in ("set_combinations", "primary_preferences", "secondary_preferences"):
        if not isinstance(profile.get(key), dict) or not profile[key]:
            return "incomplete"

    raw_timestamp = model.get("fetched_at_utc") or model.get("refreshed_at_utc")
    if not raw_timestamp:
        source_timestamps = [
            source.get("fetched_at_utc") or source.get("refreshed_at_utc")
            for source in sources
        ]
        if not all(source_timestamps):
            return "incomplete"
        raw_timestamp = min(source_timestamps)

    try:
        fetched_at = datetime.fromisoformat(str(raw_timestamp).replace("Z", "+00:00"))
        if fetched_at.tzinfo is None:
            fetched_at = fetched_at.replace(tzinfo=timezone.utc)
        fetched_at = fetched_at.astimezone(timezone.utc)
    except (TypeError, ValueError):
        return "incomplete"

    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    now = now.astimezone(timezone.utc)
    if fetched_at > now + timedelta(minutes=5):
        return "incomplete"
    if now - fetched_at > timedelta(days=max_age_days):
        return "stale"
    return "fresh"


def load_fresh_profiles(now=None, max_age_days=5):
    """Load every complete cached profile still valid under the five-day rule."""
    try:
        data = json.loads(PROFILE_FILE.read_text(encoding="utf-8"))
        stored = data.get("profiles", {})
        if not isinstance(stored, dict):
            return {}
    except (OSError, json.JSONDecodeError, ValueError):
        return {}
    return {
        str(base_id): profile
        for base_id, profile in stored.items()
        if profile_cache_status(profile, now=now, max_age_days=max_age_days) == "fresh"
    }


def ensure_profiles(base_ids, names=None):
    """Return only requested cached profiles and a per-unit availability status."""
    names = names or {}
    try:
        data = json.loads(PROFILE_FILE.read_text(encoding="utf-8"))
        stored = data.get("profiles", {})
        if not isinstance(stored, dict):
            raise ValueError("nieprawidłowa sekcja profiles")
    except (OSError, json.JSONDecodeError, ValueError):
        stored = {}

    profiles = {}
    status = {}
    for base_id in sorted({str(value) for value in base_ids if value}):
        profile = stored.get(base_id)
        if isinstance(profile, dict):
            profiles[base_id] = profile
            status[base_id] = "cached"
        else:
            label = names.get(base_id, base_id)
            status[base_id] = "unavailable"
            print(f"PROFILE CACHE: {label} ({base_id}) — brak profilu; wymagany ręczny odczyt SWGOH.GG.")
    return profiles, status
