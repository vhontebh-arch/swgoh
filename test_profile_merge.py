import unittest

from mod_analyzer import merge_profiles


class ProfileMergeTests(unittest.TestCase):
    def test_adding_donor_profiles_preserves_target_profiles(self):
        target = {"50RT": {"name": "50R-T"}}
        donor = {"GLREY": {"name": "GL Rey"}}

        merged = merge_profiles(target, donor)

        self.assertEqual(merged["50RT"], target["50RT"])
        self.assertEqual(merged["GLREY"], donor["GLREY"])
        self.assertEqual(set(merged), {"50RT", "GLREY"})

    def test_new_profile_can_refresh_existing_key_without_dropping_others(self):
        existing = {
            "50RT": {"version": 1},
            "SCORCH": {"version": 1},
        }
        additional = {"SCORCH": {"version": 2}}

        merged = merge_profiles(existing, additional)

        self.assertEqual(merged["SCORCH"]["version"], 2)
        self.assertEqual(merged["50RT"]["version"], 1)


if __name__ == "__main__":
    unittest.main()
