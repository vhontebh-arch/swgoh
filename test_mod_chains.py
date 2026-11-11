# Regression coverage for expected level-15 scoring and executable transfer order.
import unittest

from mod_analyzer import (apply_optimizer_replacements, rolls, quality,
                          profile_primary_preference, profile_secondary_preference,
                          profile_set_preferences, profile_set_combo_support, render_user_report,
                          project_mod_for_build, optimize_target_build)


TARGET = "target-instance"
DONOR = "donor-instance"
DONOR_B = "donor-b-instance"


def make_mod(mod_id, owner="", equipped=False, slot="Arrow", value=10, mod_set="Speed"):
    return {
        "id": mod_id,
        "assignedTo": owner,
        "equipped": "True" if equipped else "False",
        "slot": slot,
        "set": mod_set,
        "modValue": str(value),
    }


def run_plan(rows, selected, aliases=None):
    aliases = aliases or {TARGET: "TARGET"}
    return apply_optimizer_replacements(
        rows,
        {"TARGET": {"mods": [selected]}},
        {"TARGET"},
        aliases=aliases,
    )





class ExpectedLevel15ProjectionTests(unittest.TestCase):
    def test_missing_rolls_use_average_expected_profile_fit_not_best_stat(self):
        row = {
            "id": "unfinished", "dots": "5", "tier": "2", "level": "6",
            "secondary1Stat": "Speed", "secondary1Value": "6",
            "secondary1Rolls": "1", "secondary1RawRolls": "600000",
        }
        profile = {"secondary_preferences": {"Speed": 1.0, "Offense %": 0.5}}
        projected = project_mod_for_build(row, profile)
        mean_new_preference = 0.5 / 11.0
        expected_added_preference = 3 * mean_new_preference
        expected_final_four_mean = (1.0 + expected_added_preference) / 4.0
        expected_fit = 0.5 * (expected_added_preference + expected_final_four_mean)
        self.assertEqual(projected["level"], "15")
        self.assertEqual(projected["dots"], "5")
        self.assertEqual(projected["projectionExpectedRolls"], 4)
        self.assertAlmostEqual(
            projected["projectionExpectedSecondaryFit"],
            expected_fit,
        )
        self.assertEqual(projected["secondary1Rolls"], "1")
        self.assertEqual(projected.get("secondary2Stat", ""), row.get("secondary2Stat", ""))

    def test_primary_is_preserved_from_export_and_depends_on_current_dot_tier(self):
        five_dot = {
            "dots": "5", "tier": "5", "level": "3",
            "primaryStat": "Offense %", "primaryValue": "2.8%",
        }
        six_dot = {
            "dots": "6", "tier": "1", "level": "3",
            "primaryStat": "Speed", "primaryValue": "18",
        }
        projected_five = project_mod_for_build(five_dot, {})
        projected_six = project_mod_for_build(six_dot, {})
        self.assertEqual(projected_five["primaryValue"], "2.8%")
        self.assertEqual(projected_six["primaryValue"], "18")
        self.assertEqual(projected_five["dots"], "5")
        self.assertEqual(projected_six["dots"], "6")
        self.assertFalse(projected_five["projectionSliceApplied"])
        self.assertFalse(projected_five["projectionPrimaryProjected"])
        self.assertFalse(projected_six["projectionPrimaryProjected"])

    def test_primary_quality_uses_current_dot_tier_ceiling(self):
        profile = {
            "primary_preferences": {
                "Arrow": {"Speed": 1.0},
                "Square": {"Offense": 1.0},
                "Diamond": {"Defense": 1.0},
                "Triangle": {"Health": 1.0},
                "Circle": {"Protection": 1.0},
                "Cross": {"Potency": 1.0},
            },
            "secondary_preferences": {},
            "set_preferences": {},
        }

        def build(arrow_dots, arrow_primary):
            rows = []
            specs = [
                ("Arrow", "Speed", arrow_primary, arrow_dots),
                ("Square", "Offense", "8.5", 6),
                ("Diamond", "Defense", "20", 6),
                ("Triangle", "Health", "16", 6),
                ("Circle", "Protection", "24", 6),
                ("Cross", "Potency", "30", 6),
            ]
            for slot, stat, value, dots in specs:
                rows.append({
                    "id": slot, "slot": slot, "set": "Critical Chance",
                    "dots": str(dots), "tier": "5", "level": "15",
                    "equipped": "False", "assignedTo": "",
                    "primaryStat": stat, "primaryValue": value,
                    "modValue": "0",
                })
            return optimize_target_build(
                rows, {"TARGET"}, profiles={"TARGET": profile}
            )["TARGET"]["mods"]

        five_dot = build(5, "30")
        six_dot = build(6, "32")
        five_score = next(m["optimizerScore"] for m in five_dot if m["slot"] == "Arrow")
        six_score = next(m["optimizerScore"] for m in six_dot if m["slot"] == "Arrow")
        self.assertEqual(five_score, 6.67)
        self.assertEqual(six_score, 6.67)

    def test_five_a_is_not_sliced_in_build_projection(self):
        row = {
            "id": "five-a", "dots": "5", "tier": "5", "level": "15",
            "secondary1Stat": "Speed", "secondary1Value": "20",
            "secondary1Rolls": "4", "secondary1RawRolls": "500000|500000|500000|500000",
        }
        projected = project_mod_for_build(row, {"secondary_preferences": {"Speed": 1.0}})
        self.assertEqual(projected["dots"], "5")
        self.assertEqual(projected["projectionDots"], 5)
        self.assertEqual(projected["projectionType"], "15 (średnia)")
        self.assertFalse(projected["projectionSliceApplied"])
        self.assertFalse(projected["projectionCalibrationApplied"])
        self.assertEqual(projected["secondary1Value"], "20")


