import unittest
from character_ranking import can_transfer_by_rank

RANKING = [
    {"character": "Top", "base_id": "TOP", "rank": 1},
    {"character": "Mid", "base_id": "MID", "rank": 20},
    {"character": "Low", "base_id": "LOW", "rank": 100},
]
ALIASES = {"top-unit": "TOP", "mid-unit": "MID", "low-unit": "LOW"}


class RankTransferGateTests(unittest.TestCase):
    def test_more_important_character_cannot_donate_to_less_important(self):
        self.assertFalse(can_transfer_by_rank("top-unit", "LOW", RANKING, ALIASES))
        self.assertFalse(can_transfer_by_rank("mid-unit", "LOW", RANKING, ALIASES))

    def test_less_important_character_can_donate_to_more_important(self):
        self.assertTrue(can_transfer_by_rank("low-unit", "TOP", RANKING, ALIASES))
        self.assertTrue(can_transfer_by_rank("low-unit", "MID", RANKING, ALIASES))

    def test_equal_rank_is_allowed(self):
        same = [{"base_id": "SAME", "rank": 7}]
        self.assertTrue(can_transfer_by_rank("SAME", "SAME", same))

    def test_inventory_has_no_source_and_is_allowed(self):
        self.assertTrue(can_transfer_by_rank("", "TOP", RANKING, ALIASES))

    def test_unknown_source_or_recipient_rank_fails_closed(self):
        self.assertFalse(can_transfer_by_rank("missing", "TOP", RANKING, ALIASES))
        self.assertFalse(can_transfer_by_rank("low-unit", "missing", RANKING, ALIASES))


if __name__ == "__main__":
    unittest.main()
