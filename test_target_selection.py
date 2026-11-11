import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from mod_analyzer import load_targets


class TargetSelectionTests(unittest.TestCase):
    def test_explicit_target_overrides_farming_targets(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "targets.json"
            original = {
                "targets": [
                    {"baseId": "JARJARBINKS", "targetGearTier": 13, "targetRelicTier": 5}
                ]
            }
            path.write_text(json.dumps(original), encoding="utf-8")

            with patch("os.getcwd", return_value=directory), patch("os.path.exists", side_effect=lambda p: p != "targets.json"):
                selected = load_targets(["50RT"])

            self.assertEqual(selected, [{"baseId": "50RT"}])
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), original)

    def test_multiple_comma_separated_targets_are_normalized_and_deduplicated(self):
        self.assertEqual(
            load_targets([" 50rt, JARJARBINKS ", "50RT"]),
            [{"baseId": "50RT"}, {"baseId": "JARJARBINKS"}],
        )

    def test_no_override_preserves_targets_json_behavior(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "targets.json"
            expected = [{"baseId": "JARJARBINKS", "targetGearTier": 13, "targetRelicTier": 5}]
            path.write_text(json.dumps({"targets": expected}), encoding="utf-8")
            with patch("os.path.exists", side_effect=lambda p: p == "targets.json"), patch(
                "builtins.open", side_effect=lambda name, *args, **kwargs: path.open(*args, **kwargs)
            ):
                self.assertEqual(load_targets(), expected)


if __name__ == "__main__":
    unittest.main()
