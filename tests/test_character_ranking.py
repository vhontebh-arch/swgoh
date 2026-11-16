import tempfile
import unittest
from pathlib import Path

from character_ranking import (
    EXPECTED_COLUMNS, SOURCE_NAME, build_payload, get_character_rank,
    load_stack_rank, rank_characters,
)


def tsv(rows):
    lines = ["\t".join(EXPECTED_COLUMNS)]
    lines.extend("\t".join(str(value) for value in row) for row in rows)
    return "\n".join(lines) + "\n"


def row(rank, name, final_tier, base_tier=None, synergy=0, omicron=0):
    values = {
        "Rank": rank, "Character": name, "Sort Score": "5.00",
        "SubSort Score": "12.1000", "Final Tier": final_tier,
        "Base Tier": base_tier if base_tier is not None else final_tier,
        "Synergy Enhancement": synergy, "Omicron Boost": omicron,
        "Omicron Synergy Boost": 0, "Relic Gear Level": "13.3",
        "Ability Score": 0,
    }
    return [values[column] for column in EXPECTED_COLUMNS]


class StackRankImportTests(unittest.TestCase):
    def test_import_preserves_tier_and_rank_as_separate_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stack.tsv"
            path.write_text(tsv([
                row(1, "A", 2), row(2, "B", 5, 8, 3),
                row(3, "C", 5, 5),
            ]), encoding="utf-8")
            data = load_stack_rank(path)
        self.assertEqual(data[1]["rank"], 2)
        self.assertEqual(data[1]["final_tier"], 5)
        self.assertEqual(data[1]["base_tier"], 8)
        self.assertEqual(data[1]["importance_score"], 15)
        self.assertEqual(data[1]["synergy_enhancement"], 3)

    def test_primary_sort_is_final_tier_then_source_rank(self):
        rows = [
            {"character": "B", "rank": 1, "final_tier": 5},
            {"character": "A", "rank": 9, "final_tier": 2},
            {"character": "C", "rank": 3, "final_tier": 5},
        ]
        self.assertEqual(
            [x["character"] for x in rank_characters(rows)], ["A", "B", "C"]
        )

    def test_lookup_is_case_insensitive(self):
        item = {"character": "Grogu & Anzellans", "rank": 270, "final_tier": 10}
        self.assertEqual(
            get_character_rank([item], "grogu & anzellans")["rank"], 270
        )

    def test_rejects_duplicate_names_and_invalid_tiers(self):
        for rows in (
            [row(1, "A", 2), row(2, "a", 3)],
            [row(1, "A", 20)],
        ):
            with self.subTest(rows=rows), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "bad.tsv"
                path.write_text(tsv(rows), encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_stack_rank(path)

    def test_repository_snapshot_has_313_rows(self):
        snapshot = Path(__file__).resolve().parents[1] / "data" / "stack_rank.tsv"
        data = load_stack_rank(snapshot)
        self.assertEqual(len(data), 313)
        self.assertEqual(data[0]["character"], "Rey")
        self.assertEqual(data[0]["final_tier"], 2)
        ben = get_character_rank(data, "Ben Solo")
        self.assertEqual(ben["rank"], 16)
        self.assertEqual(ben["final_tier"], 5)
        grogu = get_character_rank(data, "Grogu & Anzellans")
        self.assertEqual(grogu["rank"], 270)
        self.assertEqual(grogu["final_tier"], 10)

    def test_generated_payload_declares_single_source(self):
        snapshot = Path(__file__).resolve().parents[1] / "data" / "stack_rank.tsv"
        payload = build_payload(snapshot)
        self.assertEqual(payload["source"], SOURCE_NAME)
        self.assertEqual(payload["record_count"], 313)
        self.assertTrue(all(x["source"] == SOURCE_NAME for x in payload["characters"]))


if __name__ == "__main__":
    unittest.main()
