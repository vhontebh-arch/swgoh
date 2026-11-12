import unittest
from sync_optimizer_data import git_blob_sha

class OptimizerDataSyncTests(unittest.TestCase):
    def test_git_blob_sha_matches_git_object_format(self):
        self.assertEqual(git_blob_sha(b"test\n"), "9daeafb9864cf43055ae93beb0afd6c7d144bfa4")

    def test_empty_blob_hash(self):
        self.assertEqual(git_blob_sha(b""), "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391")

if __name__ == "__main__":
    unittest.main()
