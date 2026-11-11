import unittest

from validate_mod_target_report import parse_targets, validate_report


def report_for(target, slots=("Arrow", "Square", "Diamond", "Triangle", "Circle", "Cross")):
    rows = "\n".join("| {} | mod | MAGAZYN | 70.0 |".format(slot) for slot in slots)
    return (
        "### {} — najlepszy wirtualny build 6/6\n\n"
        "| Slot | Mod — parametry wyszukiwalne | Źródło | Fit |\n"
        "|---|---|---|---:|\n"
        "{}\n\n"
        "## BEZPIECZNY ŁAŃCUCH — walidacja globalna\n"
        "**STATUS: OK — transfery są fizycznie wykonalne.**\n"
    ).format(target, rows)


class TargetReportValidationTests(unittest.TestCase):
    def test_parse_target_list(self):
        self.assertEqual(parse_targets("50rt, JARJARBINKS,50RT"), ["50RT", "JARJARBINKS"])

    def test_accepts_complete_six_slot_build_and_chain_status(self):
        self.assertEqual(validate_report(report_for("50RT"), ["50RT"]), [])

    def test_rejects_missing_slot(self):
        errors = validate_report(report_for("50RT", ("Arrow", "Square", "Diamond", "Triangle", "Circle")), ["50RT"])
        self.assertTrue(any("dokładnie sześciu" in error for error in errors))

    def test_rejects_missing_target_build_even_if_chain_exists(self):
        report = "## BEZPIECZNY ŁAŃCUCH — walidacja globalna\n**STATUS: OK**"
        errors = validate_report(report, ["50RT"])
        self.assertTrue(any("brak sekcji kompletnego buildu" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
