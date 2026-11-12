import unittest

from mod_analyzer import (
    optimize_target_build,
    profile_mod_score_components,
    profiled_build_score,
    compare_profiled_builds,
    score_profile,
)


def make_mod(mod_id, slot, primary="Health", primary_value=16, mod_set="Health",
             secondary_stat="Speed", secondary_value=6, rolls_count=1):
    row = {
        "id": mod_id, "slot": slot, "set": mod_set,
        "primaryStat": primary, "primaryValue": str(primary_value),
        "dots": "6", "tier": "5", "level": "15",
        "equipped": "False", "assignedTo": "",
    }
    if secondary_stat:
        row.update({
            "secondary1Stat": secondary_stat,
            "secondary1Value": str(secondary_value),
            "secondary1Rolls": str(rolls_count),
            "secondary1RawRolls": str(int(float(secondary_value) * 10000)),
        })
    return row


PROFILE = {
    "primary_preferences": {
        "Square": {"Offense": 1.0},
        "Diamond": {"Defense": 1.0},
        "Circle": {"Health": 1.0},
        "Arrow": {"Speed": 1.0},
        "Triangle": {"Offense": 1.0},
        "Cross": {"Potency": 1.0},
    },
    "secondary_preferences": {"Speed": 1.0, "Offense %": 0.5},
    "set_preferences": {"Speed": 1.0, "Health": 0.5},
}


class UnifiedScoringTests(unittest.TestCase):
    def test_score_profile_uses_optimizer_40_60_model(self):
        mod = make_mod("one", "Arrow", primary="Speed", primary_value=32,
                       secondary_stat="Speed", secondary_value=30, rolls_count=5)
        components = profile_mod_score_components(mod, PROFILE)
        result = score_profile(mod, PROFILE)
        self.assertAlmostEqual(result["fitScore"], components["fitScore"], places=2)
        self.assertAlmostEqual(
            result["fitScore"],
            result["primaryPoints"] + result["secondaryPoints"],
            places=2,
        )
        self.assertAlmostEqual(result["primaryPoints"], 40.0 / 6.0, places=2)
        self.assertAlmostEqual(result["secondaryPoints"], 60.0 * 5.0 / 24.0, places=2)

    def test_optimizer_and_single_mod_fit_share_exact_score(self):
        rows = [
            make_mod("square", "Square", "Offense", 8.5, "Offense", "Speed", 18, 3),
            make_mod("diamond", "Diamond", "Defense", 20, "Health", "Speed", 12, 2),
            make_mod("circle", "Circle", "Health", 16, "Health", "Speed", 15, 3),
            make_mod("arrow", "Arrow", "Speed", 32, "Speed", "Speed", 30, 5),
            make_mod("triangle", "Triangle", "Offense", 8.5, "Offense", "Speed", 18, 3),
            make_mod("cross", "Cross", "Potency", 30, "Potency", "Speed", 12, 2),
        ]
        result = optimize_target_build(rows, {"TARGET"}, {"TARGET": PROFILE})
        self.assertIn("TARGET", result)
        for mod in result["TARGET"]["mods"]:
            self.assertAlmostEqual(
                score_profile(mod, PROFILE)["fitScore"],
                mod["optimizerScore"],
                places=2,
            )

    def test_dominant_profile_set_combo_outranks_higher_scoring_unobserved_mix(self):
        slots = ("Square", "Diamond", "Circle", "Arrow", "Triangle", "Cross")
        primary = {
            "Square": ("Offense", 8.5), "Diamond": ("Defense", 20),
            "Circle": ("Health", 16), "Arrow": ("Speed", 30),
            "Triangle": ("Critical Damage", 42), "Cross": ("Potency", 30),
        }
        rows = []
        for slot in slots:
            pstat, pvalue = primary[slot]
            # Strong individual mods from an unobserved set mix.
            rows.append(make_mod(
                "health-" + slot, slot, pstat, pvalue, "Health", "Speed", 30, 5
            ))
            # Weaker individual mods, but the complete 4+2 set combination
            # is the dominant combination in the target's profile.
            preferred_set = "Critical Damage" if slot in slots[:4] else "Critical Chance"
            rows.append(make_mod(
                "profile-" + slot, slot, pstat, pvalue,
                preferred_set, "Speed", 6, 1
            ))

        profile = {
            "primary_preferences": {
                slot: {primary[slot][0]: 1.0} for slot in slots
            },
            "secondary_preferences": {"Speed": 1.0},
            "set_preferences": {"Health": 1.0},
            "set_combinations": {
                "Crit Damage + Crit Chance": 30.0,
                "Health + Offense": 8.0,
            },
        }
        result = optimize_target_build(rows, {"TARGET"}, {"TARGET": profile})
        chosen = result["TARGET"]["mods"]
        counts = {}
        for mod in chosen:
            counts[mod["set"]] = counts.get(mod["set"], 0) + 1
        self.assertEqual(counts.get("Critical Damage"), 4)
        self.assertEqual(counts.get("Critical Chance"), 2)
        self.assertEqual(result["TARGET"]["setComboMode"], "profile_priority")

    def test_donor_build_comparison_reports_full_profile_score_delta(self):
        before = [
            make_mod("a", "Arrow", "Speed", 32, "Speed", "Speed", 24, 4),
            make_mod("b", "Square", "Offense", 8.5, "Speed", "Speed", 18, 3),
            make_mod("c", "Diamond", "Defense", 20, "Speed", "Speed", 18, 3),
            make_mod("d", "Circle", "Health", 16, "Speed", "Speed", 18, 3),
            make_mod("e", "Triangle", "Offense", 8.5, "Health", "Speed", 12, 2),
            make_mod("f", "Cross", "Potency", 30, "Health", "Speed", 12, 2),
        ]
        after = list(before)
        after[0] = make_mod("replacement", "Arrow", "Speed", 24, "Health", "Offense %", 1.5, 1)
        result = compare_profiled_builds(before, after, PROFILE)
        self.assertIsNotNone(result)
        self.assertAlmostEqual(result["before"], profiled_build_score(before, PROFILE), places=2)
        self.assertAlmostEqual(result["after"], profiled_build_score(after, PROFILE), places=2)
        self.assertAlmostEqual(result["delta"], result["after"] - result["before"], places=2)
        self.assertLess(result["delta"], 0)

    def test_donor_build_comparison_uses_no_profile_fallback_when_missing(self):
        self.assertIsNone(compare_profiled_builds([], [], {}))
        self.assertIsNone(compare_profiled_builds([], [], None))

    def test_profiled_donor_build_score_includes_all_equipped_mods(self):
        before = [
            make_mod("a", "Arrow", "Speed", 32, "Speed", "Speed", 24, 4),
            make_mod("b", "Square", "Offense", 8.5, "Speed", "Speed", 18, 3),
            make_mod("c", "Diamond", "Defense", 20, "Speed", "Speed", 18, 3),
            make_mod("d", "Circle", "Health", 16, "Speed", "Speed", 18, 3),
            make_mod("e", "Triangle", "Offense", 8.5, "Health", "Speed", 12, 2),
            make_mod("f", "Cross", "Potency", 30, "Health", "Speed", 12, 2),
        ]
        after = list(before)
        after[0] = make_mod("replacement", "Arrow", "Speed", 24, "Health", "Offense %", 1.5, 1)
        before_score = profiled_build_score(before, PROFILE)
        after_score = profiled_build_score(after, PROFILE)
        self.assertNotEqual(before_score, after_score)
        self.assertLess(after_score, before_score)


if __name__ == "__main__":
    unittest.main()