class RawRollScaleTests(unittest.TestCase):
    def test_flat_speed_raw_roll_uses_unscaled_roll_value_scale(self):
        row = {
            "secondary1Stat": "Speed",
            "secondary1Value": "4",
            "secondary1Rolls": "1",
            "secondary1RawRolls": "464520",
            "dots": "5",
        }
        stat, value, count, values = rolls(row, 1)
        self.assertAlmostEqual(values[0], 4.6452, places=4)
        self.assertAlmostEqual(quality(stat, value, count, values, 5), (4.6452 - 3.0) / 3.0, places=4)

    def test_percent_raw_roll_uses_unscaled_roll_value_scale(self):
        row = {
            "secondary1Stat": "Protection %",
            "secondary1Value": "3.36%",
            "secondary1Rolls": "2",
            "secondary1RawRolls": "1298|2067",
            "dots": "5",
        }
        stat, value, count, values = rolls(row, 1)
        self.assertAlmostEqual(values[0], 1.298, places=3)
        self.assertAlmostEqual(values[1], 2.067, places=3)
        expected = (((1.298 - 1.125) / (2.25 - 1.125)) + ((2.067 - 1.125) / (2.25 - 1.125))) / 2.0
        self.assertAlmostEqual(quality(stat, value, count, values, 5), expected, places=4)



