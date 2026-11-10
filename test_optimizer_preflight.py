import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from optimizer_preflight import inspect_profiles, profile_is_complete


def make_profile(timestamp):
    source = {
        "set_combinations_pct": {"Speed + Health": 70},
        "primary_pct": {
            "Arrow": {"Speed": 90}, "Triangle": {"Health": 80},
            "Circle": {"Health": 70}, "Cross": {"Potency": 60},
        },
        "secondary_focus": {
            "Speed": {"average": 20, "focus_pct": 20},
            "Health": {"average": 800, "focus_pct": 8},
            "Protection": {"average": 1400, "focus_pct": 7},
            "Offense": {"average": 80, "focus_pct": 6},
        },
    }
    return {
        "name": "Example",
        "source_model": {"refreshed_at_utc": timestamp, "sources": [source, source]},
        "set_preferences": {"Speed": 1.0},
        "primary_preferences": {"Arrow": {"Speed": 1.0}},
        "secondary_preferences": {"Speed": 1.0},
    }


class OptimizerPreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "profiles.json"
        self.now = datetime(2026, 11, 10, 18, tzinfo=timezone.utc)

    def tearDown(self):
        self.temp.cleanup()

    def save(self, profile, status=None):
        self.path.write_text(json.dumps({
            "profiles": {"EXAMPLE": profile},
            "profile_status": {"EXAMPLE": status or {}},
        }), encoding="utf-8")

    def test_fresh_complete_profile_passes(self):
        self.save(make_profile(self.now.isoformat()))
        self.assertTrue(inspect_profiles(["Example"], self.path, self.now)[0].startswith("PASS:"))

    def test_checked_timestamp_does_not_refresh_stale_profile(self):
        old = make_profile((self.now - timedelta(days=6)).isoformat())
        self.save(old, {"checked_at_utc": self.now.isoformat()})
        result = inspect_profiles(["Example"], self.path, self.now)
        self.assertIn("starszy niż 5 dni", result[0])

    def test_profile_missing_fails_only_for_requested_character(self):
        self.save(make_profile(self.now.isoformat()))
        result = inspect_profiles(["Not Requested"], self.path, self.now)
        self.assertIn("brak profilu", result[0])

    def test_missing_second_source_fails(self):
        profile = make_profile(self.now.isoformat())
        profile["source_model"]["sources"] = profile["source_model"]["sources"][:1]
        complete, reason = profile_is_complete(profile)
        self.assertFalse(complete)
        self.assertIn("dwóch", reason)

    def test_missing_top_four_fails(self):
        profile = make_profile(self.now.isoformat())
        profile["source_model"]["sources"][1]["secondary_focus"] = {"Speed": {"focus_pct": 20}}
        complete, reason = profile_is_complete(profile)
        self.assertFalse(complete)
        self.assertIn("TOP 4", reason)


if __name__ == "__main__":
    unittest.main()
