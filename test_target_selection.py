import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from mod_analyzer import load_targets, load_protected_owners, optimize_target_build, unavailable_profile_ids


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

    def test_mandatory_donor_exclusions_are_always_protected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "protected_owners.json"
            path.write_text(
                json.dumps({"protectedOwners": ["CUSTOM_PROTECTED"]}),
                encoding="utf-8",
            )
            with patch("os.path.exists", return_value=True), patch(
                "builtins.open",
                side_effect=lambda name, *args, **kwargs: path.open(*args, **kwargs),
            ):
                protected = load_protected_owners()

        self.assertTrue({
            "JARJARBINKS",
            "GRANDINQUISITOR",
            "SECONDSISTER",
            "THIRDSISTER",
            "FIFTHBROTHER",
            "SEVENTHSISTER",
            "EIGHTHBROTHER",
            "NINTHSISTER",
            "GRANDMOFFTARKIN",
            "HONDO",
            "CUSTOM_PROTECTED",
        }.issubset(protected))

    def test_unavailable_donor_profile_is_classified_for_protection(self):
        status = {
            "GLREY": "unavailable",
            "SCORCH": "cached",
            "50RT": "cached",
        }
        self.assertEqual(unavailable_profile_ids(status), {"GLREY"})

    def test_optimizer_uses_alternative_when_unprofiled_donor_is_protected(self):
        slots = ("Square", "Diamond", "Circle", "Arrow", "Triangle", "Cross")
        rows = []
        for slot in slots:
            rows.append({
                "id": "inventory-" + slot,
                "assignedTo": "",
                "equipped": "False",
                "slot": slot,
                "set": "Offense",
                "primaryStat": "Offense",
                "primaryValue": "8.5",
                "dots": "6",
                "tier": "5",
                "level": "15",
                "secondary1Stat": "Speed",
                "secondary1Value": "12",
                "secondary1Rolls": "4",
                "secondary1RawRolls": "30000|30000|30000|30000",
            })

        rows.append({
            "id": "glrey-arrow",
            "assignedTo": "glrey-instance",
            "equipped": "True",
            "slot": "Arrow",
            "set": "Offense",
            "primaryStat": "Offense",
            "primaryValue": "8.5",
            "dots": "6",
            "tier": "5",
            "level": "15",
            "secondary1Stat": "Speed",
            "secondary1Value": "24",
            "secondary1Rolls": "4",
            "secondary1RawRolls": "60000|60000|60000|60000",
        })
        profile = {
            "primary_preferences": {slot: {"Offense": 1.0} for slot in slots},
            "secondary_preferences": {"Speed": 1.0},
            "set_preferences": {"Offense": 1.0},
        }
        aliases = {"target-instance": "TARGET", "glrey-instance": "GLREY"}
        profiles = {"TARGET": profile}

        unrestricted = optimize_target_build(
            [dict(row) for row in rows], {"TARGET"}, profiles, aliases
        )
        self.assertEqual(
            next(mod for mod in unrestricted["TARGET"]["mods"] if mod["slot"] == "Arrow")["id"],
            "glrey-arrow",
        )

        protected = optimize_target_build(
            [dict(row) for row in rows], {"TARGET"}, profiles, aliases,
            protected_owners={"GLREY"},
        )
        self.assertEqual(
            next(mod for mod in protected["TARGET"]["mods"] if mod["slot"] == "Arrow")["id"],
            "inventory-Arrow",
        )


if __name__ == "__main__":
    unittest.main()