class ExactSetComboTests(unittest.TestCase):
    def make_six_mods(self, counts):
        slots = ["Arrow", "Square", "Diamond", "Triangle", "Circle", "Cross"]
        remaining = []
        for set_name, count in counts.items():
            remaining.extend([set_name] * count)
        self.assertEqual(len(remaining), 6)
        return [{
            "id": slot + "-" + set_name, "slot": slot, "set": set_name,
            "dots": "6", "tier": "5", "level": "15",
            "equipped": "False", "assignedTo": "",
            "primaryStat": "Protection %", "primaryValue": "24", "modValue": "0",
        } for slot, set_name in zip(slots, remaining)]

    def test_exact_combo_frequency_preserves_double_and_triple_multiplicity(self):
        from mod_analyzer import profile_set_combo_match, canonical_set_combo_from_mods
        profile = {"set_combinations": {
            "Double Health + Defense": 30.0,
            "Health + Double Defense": 12.0,
            "Triple Health": 9.0,
        }}
        common = self.make_six_mods({"Health": 4, "Defense": 2})
        less_common = self.make_six_mods({"Health": 2, "Defense": 4})
        self.assertEqual(canonical_set_combo_from_mods(common), "Double Health + Defense")
        self.assertEqual(canonical_set_combo_from_mods(less_common), "Double Defense + Health")
        self.assertEqual(profile_set_combo_match(profile, common)["frequency"], 30.0)
        self.assertEqual(profile_set_combo_match(profile, common)["preference"], 1.0)
        self.assertEqual(profile_set_combo_match(profile, less_common)["frequency"], 12.0)
        self.assertAlmostEqual(profile_set_combo_match(profile, less_common)["preference"], 0.4)

    def test_exact_combo_aliases_are_canonicalized_and_unknown_combo_falls_back(self):
        from mod_analyzer import profile_set_combo_match, canonical_set_combo_from_mods
        profile = {"set_combinations": {"Offense + Crit Chance": 25.0, "Triple Health": 10.0}}
        mods = self.make_six_mods({"Offense": 4, "Critical Chance": 2})
        self.assertEqual(canonical_set_combo_from_mods(mods), "Offense + Critical Chance")
        self.assertEqual(profile_set_combo_match(profile, mods)["frequency"], 25.0)
        self.assertIsNone(profile_set_combo_match(profile, self.make_six_mods({"Health": 4, "Defense": 2})))

    def test_tie_break_mode_keeps_scores_unchanged_and_uses_combo_only_after_existing_ties(self):
        profile = {
            "set_combinations": {
                "Double Health + Defense": 60.0,
                "Double Defense + Health": 20.0,
                "Triple Health": 10.0,
                "Triple Defense": 10.0,
            },
            "secondary_preferences": {},
            "set_preferences": {"Health": 1.0, "Defense": 1.0},
        }
        rows = []
        for slot in ["Square", "Diamond", "Circle", "Arrow", "Triangle", "Cross"]:
            for set_name in ["Health", "Defense"]:
                rows.append({
                    "id": slot + "-" + set_name, "slot": slot, "set": set_name,
                    "dots": "6", "tier": "5", "level": "15",
                    "equipped": "False", "assignedTo": "",
                    "primaryStat": "Protection %", "primaryValue": "24", "modValue": "0",
                })
        base = optimize_target_build(rows, {"TARGET"}, profiles={"TARGET": profile},
                                     set_combo_mode="base")["TARGET"]
        tie = optimize_target_build(rows, {"TARGET"}, profiles={"TARGET": profile},
                                    set_combo_mode="tie_break")["TARGET"]
        self.assertEqual(tie["totalScore"], base["totalScore"])
        self.assertEqual(tie["baseScore"], base["baseScore"])
        self.assertEqual(tie["setBonusScore"], base["setBonusScore"])
        self.assertEqual(tie["setPreferenceScore"], base["setPreferenceScore"])
        self.assertEqual(tie["setComboKey"], "Double Health + Defense")
        self.assertEqual(tie["setComboFrequency"], 60.0)

    def test_exact_mode_prefers_the_most_frequent_observed_combo(self):
        profile = {
            "set_combinations": {
                "Double Health + Defense": 60.0, "Double Defense + Health": 20.0,
                "Triple Health": 10.0, "Triple Defense": 10.0,
            },
            "secondary_preferences": {},
            "set_preferences": {"Health": 1.0, "Defense": 1.0},
        }
        rows = []
        for slot in ["Square", "Diamond", "Circle", "Arrow", "Triangle", "Cross"]:
            for set_name in ["Health", "Defense"]:
                rows.append({
                    "id": slot + "-" + set_name, "slot": slot, "set": set_name,
                    "dots": "6", "tier": "5", "level": "15",
                    "equipped": "False", "assignedTo": "",
                    "primaryStat": "Protection %", "primaryValue": "24", "modValue": "0",
                })
        result = optimize_target_build(rows, {"TARGET"}, profiles={"TARGET": profile},
                                       set_combo_mode="exact")["TARGET"]
        counts = {}
        for mod in result["mods"]:
            counts[mod["set"]] = counts.get(mod["set"], 0) + 1
        self.assertEqual(counts, {"Health": 4, "Defense": 2})
        self.assertEqual(result["setComboKey"], "Double Health + Defense")
        self.assertEqual(result["setComboFrequency"], 60.0)


