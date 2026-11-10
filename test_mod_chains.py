import unittest

from mod_analyzer import apply_optimizer_replacements


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
