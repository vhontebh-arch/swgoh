import unittest

from character_ranking import rank_importance_score, rank_weighted_donor_delta, rank_weighted_account_delta


_NAMED_RANKS = {
    10: ("Jedi Knight Revan", "JEDIKNIGHTREVAN"),
    62: ("Scorch", "SCORCH"),
    76: ("50R-T", "50RT"),
    135: ("Sana Starros", "SANASTARROS"),
    174: ("Merrin", "MERRIN"),
    218: ("Vel", "VEL"),
    302: ("4-LOM", "FOURLOM"),
}
RANKING = [
    {"character": _NAMED_RANKS.get(rank, (f"Filler {rank}", f"FILLER{rank}"))[0],
     "base_id": _NAMED_RANKS.get(rank, (f"Filler {rank}", f"FILLER{rank}"))[1],
     "rank": rank}
    for rank in range(1, 314)
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
        self.assertAlmostEqual(first, -10.0 * rank_importance_score(10, len(RANKING)))

    def test_account_objective_weights_target_and_donors_symmetrically(self):
        aliases = {
            "gopherants-unit": "GROGUANZELLANS",
            "piett-unit": "ADMIRALPIETT",
        }
        ranking = RANKING + [
            {"character": "Grogu & Anzellans", "base_id": "GROGUANZELLANS", "rank": 270},
            {"character": "Admiral Piett", "base_id": "ADMIRALPIETT", "rank": 2},
        ]
        moves = [
            {"owner": "gopherants-unit", "gain": 109.41},
            {"owner": "piett-unit", "gain": -5.79},
        ]
        expected = (
            109.41 * rank_importance_score(270, len(ranking))
            - 5.79 * rank_importance_score(2, len(ranking))
        )
        self.assertAlmostEqual(
            rank_weighted_account_delta(moves, ranking, aliases), expected, places=5
        )


if __name__ == "__main__":
    unittest.main()
