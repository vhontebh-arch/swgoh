import unittest

from validate_mod_target_report import parse_targets, validate_report
from test_user_mod_report import valid_report


class TargetReportValidationTests(unittest.TestCase):
    def test_parse_target_list(self):
        self.assertEqual(parse_targets("50rt, JARJARBINKS,50RT"), ["50RT", "JARJARBINKS"])

    def test_accepts_complete_user_report(self):
        self.assertEqual(validate_report(valid_report(), ["50RT"]), [])

    def test_rejects_missing_slot(self):
        report = valid_report().replace("#### Cross\n", "")
        errors = validate_report(report, ["50RT"])
        self.assertTrue(any("Brak sekcji slotu Cross." == error for error in errors))

    def test_rejects_missing_user_report_even_if_technical_chain_exists(self):
        report = "## BEZPIECZNY ŁAŃCUCH — walidacja globalna\n**STATUS: OK**"
        errors = validate_report(report, ["50RT"])
        self.assertTrue(any("Brak wymaganej sekcji raportu użytkowego" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
