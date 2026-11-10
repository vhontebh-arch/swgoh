import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import update_mod_profiles as profiles


def valid_profile():
    return {
        "name": "Example",
        "source_model": {"refreshed_at_utc": datetime.now(timezone.utc).isoformat()},
        "set_preferences": {"Speed": 1.0},
        "primary_preferences": {
            "Arrow": {"Speed": 1.0},
            "Triangle": {"Protection": 1.0},
            "Circle": {"Protection": 1.0},
            "Cross": {"Potency": 1.0},
        },
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

    def load(self):
        return json.loads(self.path.read_text(encoding="utf-8"))

    def test_fresh_profile_uses_cache_without_fetch(self):
        cached = valid_profile()
        self.save({"profiles": {"UNIT": cached}})
        with patch.object(profiles, "refresh_one", side_effect=AssertionError("unexpected fetch")):
            result, status = profiles.ensure_profiles({"UNIT"}, {"UNIT": "Example"})
        self.assertEqual(status["UNIT"], "cached")
        self.assertEqual(result["UNIT"], cached)

    def test_missing_profile_is_fetched_and_persisted(self):
        fetched = valid_profile()
        self.save({"profiles": {}})
        with patch.object(profiles, "refresh_one", return_value=fetched) as fetch:
            result, status = profiles.ensure_profiles({"UNIT"}, {"UNIT": "Example"})
        fetch.assert_called_once()
        self.assertEqual(status["UNIT"], "refreshed")
        self.assertEqual(self.load()["profiles"]["UNIT"], fetched)
        self.assertIn("profile_status", self.load())

    def test_failed_refresh_keeps_previous_profile_unchanged(self):
        cached = valid_profile()
        cached["source_model"]["refreshed_at_utc"] = "2020-01-01T00:00:00+00:00"
        self.save({"profiles": {"UNIT": cached}})
        with patch.object(profiles, "refresh_one", side_effect=RuntimeError("short response")):
            result, status = profiles.ensure_profiles({"UNIT"}, {"UNIT": "Example"})
        self.assertEqual(status["UNIT"], "stale_fallback")
        self.assertEqual(result["UNIT"], cached)
        self.assertEqual(self.load()["profiles"]["UNIT"], cached)
        self.assertEqual(self.load()["profile_status"]["UNIT"]["status"], "stale_fallback")

    def test_one_failed_unit_does_not_block_other_profiles(self):
        good = valid_profile()
        self.save({"profiles": {}})
        def refresh(base_id, name, existing):
            if base_id == "BAD":
                raise RuntimeError("unavailable")
            return good
        with patch.object(profiles, "refresh_one", side_effect=refresh):
            result, status = profiles.ensure_profiles({"BAD", "GOOD"}, {"BAD": "Bad", "GOOD": "Good"})
        self.assertEqual(status["BAD"], "unavailable")
        self.assertEqual(status["GOOD"], "refreshed")
        self.assertIn("GOOD", result)
        self.assertNotIn("BAD", result)


if __name__ == "__main__":
    unittest.main()
