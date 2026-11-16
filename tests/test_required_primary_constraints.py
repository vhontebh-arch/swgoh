import unittest

from mod_analyzer import optimize_target_build


def mod(mod_id, slot, set_name, primary, secondary_speed=0, dots=5):
    row = {
        "id": mod_id, "slot": slot, "set": set_name, "dots": str(dots),
        "tier": "5", "level": "15", "equipped": "False", "assignedTo": "",
        "primaryStat": primary,
        "primaryValue": {
            "Speed": "30", "Offense %": "5.88%", "Defense %": "11.75%",
            "Health %": "5.88%",
        }.get(primary, "5.88%"),
        "modValue": "50", "potentialCeiling": "60",
    }
    if secondary_speed:
        row.update({
            "secondary1Stat": "Speed",
            "secondary1Value": str(secondary_speed),
            "secondary1Rolls": "4",
            "secondary1RawRolls": "|".join(["60000"] * 4),
        })
    return row


class RequiredPrimaryTests(unittest.TestCase):
    def test_triangle_must_be_health_primary_and_not_speed_set(self):
        profile = {
            "set_combinations": {"Speed + Health": 100.0},
            "set_preferences": {"Speed": 1.0, "Health": 1.0},
            "primary_preferences": {
                "Arrow": {"Speed": 1.0},
                "Square": {"Offense %": 1.0},
                "Diamond": {"Defense %": 1.0},
                "Circle": {"Health %": 1.0},
                "Triangle": {"Health %": 1.0, "Offense %": 0.2},
                "Cross": {"Health %": 1.0},
            },
            "secondary_preferences": {"Speed": 1.0, "Health": 0.5},
        }
        rows = [
            mod("arrow-health", "Arrow", "Health", "Speed"),
            mod("square-speed", "Square", "Speed", "Offense %"),
            mod("diamond-speed", "Diamond", "Speed", "Defense %"),
            mod("circle-speed", "Circle", "Speed", "Health %"),
            mod("cross-speed", "Cross", "Speed", "Health %"),
            mod("cross-health", "Cross", "Health", "Health %"),
            mod("triangle-health-primary", "Triangle", "Health", "Health %"),
            mod("triangle-offense-primary", "Triangle", "Health", "Offense %", 24),
            mod("triangle-speed-set", "Triangle", "Speed", "Health %", 24),
        ]
        result = optimize_target_build(
            rows, {"TEST"}, {"TEST": profile}, {}, {}, set(),
            required_set_combo="Speed + Health",
            projected=False,
            required_primaries={"Triangle": {"Health %"}},
            forbidden_sets={"Triangle": {"Speed"}},
        )
        chosen = next(m for m in result["TEST"]["mods"] if m["slot"] == "Triangle")
        self.assertEqual(chosen["id"], "triangle-health-primary")
        self.assertEqual(chosen["primaryStat"], "Health %")
        self.assertEqual(chosen["set"], "Health")

    def test_six_dot_mod_is_excluded_for_below_g12_target(self):
        profile = {
            "set_combinations": {"Speed + Health": 100.0},
            "set_preferences": {"Speed": 1.0, "Health": 1.0},
            "primary_preferences": {
                "Arrow": {"Speed": 1.0},
                "Square": {"Offense %": 1.0},
                "Diamond": {"Defense %": 1.0},
                "Circle": {"Health %": 1.0},
                "Triangle": {"Health %": 1.0},
                "Cross": {"Health %": 1.0},
            },
            "secondary_preferences": {"Speed": 1.0, "Health": 0.5},
        }
        rows = [
            mod("arrow-health-5", "Arrow", "Health", "Speed", dots=5),
            mod("arrow-health-6", "Arrow", "Health", "Speed", 24, dots=6),
            mod("square-speed", "Square", "Speed", "Offense %"),
            mod("diamond-speed", "Diamond", "Speed", "Defense %"),
            mod("circle-speed", "Circle", "Speed", "Health %"),
            mod("cross-speed", "Cross", "Speed", "Health %"),
            mod("triangle-health", "Triangle", "Health", "Health %"),
        ]
        result = optimize_target_build(
            rows, {"TEST"}, {"TEST": profile}, {}, {}, set(),
            required_set_combo="Speed + Health",
            projected=False,
            gear_tiers={"TEST": 9},
        )
        arrow = next(m for m in result["TEST"]["mods"] if m["slot"] == "Arrow")
        self.assertEqual(arrow["id"], "arrow-health-5")
        self.assertEqual(int(arrow["dots"]), 5)


if __name__ == "__main__":
    unittest.main()