class ProfileNormalizationTests(unittest.TestCase):
    def test_percent_primary_matches_swgoh_gg_label_without_percent(self):
        profile = {"primary_preferences": {"Triangle": {"Critical Damage": 0.82}}}
        self.assertAlmostEqual(
            profile_primary_preference(profile, "Triangle", "Critical Damage %"),
            0.82,
        )

    def test_percent_secondary_maps_only_known_swgoh_gg_aliases(self):
        profile = {"secondary_preferences": {"Tenacity": 0.7, "Health": 0.4}}
        self.assertAlmostEqual(profile_secondary_preference(profile, "Tenacity %"), 0.7)
        self.assertEqual(profile_secondary_preference(profile, "Health %"), 0.0)
        self.assertAlmostEqual(profile_secondary_preference(profile, "Health"), 0.4)

    def test_set_preferences_aggregate_base_sets_from_combinations(self):
        profile = {
            "set_combinations": {
                "Double Health + Defense": 50.0,
                "Triple Health": 30.0,
                "Speed + Health": 20.0,
                "Offense + Crit Chance": 10.0,
            },
            "set_preferences": {"Health": 0.1},
        }
        prefs = profile_set_preferences(profile)
        self.assertAlmostEqual(prefs["Health"], 1.0)
        self.assertAlmostEqual(prefs["Defense"], 0.5)
        self.assertAlmostEqual(prefs["Speed"], 0.2)
        self.assertAlmostEqual(prefs["Offense"], 0.1)
        self.assertAlmostEqual(prefs["Critical Chance"], 0.1)


class DonorProfileImpactTests(unittest.TestCase):
    def test_rare_set_combination_is_not_material_donor_loss(self):
        profile = {"set_combinations": {
            "Speed + Health": 52.3,
            "Crit Damage + Health": 6.3,
            "Speed + Defense": 11.4,
            "Triple Health": 8.3,
        }}
        self.assertAlmostEqual(profile_set_combo_support(profile, "Defense"), 11.4)
        self.assertLess(profile_set_combo_support(profile, "Defense"), 20.0)

    def test_common_scorch_defense_combinations_are_material(self):
        profile = {"set_combinations": {
            "Double Health + Defense": 48.9,
            "Double Defense + Health": 16.65,
            "Triple Health": 14.35,
            "Triple Defense": 6.45,
        }}
        self.assertAlmostEqual(profile_set_combo_support(profile, "Defense"), 72.0)
        self.assertGreaterEqual(profile_set_combo_support(profile, "Defense"), 20.0)


