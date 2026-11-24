import unittest

from mod_analyzer import optimize_target_build


SLOTS = {
    "Square": ("Offense", "8.5"),
    "Diamond": ("Defense", "20"),
    "Circle": ("Health", "16"),
    "Arrow": ("Speed", "32"),
    "Triangle": ("Offense", "8.5"),
    "Cross": ("Potency", "30"),
}


def make_mod(slot, mod_id, speed_roll, equipped, owner=""):
    return {
        "id": mod_id,
        "slot": slot,
        "set": "Health",
        "dots": "6",
        "tier": "5",
        "tierName": "A",
        "level": "15",
        "primaryStat": SLOTS[slot][0],
        "primaryValue": SLOTS[slot][1],
        "secondary1Stat": "Speed",
        "secondary1Value": str(speed_roll * 4),
        "secondary1Rolls": "4",
        "secondary1RawRolls": "|".join([str(speed_roll * 10000)] * 4),
        "equipped": "true" if equipped else "false",
        "assignedTo": owner,
        "modValue": 50 if speed_roll >= 6 else 10,
    }


def make_profile():
    return {
        "primary_preferences": {
            slot: {primary: 1.0} for slot, (primary, _value) in SLOTS.items()
        },
        "secondary_preferences": {"Speed": 1.0},
        "set_preferences": {"Health": 1.0},
        "set_combinations": {"Triple Health": 100.0},
    }


class ActualModScoringTests(unittest.TestCase):
    def optimize(self, rows):
        return optimize_target_build(
            rows,
            {"TARGET"},
            profiles={"TARGET": make_profile()},
            aliases={},
            names={"TARGET": "Target"},
            protected_owners=set(),
            ranking=[],
        )

    def test_weaker_inventory_mods_never_replace_better_equipped_mods(self):
        rows = []
        for slot in SLOTS:
            rows.append(make_mod(slot, "current-" + slot, 6, True, "TARGET"))
            rows.append(make_mod(slot, "weaker-" + slot, 3, False))
        result = self.optimize(rows)
        self.assertNotIn("TARGET", result)

    def test_real_upgrade_is_selected_and_gain_is_actual(self):
        rows = []
        for slot in SLOTS:
            rows.append(make_mod(slot, "current-" + slot, 3, True, "TARGET"))
            rows.append(make_mod(slot, "upgrade-" + slot, 6, False))
        result = self.optimize(rows)
        self.assertIn("TARGET", result)
        self.assertGreater(result["TARGET"]["gain"], 0)
        self.assertNotIn("currentProjectedScore", result["TARGET"])
        self.assertNotIn("optimizerProjectedScore", result["TARGET"]["mods"][0])


if __name__ == "__main__":
    unittest.main()
