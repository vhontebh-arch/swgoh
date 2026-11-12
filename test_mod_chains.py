import unittest

from mod_analyzer import apply_optimizer_replacements


TARGET = "target-instance"
DONOR = "donor-instance"
DONOR_B = "donor-b-instance"


def make_mod(mod_id, owner="", equipped=False, slot="Arrow", value=10, mod_set="Speed", speed_roll=None):
    row = {
        "id": mod_id, "assignedTo": owner,
        "equipped": "True" if equipped else "False",
        "slot": slot, "set": mod_set, "modValue": str(value),
        "dots": "5", "tier": "5", "level": "15",
    }
    if speed_roll is not None:
        row.update({"secondary1Stat": "Speed", "secondary1Value": str(speed_roll),
                    "secondary1Rolls": "1",
                    "secondary1RawRolls": str(int(float(speed_roll) * 10000))})
    return row


def run_plan(rows, selected, aliases=None, profiles=None):
    aliases = aliases or {TARGET: "TARGET"}
    return apply_optimizer_replacements(
        rows, {"TARGET": {"mods": [selected]}}, {"TARGET"},
        aliases=aliases, profiles=profiles,
    )


class TransferChainTests(unittest.TestCase):
    def test_donor_combo_changes_patch_choice_and_is_rendered_in_report(self):
        from mod_analyzer import append_donor_combo_report

        # The donor starts with the common 4 Health + 2 Defense combination.
        # The higher-fit Health patch breaks it; the lower-fit Defense patch preserves it.
        selected = make_mod("selected-defense-arrow", DONOR, True, "Arrow", 10, "Defense", 3)
        donor_mods = [
            make_mod("donor-square", DONOR, True, "Square", 10, "Health"),
            make_mod("donor-diamond", DONOR, True, "Diamond", 10, "Health"),
            make_mod("donor-triangle", DONOR, True, "Triangle", 10, "Health"),
            make_mod("donor-circle", DONOR, True, "Circle", 10, "Health"),
            make_mod("donor-cross", DONOR, True, "Cross", 10, "Defense"),
        ]
        high_fit_breaking_patch = make_mod("health-patch-high-fit", value=30, mod_set="Health", speed_roll=6)
        preserving_patch = make_mod("defense-patch-lower-fit", value=10, mod_set="Defense", speed_roll=3)
        profile = {
            "set_combinations": {"Double Health + Defense": 48.9, "Double Defense + Health": 20.0},
            "secondary_preferences": {"Speed": 1.0},
        }
        result = run_plan(
            [selected, *donor_mods, high_fit_breaking_patch, preserving_patch],
            selected, {TARGET: "TARGET", DONOR: "DONOR"}, {"DONOR": profile},
        )
        self.assertTrue(result["safe"], result["failed"])
        move = result["plans"][0]["moves"][0]
        self.assertEqual(move["replacement"]["id"], "defense-patch-lower-fit")
        from mod_analyzer import score_profile
        self.assertGreater(
            score_profile(high_fit_breaking_patch, profile)["fitScore"],
            score_profile(preserving_patch, profile)["fitScore"],
        )
        donor = next(item for item in result["validation"] if item["owner"] == DONOR)
        self.assertEqual(donor["beforeComboKey"], "Double Health + Defense")
        self.assertEqual(donor["afterComboKey"], "Double Health + Defense")
        self.assertEqual(donor["beforeComboFrequency"], 48.9)
        self.assertEqual(donor["afterComboFrequency"], 48.9)

        lines = []
        append_donor_combo_report(lines, result["validation"], {DONOR})
        report = "\n".join(lines)
        self.assertIn("Dokładna kombinacja setów dawców", report)
        self.assertIn("Double Health + Defense", report)
        self.assertIn("48.9%", report)

    def test_inventory_to_empty_target(self):
        selected = make_mod("inventory-mod")
        result = run_plan([selected], selected)
        self.assertTrue(result["safe"], result["failed"])
        self.assertEqual(len(result["plans"]), 1)
        self.assertEqual(result["plans"][0]["moves"], [])

    def test_inventory_to_occupied_target_returns_displaced_mod(self):
        selected = make_mod("inventory-mod")
        current = make_mod("target-current", TARGET, True, value=5)
        result = run_plan([selected, current], selected)
        self.assertTrue(result["safe"], result["failed"])
        self.assertEqual(result["plans"][0]["target_current"]["id"], "target-current")

    def test_equipped_source_is_repaired_into_the_new_hole(self):
        selected = make_mod("selected-mod", DONOR, True, value=20)
        patch = make_mod("inventory-patch", value=15)
        result = run_plan(
            [selected, patch],
            selected,
            {TARGET: "TARGET", DONOR: "DONOR"},
        )
        self.assertTrue(result["safe"], result["failed"])
        moves = result["plans"][0]["moves"]
        self.assertEqual(len(moves), 1)
        self.assertIsNone(moves[0]["removed"])
        self.assertEqual(moves[0]["replacement"]["id"], "inventory-patch")

    def test_target_current_can_be_recycled_to_repair_source(self):
        selected = make_mod("selected-mod", DONOR, True, value=20)
        target_current = make_mod("target-current", TARGET, True, value=5)
        result = run_plan(
            [selected, target_current],
            selected,
            {TARGET: "TARGET", DONOR: "DONOR"},
        )
        self.assertTrue(result["safe"], result["failed"])
        moves = result["plans"][0]["moves"]
        self.assertEqual(len(moves), 1)
        self.assertEqual(moves[0]["replacement"]["id"], "target-current")
        self.assertIsNone(moves[0]["removed"])

    def test_selected_mod_must_be_in_its_declared_source_slot(self):
        source_row = make_mod("selected-mod", DONOR, True, slot="Triangle", value=20)
        selected_copy = dict(source_row, slot="Arrow")
        patch = make_mod("inventory-patch", slot="Arrow", value=15)
        result = run_plan(
            [source_row, patch],
            selected_copy,
            {TARGET: "TARGET", DONOR: "DONOR"},
        )
        self.assertFalse(result["safe"])
        self.assertTrue(any("nie znajduje się w slocie Arrow" in reason for _, reason in result["failed"]))

    def test_best_patch_is_selected_from_all_inventory_candidates(self):
        selected = make_mod("selected-mod", DONOR, True, value=10)
        weaker = make_mod("weaker-patch", value=12)
        stronger = make_mod("stronger-patch", value=30)
        result = run_plan(
            [selected, weaker, stronger],
            selected,
            {TARGET: "TARGET", DONOR: "DONOR"},
        )
        self.assertTrue(result["safe"], result["failed"])
        moves = result["plans"][0]["moves"]
        self.assertEqual(len(moves), 1)
        self.assertEqual(moves[0]["replacement"]["id"], "stronger-patch")

    def test_profile_first_fallback_prefers_higher_fit_before_set_preservation(self):
        selected = make_mod("selected-mod", DONOR, True, value=10, mod_set="Speed")
        other_set_pieces = [
            make_mod("donor-circle", DONOR, True, slot="Circle", value=10, mod_set="Speed"),
            make_mod("donor-cross", DONOR, True, slot="Cross", value=10, mod_set="Speed"),
            make_mod("donor-triangle", DONOR, True, slot="Triangle", value=10, mod_set="Speed"),
        ]
        higher_value = make_mod("higher-value-patch", value=30, mod_set="Critical Chance")
        set_preserving = make_mod("set-preserving-patch", value=12, mod_set="Speed")
        result = run_plan(
            [selected, *other_set_pieces, higher_value, set_preserving],
            selected,
            {TARGET: "TARGET", DONOR: "DONOR"},
        )
        self.assertTrue(result["safe"], result["failed"])
        move = result["plans"][0]["moves"][0]
        # With no donor profiles available, the documented fallback is modValue.
        # In v8 donor fit/value ranks ahead of set preservation, so the larger
        # fallback gain wins and the set loss must remain visible in the audit.
        self.assertEqual(
            move["replacement"]["id"], "higher-value-patch",
            "chosen move={!r}".format(move),
        )
        self.assertEqual(move["set_delta"], -1)

    def test_inventory_patch_is_currently_preferred_to_another_donor(self):
        selected = make_mod("selected-mod", DONOR, True, value=20)
        other_donor = make_mod("other-donor-mod", DONOR_B, True, value=12)
        inventory_patch = make_mod("inventory-patch", value=15)
        result = run_plan(
            [selected, other_donor, inventory_patch],
            selected,
            {TARGET: "TARGET", DONOR: "DONOR", DONOR_B: "DONOR_B"},
        )
        self.assertTrue(result["safe"], result["failed"])
        moves = result["plans"][0]["moves"]
        self.assertEqual(len(moves), 1)
        self.assertEqual(moves[0]["replacement"]["id"], "inventory-patch")

    def test_unrepairable_source_is_rejected(self):
        selected = make_mod("selected-mod", DONOR, True, value=20)
        result = run_plan(
            [selected],
            selected,
            {TARGET: "TARGET", DONOR: "DONOR"},
        )
        self.assertFalse(result["safe"])
        self.assertTrue(any("brak wykonalnego łańcucha" in reason for _, reason in result["failed"]))

    def test_independent_donor_chains_do_not_conflict_on_empty_removed_marker(self):
        donor_a = "donor-a-instance"
        donor_b = "donor-b-instance"
        selected_a = make_mod("selected-a", donor_a, True, slot="Arrow", value=20)
        selected_b = make_mod("selected-b", donor_b, True, slot="Circle", value=20)
        patch_a = make_mod("patch-a", slot="Arrow", value=15)
        patch_b = make_mod("patch-b", slot="Circle", value=15)

        result = apply_optimizer_replacements(
            [selected_a, selected_b, patch_a, patch_b],
            {"TARGET": {"mods": [selected_a, selected_b]}},
            {"TARGET"},
            aliases={
                TARGET: "TARGET",
                donor_a: "DONOR_A",
                donor_b: "DONOR_B",
            },
        )

        self.assertTrue(result["safe"], result["failed"])
        self.assertEqual(len(result["plans"]), 2)
        self.assertEqual(
            {plan["mod"]["id"] for plan in result["plans"]},
            {"selected-a", "selected-b"},
        )

    def test_same_inventory_mod_cannot_be_assigned_to_two_targets(self):
        target_b = "target-b-instance"
        shared = make_mod("shared-mod")
        result = apply_optimizer_replacements(
            [shared],
            {
                "TARGET": {"mods": [shared]},
                "TARGET_B": {"mods": [shared]},
            },
            {"TARGET", "TARGET_B"},
            aliases={TARGET: "TARGET", target_b: "TARGET_B"},
        )
        self.assertFalse(result["safe"])
        self.assertTrue(any("konflikt modów" in reason for _, reason in result["failed"]))


