import unittest
from datetime import date

from character_ranking import get_character_rank, rank_characters


def row(base_id, count, release, r7=None, r9=None):
    counts = {"r5_plus": count}
    if r7 is not None:
        counts["r7_plus"] = r7
    if r9 is not None:
        counts["r9_plus"] = r9
    return {
        "base_id": base_id,
        "name": base_id,
        "release_date": date.fromisoformat(release) if release else None,
        "counts": counts,
    }


class RankingTests(unittest.TestCase):
    def test_recent_character_competes_with_age_peers(self):
        rows = [
            row("OLD_A", 1000, "2018-01-01"),
            row("OLD_B", 900, "2018-02-01"),
            row("OLD_C", 800, "2018-03-01"),
            row("OLD_D", 700, "2018-04-01"),
            row("NEW_A", 100, "2026-01-01"),
            row("NEW_B", 80, "2026-02-01"),
            row("NEW_C", 60, "2026-03-01"),
            row("NEW_D", 40, "2026-04-01"),
            row("NEW_E", 20, "2026-05-01"),
        ]
        result = rank_characters(rows, as_of=date(2026, 11, 16))
        new_a = get_character_rank(result, "NEW_A")
        self.assertIsNotNone(new_a)
        self.assertTrue(new_a["age_adjustment_applied"])
        self.assertGreater(new_a["rank_score"], new_a["global_score"])

    def test_missing_release_date_falls_back_to_global(self):
        result = rank_characters([
            row("A", 100, None), row("B", 50, None),
            row("C", 25, None), row("D", 10, None),
        ])
        self.assertFalse(result[0]["age_adjustment_applied"])
        self.assertEqual(result[0]["rank_score"], result[0]["global_score"])

    def test_missing_relic_tiers_are_supported(self):
        result = rank_characters([
            row("A", 100, None, 80, 40),
            row("B", 50, None, 20, 5),
            row("C", 25, None, 10, 1),
            row("D", 10, None, 2, 0),
        ])
        self.assertIn("r9_plus", result[0]["tier_percentiles"])

    def test_sorted_and_ranked(self):
        result = rank_characters([
            row("A", 10, None), row("B", 100, None),
            row("C", 50, None),
        ])
        self.assertEqual([item["rank"] for item in result], [1, 2, 3])
        self.assertEqual(result[0]["base_id"], "B")


if __name__ == "__main__":
    unittest.main()
