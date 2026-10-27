import unittest

from rote_planner.src.operations_planner import plan_operations


class OperationsPlannerTests(unittest.TestCase):
    def test_fills_synthetic_slots_and_prefers_lower_relic(self):
        data = {
            "members": [
                {"ally_code": "111", "name": "A", "units": [
                    {"unit_base_id": "ALPHA", "stars": 7, "relic": 5, "gp": 200},
                    {"unit_base_id": "BETA", "stars": 7, "relic": 7, "gp": 300},
                ]},
                {"ally_code": "222", "name": "B", "units": [
                    {"unit_base_id": "ALPHA", "stars": 7, "relic": 6, "gp": 250},
                    {"unit_base_id": "GAMMA", "stars": 7, "relic": 5, "gp": 180},
                ]},
            ],
            "platoons": [{"platoon_id": "P1", "planet_id": "PLANET1", "phase": 1,
                "slots": [
                    {"slot_id": "S1", "unit_base_id": "ALPHA", "required_stars": 7, "required_relic": 5},
                    {"slot_id": "S2", "unit_base_id": "BETA", "required_stars": 7, "required_relic": 5},
                    {"slot_id": "S3", "unit_base_id": "GAMMA", "required_stars": 7, "required_relic": 5},
                ]}],
        }
        result = plan_operations(data)
        self.assertEqual(result["summary"]["assigned_count"], 3)
        alpha = next(a for a in result["assignments"] if a["unit_base_id"] == "ALPHA")
        self.assertEqual(alpha["ally_code"], "111")
        self.assertEqual(result["summary"]["unfilled_count"], 0)

    def test_respects_tier_requirements(self):
        data = {
            "members": [{"ally_code": "111", "units": [
                {"unit_base_id": "ALPHA", "stars": 6, "relic": 8, "gp": 200}
            ]}],
            "platoons": [{"platoon_id": "P1", "planet_id": "PLANET1", "phase": 1,
                "slots": [{"slot_id": "S1", "unit_base_id": "ALPHA",
                           "required_stars": 7, "required_relic": 5}]}],
        }
        result = plan_operations(data)
        self.assertEqual(result["summary"]["assigned_count"], 0)
        self.assertEqual(result["summary"]["unfilled_count"], 1)

    def test_does_not_donate_same_character_twice_to_same_planet_phase(self):
        data = {
            "members": [{"ally_code": "111", "units": [
                {"unit_base_id": "ALPHA", "stars": 7, "relic": 5, "gp": 200}
            ]}],
            "platoons": [
                {"platoon_id": "P1", "planet_id": "PLANET1", "phase": 1,
                 "slots": [{"slot_id": "S1", "unit_base_id": "ALPHA", "required_stars": 7}]},
                {"platoon_id": "P2", "planet_id": "PLANET1", "phase": 1,
                 "slots": [{"slot_id": "S2", "unit_base_id": "ALPHA", "required_stars": 7}]},
            ],
        }
        result = plan_operations(data)
        self.assertEqual(result["summary"]["assigned_count"], 1)
        self.assertEqual(result["summary"]["unfilled_count"], 1)


if __name__ == "__main__":
    unittest.main()