class ProfileSetAliasTests(unittest.TestCase):
    def test_swgoh_gg_set_aliases_match_internal_game_names(self):
        from mod_analyzer import profile_set_preference, score_profile

        profile = {"set_preferences": {"Crit Damage": 1.0, "Crit Chance": 0.8}}
        self.assertEqual(profile_set_preference(profile, "Critical Damage"), 1.0)
        self.assertEqual(profile_set_preference(profile, "Critical Chance"), 0.8)
        self.assertEqual(score_profile(make_mod("cd", mod_set="Critical Damage"), profile)["setFit"], 100.0)
        self.assertEqual(score_profile(make_mod("cc", mod_set="Critical Chance"), profile)["setFit"], 80.0)

    def test_alias_preferences_contribute_to_full_build_set_score(self):
        from mod_analyzer import profiled_build_score

        mods = [
            make_mod("cd-1", slot="Arrow", mod_set="Critical Damage"),
            make_mod("cd-2", slot="Square", mod_set="Critical Damage"),
            make_mod("cd-3", slot="Diamond", mod_set="Critical Damage"),
            make_mod("cd-4", slot="Triangle", mod_set="Critical Damage"),
            make_mod("cc-1", slot="Circle", mod_set="Critical Chance"),
            make_mod("cc-2", slot="Cross", mod_set="Critical Chance"),
        ]
        profile = {
            "set_preferences": {"Crit Damage": 1.0, "Crit Chance": 0.8},
            "secondary_preferences": {"Critical Damage %": 1.0, "Critical Chance %": 1.0},
        }
        without_preferences = {
            "set_preferences": {},
            "secondary_preferences": {"Critical Damage %": 1.0, "Critical Chance %": 1.0},
        }
        self.assertGreater(
            profiled_build_score(mods, profile),
            profiled_build_score(mods, without_preferences),
        )

    def test_preferred_set_bonus_is_not_zero_when_bonus_stat_is_not_top_secondary(self):
        from mod_analyzer import profiled_build_score

        mods = [
            make_mod("cd-1", slot="Arrow", mod_set="Critical Damage"),
            make_mod("cd-2", slot="Square", mod_set="Critical Damage"),
            make_mod("cd-3", slot="Diamond", mod_set="Critical Damage"),
            make_mod("cd-4", slot="Triangle", mod_set="Critical Damage"),
        ]
        profile = {
            "set_preferences": {"Crit Damage": 1.0},
            "secondary_preferences": {"Speed": 1.0, "Offense": 0.8},
        }
        self.assertGreater(profiled_build_score(mods, profile), 0.0)

    def test_exact_combo_match_normalizes_swgoh_gg_aliases(self):
        from mod_analyzer import profile_set_combo_match

        mods = [
            make_mod("cd-1", slot="Arrow", mod_set="Critical Damage"),
            make_mod("cd-2", slot="Square", mod_set="Critical Damage"),
            make_mod("cd-3", slot="Diamond", mod_set="Critical Damage"),
            make_mod("cd-4", slot="Triangle", mod_set="Critical Damage"),
            make_mod("cc-1", slot="Circle", mod_set="Critical Chance"),
            make_mod("cc-2", slot="Cross", mod_set="Critical Chance"),
        ]
        profile = {
            "set_combinations": {"Crit Damage + Crit Chance": 30.45, "Crit Damage + Health": 6.2}
        }
        match = profile_set_combo_match(profile, mods)
        self.assertEqual(match["key"], "Critical Damage + Critical Chance")
        self.assertEqual(match["frequency"], 30.45)
        self.assertEqual(match["preference"], 1.0)


if __name__ == "__main__":
    unittest.main()
