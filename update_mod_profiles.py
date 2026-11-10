"""Read-only profile cache adapter used by mod_analyzer.

Profile refresh is deliberately manual: see MOD_PROFILE_REFRESH.md.
This module only returns requested cached profiles and never performs network
requests or writes to mod_profiles.json.
"""
from __future__ import annotations

import json
from pathlib import Path

PROFILE_FILE = Path("mod_profiles.json")


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
