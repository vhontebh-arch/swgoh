import unittest

from character_ranking import rank_importance_score, rank_weighted_donor_delta


RANKING = [
    {"character": "Jedi Knight Revan", "base_id": "JEDIKNIGHTREVAN", "rank": 10},
    {"character": "Scorch", "base_id": "SCORCH", "rank": 62},
    {"character": "50R-T", "base_id": "50RT", "rank": 76},
    {"character": "Sana Starros", "base_id": "SANASTARROS", "rank": 135},
    {"character": "Merrin", "base_id": "MERRIN", "rank": 174},
    {"character": "Vel", "base_id": "VEL", "rank": 218},
    {"character": "4-LOM", "base_id": "FOURLOM", "rank": 302},
]


class RankWeightedChainSelectionTests(unittest.TestCase):
    def test_kleya_full_recursive_chain_beats_jkr_only_patch(self):
        aliases = {
            "jkr-unit": "JEDIKNIGHTREVAN",
            "scorch-unit": "SCORCH",
            "50rt-unit": "50RT",
            "sana-unit": "SANASTARROS",
            "merrin-unit": "MERRIN",
            "vel-unit": "VEL",
            "4lom-unit": "FOURLOM",
        }
        full_chain = [
            {"owner": "merrin-unit", "gain": -0.93},
            {"owner": "50rt-unit", "gain": 43.79},
            {"owner": "sana-unit", "gain": -1.48},
            {"owner": "vel-unit", "gain": -6.59},
            {"owner": "scorch-unit", "gain": -16.52},
            {"owner": "4lom-unit", "gain": 0.0},
            {"owner": "jkr-unit", "gain": -23.33},
        ]
        jkr_only = [{"owner": "jkr-unit", "gain": -43.58}]

        full_donor_score = rank_weighted_donor_delta(full_chain, RANKING, aliases)
        jkr_only_score = rank_weighted_donor_delta(jkr_only, RANKING, aliases)

        self.assertAlmostEqual(full_donor_score, -22.46992, places=4)
        self.assertAlmostEqual(jkr_only_score, -125.784064, places=3)
        self.assertGreater(116.41 + full_donor_score, 0)
        self.assertLess(116.41 + jkr_only_score, 0)
        self.assertGreater(full_donor_score, jkr_only_score)

    def test_rank_weighting_groups_multiple_patch_steps_for_same_donor(self):
        moves = [
            {"owner": "jkr-unit", "gain": -10.0},
            {"owner": "jkr-unit", "gain": -5.0},
        ]
        aliases = {"jkr-unit": "JEDIKNIGHTREVAN"}
        expected = -15.0 * rank_importance_score(10, len(RANKING))
        self.assertAlmostEqual(
            rank_weighted_donor_delta(moves, RANKING, aliases), expected, places=5
        )

    def test_missing_rank_falls_back_to_neutral_weight(self):
        moves = [{"owner": "unknown-unit", "gain": -12.5}]
        self.assertEqual(rank_weighted_donor_delta(moves, RANKING), -12.5)

    def test_target_gain_is_not_part_of_donor_objective(self):
        moves = [{"owner": "jkr-unit", "gain": -10.0}]
        aliases = {"jkr-unit": "JEDIKNIGHTREVAN"}
        first = rank_weighted_donor_delta(moves, RANKING, aliases)
        # The caller adds target gain separately and unweighted.
        self.assertAlmostEqual(first, -10.0 * rank_importance_score(10, len(RANKING)))


if __name__ == "__main__":
    unittest.main()