class UserReportTests(unittest.TestCase):
    def test_report_is_actionable_and_marks_donor_set_loss_as_compromise(self):
        current = {
            "id": "current-square", "assignedTo": "target-instance", "equipped": True,
            "slot": "Square", "set": "Health", "primaryStat": "Offense %",
            "primaryValue": "8.5%", "dots": "6", "tierName": "C", "level": "15",
            "secondary1Stat": "Speed", "secondary1Value": "11",
        }
        selected = {
            "id": "selected-square", "assignedTo": "", "equipped": False,
            "slot": "Square", "set": "Defense", "primaryStat": "Offense %",
            "primaryValue": "5.88%", "dots": "5", "tierName": "A", "level": "15",
            "secondary1Stat": "Speed", "secondary1Value": "5",
        }
        patch = {
            "id": "patch-square", "assignedTo": "", "equipped": False,
            "slot": "Square", "set": "Health", "primaryStat": "Offense %",
            "primaryValue": "0.63%", "dots": "5", "tierName": "D", "level": "1",
            "secondary1Stat": "Speed", "secondary1Value": "4",
        }
        aliases = {"target-instance": "VEL", "donor-instance": "DONOR"}
        names = {"VEL": "Vel Sartha", "DONOR": "Dawca"}
        def display_name(owner_id):
            base = aliases.get(owner_id, owner_id)
            return names.get(owner_id) or names.get(base) or base or "MAGAZYN"

        report = render_user_report(
            rows=[current],
            optimizer={"VEL": {"mods": [selected], "gain": 5.1}},
            chain_result={
                "safe": True,
                "plans": [{
                    "target": "VEL", "target_owner": "target-instance",
                    "mod": selected, "target_current": current,
                    "moves": [{
                        "owner": "donor-instance", "name": "Dawca",
                        "replacement": patch, "removed": None, "gain": -1.0,
                    }],
                }],
                "validation": [{
                    "owner": "donor-instance", "name": "Dawca",
                    "beforeModValue": 10.0, "afterModValue": 12.0,
                    "modValueDelta": 2.0,
                    "beforeComboKey": "Double Health + Defense",
                    "beforeComboFrequency": 50.0,
                    "afterComboKey": "Triple Health",
                    "afterComboFrequency": 15.0,
                    "setChanges": [{
                        "set": "Defense", "status": "ROZBITO",
                        "beforeFull": 1, "afterFull": 0,
                    }],
                }],
                "failed": [],
            },
            profiles={"VEL": {"source_model": {"sources": [
                {"name": "Kyber", "units_fully_modded": 10},
                {"name": "Top 100 Guilds", "units_fully_modded": 20},
            ]}}},
            aliases=aliases, names=names, target_ids={"VEL"},
            profile_fetch_status={"VEL": "cached", "DONOR": "cached"},
            display_name=display_name,
        )
        self.assertIn("KOMPROMIS", report)
        self.assertIn("Kolejność przekładania", report)
        self.assertIn("PATCH", report)
        self.assertIn("Vel Sartha", report)
        self.assertIn("Kombinacja setów: Double Health + Defense (50.0%) → Triple Health (15.0%)", report)
        self.assertIn("Fit pojedynczych modów wg profilu dawcy: Square -1.0 pkt", report)
        self.assertNotIn("UPGRADE:", report)
        self.assertNotIn("Zdejmij", report)
        self.assertNotIn("Zdejmowany z Vel", report)
        self.assertLess(report.index("**Square — załóż na Vel Sartha"), report.index("**PATCH — załóż na Dawca"))



    def test_report_groups_all_target_mods_before_tiered_donor_repairs(self):
        def mod(mid, slot, owner_id="", equipped=False):
            return {
                "id": mid, "slot": slot, "equipped": equipped,
                "assignedTo": owner_id, "set": "Defense",
                "primaryStat": "Protection %", "primaryValue": "24%",
                "dots": "6", "tierName": "A", "level": "15",
                "secondary1Stat": "Speed", "secondary1Value": "10",
            }

        target_arrow = mod("target-arrow", "Arrow", "target-instance", True)
        target_square = mod("target-square", "Square", "target-instance", True)
        donor_one_mod = mod("donor-one-mod", "Square", "donor-one", True)
        donor_two_mod = mod("donor-two-mod", "Square", "donor-two", True)
        inventory_patch = mod("inventory-patch", "Square")
        donor_two_patch = mod("donor-two-patch", "Square", "donor-three", True)
        aliases = {
            "target-instance": "VEL", "donor-one": "DONOR_ONE",
            "donor-two": "DONOR_TWO", "donor-three": "DONOR_THREE",
        }
        names = {
            "VEL": "Vel Sartha", "DONOR_ONE": "Dawca pierwszy",
            "DONOR_TWO": "Dawca drugi", "DONOR_THREE": "Dawca trzeci",
        }
        def display_name(owner_id):
            base_id = aliases.get(owner_id, owner_id)
            return names.get(owner_id) or names.get(base_id) or base_id or "MAGAZYN"

        plans = [
            {"target": "VEL", "target_owner": "target-instance", "mod": target_square,
             "target_current": mod("old-square", "Square", "target-instance", True),
             "moves": [
                 {"owner": "donor-one", "name": "Dawca pierwszy",
                  "replacement": donor_one_mod},
                 {"owner": "donor-two", "name": "Dawca drugi",
                  "replacement": donor_two_patch},
             ]},
            {"target": "VEL", "target_owner": "target-instance", "mod": target_arrow,
             "target_current": mod("old-arrow", "Arrow", "target-instance", True),
             "moves": [
                 {"owner": "donor-two", "name": "Dawca drugi",
                  "replacement": inventory_patch},
             ]},
        ]
        report = render_user_report(
            rows=[target_arrow, target_square],
            optimizer={"VEL": {"mods": [target_arrow, target_square], "gain": 1.0}},
            chain_result={"safe": True, "plans": plans, "validation": [], "failed": []},
            profiles={"VEL": {"source_model": {"sources": []}}},
            aliases=aliases, names=names, target_ids={"VEL"},
            profile_fetch_status={"VEL": "cached"}, display_name=display_name,
        )
        first_patch = report.index("**PATCH — załóż na")
        last_target_mod = report.rindex("— załóż na Vel Sartha")
        level_one = report.index("### Uzupełnienie dawców — poziom 1")
        level_two = report.index("### Uzupełnienie dawców — poziom 2")
        self.assertLess(last_target_mod, first_patch)
        self.assertLess(level_one, level_two)
        self.assertNotIn("Zdejmij", report)
        self.assertEqual(report.count("**PATCH — załóż na"), 3)


    def test_report_orders_target_mods_by_slot_before_donor_repairs(self):
        def mod(mid, slot, equipped, assigned_to, set_name):
            return {
                "id": mid, "slot": slot, "equipped": equipped,
                "assignedTo": assigned_to, "set": set_name,
                "primaryStat": "Protection %", "primaryValue": "24%",
                "dots": "6", "tierName": "A", "level": "15",
                "secondary1Stat": "Speed", "secondary1Value": "10",
            }

        current_circle = mod("old-circle", "Circle", True, "target-instance", "Health")
        current_square = mod("old-square", "Square", True, "target-instance", "Health")
        selected_circle = mod("new-circle", "Circle", False, "", "Defense")
        selected_square = mod("new-square", "Square", False, "", "Defense")
        aliases = {"target-instance": "VEL"}
        names = {"VEL": "Vel Sartha"}
        def display_name(owner_id):
            base = aliases.get(owner_id, owner_id)
            return names.get(owner_id) or names.get(base) or base or "MAGAZYN"

        plans = [
            {"target": "VEL", "target_owner": "target-instance", "mod": selected_circle,
             "target_current": current_circle, "moves": []},
            {"target": "VEL", "target_owner": "target-instance", "mod": selected_square,
             "target_current": current_square, "moves": []},
        ]
        report = render_user_report(
            rows=[current_circle, current_square],
            optimizer={"VEL": {"mods": [selected_circle, selected_square], "gain": 0.0}},
            chain_result={"safe": True, "plans": plans, "validation": [], "failed": []},
            profiles={"VEL": {"source_model": {"sources": [
                {"name": "Kyber", "units_fully_modded": 1},
                {"name": "Top 100 Guilds", "units_fully_modded": 2},
            ]}}},
            aliases=aliases, names=names, target_ids={"VEL"},
            profile_fetch_status={"VEL": "cached"}, display_name=display_name,
        )
        self.assertLess(
            report.index("**Square — załóż na Vel Sartha"),
            report.index("**Circle — załóż na Vel Sartha"),
        )
        self.assertNotIn("Zdejmij", report)


