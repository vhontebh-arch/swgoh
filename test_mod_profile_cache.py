import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import update_mod_profiles as profiles


def valid_profile(timestamp=None):
    timestamp = timestamp or datetime.now(timezone.utc).isoformat()
    source = lambda name: {
        "name": name,
        "set_combinations_pct": {"Speed + Health": 100.0},
        "primary_pct": {"Arrow": {"Speed": 100.0}},
        "secondary_focus": {
            "Speed": {"average": 10.0, "focus_pct": 100.0},
            "Offense": {"average": 50.0, "focus_pct": 50.0},
            "Health": {"average": 500.0, "focus_pct": 25.0},
            "Defense": {"average": 20.0, "focus_pct": 10.0},
        },
    }
    return {
        "name": "Example",
        "source_model": {
            "refreshed_at_utc": timestamp,
            "sources": [source("Top 1000 Kyber GAC"), source("Top 100 Guilds")],
        },
        "set_combinations": {"Speed + Health": 100.0},
        "set_preferences": {"Speed": 1.0, "Health": 1.0},
        "primary_preferences": {"Arrow": {"Speed": 1.0}},
        "secondary_preferences": {"Speed": 1.0},
    }


class ProfileCacheTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "mod_profiles.json"
        self.patcher = patch.object(profiles, "PROFILE_FILE", self.path)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.temp.cleanup()

    def save(self, data):
        self.path.write_text(json.dumps(data), encoding="utf-8")

    def load_text(self):
        return self.path.read_text(encoding="utf-8")

    def test_requested_profile_uses_cache_without_network_or_write(self):
        cached = valid_profile()
        self.save({"profiles": {"UNIT": cached}})
        before = self.load_text()
        with patch("urllib.request.urlopen", side_effect=AssertionError("network access forbidden")):
            result, status = profiles.ensure_profiles({"UNIT"}, {"UNIT": "Example"})
        self.assertEqual(status["UNIT"], "cached")
        self.assertEqual(result["UNIT"], cached)
        self.assertEqual(self.load_text(), before)

    def test_missing_profile_is_reported_unavailable_without_fetch(self):
        self.save({"profiles": {}})
        before = self.load_text()
        with patch("urllib.request.urlopen", side_effect=AssertionError("network access forbidden")):
            result, status = profiles.ensure_profiles({"UNIT"}, {"UNIT": "Example"})
        self.assertEqual(status["UNIT"], "unavailable")
        self.assertNotIn("UNIT", result)
        self.assertEqual(self.load_text(), before)

    def test_only_explicitly_requested_profiles_are_returned(self):
        wanted = valid_profile()
        other = valid_profile()
        self.save({"profiles": {"UNIT": wanted, "OTHER": other}})
        result, status = profiles.ensure_profiles({"UNIT"}, {"UNIT": "Example"})
        self.assertEqual(set(result), {"UNIT"})
        self.assertEqual(status, {"UNIT": "cached"})

    def test_load_fresh_profiles_returns_all_fresh_complete_cached_profiles(self):
        now = datetime(2026, 11, 13, tzinfo=timezone.utc)
        self.save({"profiles": {
            "UNIT": valid_profile("2026-11-10T00:00:00Z"),
            "OTHER": valid_profile("2026-11-12T00:00:00Z"),
        }})
        result = profiles.load_fresh_profiles(now=now)
        self.assertEqual(set(result), {"UNIT", "OTHER"})

    def test_load_fresh_profiles_excludes_stale_and_incomplete_profiles(self):
        now = datetime(2026, 11, 13, tzinfo=timezone.utc)
        incomplete = valid_profile("2026-11-12T00:00:00Z")
        incomplete["source_model"]["sources"].pop()
        self.save({"profiles": {
            "FRESH": valid_profile("2026-11-10T00:00:00Z"),
            "STALE": valid_profile("2026-11-07T00:00:00Z"),
            "INCOMPLETE": incomplete,
        }})
        result = profiles.load_fresh_profiles(now=now)
        self.assertEqual(set(result), {"FRESH"})

    def test_corrupt_cache_fails_closed_without_rewriting_file(self):
        self.path.write_text("{broken", encoding="utf-8")
        before = self.load_text()
        result, status = profiles.ensure_profiles({"UNIT"}, {"UNIT": "Example"})
        self.assertEqual(result, {})
        self.assertEqual(status, {"UNIT": "unavailable"})
        self.assertEqual(self.load_text(), before)


if __name__ == "__main__":
    unittest.main()