class TransferChainTests(unittest.TestCase):
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

    def test_profile_exact_combo_preservation_precedes_higher_local_fit(self):
        selected = make_mod("selected-circle", DONOR, True, slot="Circle", value=10, mod_set="Defense")
        donor_mods = [
            make_mod("donor-arrow", DONOR, True, slot="Arrow", mod_set="Health"),
            make_mod("donor-square", DONOR, True, slot="Square", mod_set="Health"),
            make_mod("donor-diamond", DONOR, True, slot="Diamond", mod_set="Defense"),
            make_mod("donor-triangle", DONOR, True, slot="Triangle", mod_set="Health"),
            make_mod("donor-cross", DONOR, True, slot="Cross", mod_set="Health"),
        ]
        health_patch = make_mod("health-patch", value=30, slot="Circle", mod_set="Health")
        health_patch.update({
            "dots": "6", "primaryStat": "Protection %", "primaryValue": "24%",
            "secondary1Stat": "Speed", "secondary1Value": "30",
            "secondary1Rolls": "5",
        })
        defense_patch = make_mod("defense-patch", value=10, slot="Circle", mod_set="Defense")
        defense_patch.update({
            "dots": "6", "primaryStat": "Protection %", "primaryValue": "24%",
            "secondary1Stat": "Defense", "secondary1Value": "8",
            "secondary1Rolls": "1",
        })
        profile = {
            "set_combinations": {
                "Double Health + Defense": 50.0,
                "Triple Health": 15.0,
            },
            "primary_preferences": {"Circle": {"Protection": 1.0}},
            "secondary_preferences": {"Speed": 1.0},
        }
        result = apply_optimizer_replacements(
            [selected, *donor_mods, health_patch, defense_patch],
            {"TARGET": {"mods": [selected]}},
            {"TARGET"},
            profiles={"DONOR": profile},
            aliases={TARGET: "TARGET", DONOR: "DONOR"},
        )
        self.assertTrue(result["safe"], result["failed"])
        move = result["plans"][0]["moves"][0]
        # Health has a better individual fit, but it would destroy the donor's
        # observed Double Health + Defense six-mod combination.
        self.assertEqual(move["replacement"]["id"], "defense-patch")
        self.assertEqual(move["combo_delta"], 0.0)
        self.assertEqual(move["set_delta"], 0)

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

    def test_two_independent_inventory_patches_do_not_conflict(self):
        selected_arrow = make_mod("selected-arrow", DONOR, True, slot="Arrow", value=20)
        selected_square = make_mod("selected-square", DONOR_B, True, slot="Square", value=20)
        arrow_patch = make_mod("arrow-patch", slot="Arrow", value=15)
        square_patch = make_mod("square-patch", slot="Square", value=15)
        result = apply_optimizer_replacements(
            [selected_arrow, selected_square, arrow_patch, square_patch],
            {"TARGET": {"mods": [selected_arrow, selected_square]}},
            {"TARGET"},
            aliases={TARGET: "TARGET", DONOR: "DONOR", DONOR_B: "DONOR_B"},
        )
        self.assertTrue(result["safe"], result["failed"])
        self.assertEqual(len(result["plans"]), 2)
        self.assertEqual(
            {plan["mod"]["id"] for plan in result["plans"]},
            {"selected-arrow", "selected-square"},
        )

    def test_exact_report_order_replay_uses_shortest_inventory_repair(self):
        selected = make_mod("selected-mod", DONOR, True, slot="Arrow", value=20)
        donor_two_mod = make_mod("donor-two-mod", DONOR_B, True, slot="Arrow", value=15)
        inventory_patch = make_mod("inventory-patch", slot="Arrow", value=12)
        result = apply_optimizer_replacements(
            [selected, donor_two_mod, inventory_patch],
            {"TARGET": {"mods": [selected]}},
            {"TARGET"},
            aliases={TARGET: "TARGET", DONOR: "DONOR", DONOR_B: "DONOR_B"},
        )
        self.assertTrue(result["safe"], result["failed"])
        self.assertTrue(result["report_order_validated"])
        actions = result["report_execution_order"]
        # The planner intentionally prefers a directly executable inventory
        # repair over a longer donor-to-donor chain.
        self.assertEqual([item["action"] for item in actions], ["MOD", "PATCH"])
        self.assertEqual([item["mod_id"] for item in actions], [
            "selected-mod", "inventory-patch"
        ])
        self.assertEqual(actions[1]["depth"], 1)

    def test_exact_report_order_replay_places_all_target_mods_before_patches(self):
        selected_arrow = make_mod("selected-arrow", DONOR, True, slot="Arrow", value=20)
        selected_square = make_mod("selected-square", DONOR_B, True, slot="Square", value=20)
        arrow_patch = make_mod("arrow-patch", slot="Arrow", value=15)
        square_patch = make_mod("square-patch", slot="Square", value=15)
        result = apply_optimizer_replacements(
            [selected_arrow, selected_square, arrow_patch, square_patch],
            {"TARGET": {"mods": [selected_arrow, selected_square]}},
            {"TARGET"},
            aliases={TARGET: "TARGET", DONOR: "DONOR", DONOR_B: "DONOR_B"},
        )
        self.assertTrue(result["safe"], result["failed"])
        self.assertTrue(result["report_order_validated"])
        actions = result["report_execution_order"]
        self.assertEqual([item["action"] for item in actions], ["MOD", "MOD", "PATCH", "PATCH"])
        self.assertEqual([item["slot"] for item in actions], ["Arrow", "Square", "Arrow", "Square"])
        self.assertTrue(all(item["depth"] == 1 for item in actions[2:]))

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


if __name__ == "__main__":
    unittest.main()
