import unittest

from validate_mod_target_report import validate_report
from mod_analyzer import account_balance_summary


def valid_report():
    parts = [
        "# Raport modów — Vel Sartha",
        "## Status",
        "- **Wykonalność fizyczna:** POTWIERDZONA",
        "- **Ocena:** REKOMENDACJA",
        "### Sześć modów docelowych",
    ]
    for slot in ("Arrow", "Square", "Diamond", "Triangle", "Circle", "Cross"):
        parts += [
            "#### " + slot,
            "- **Obecny mod:** " + slot + " / Health / primary / secondary / 5★ A lvl15",
            "- **Proponowany mod:** " + slot + " / Health / primary / secondary / 5★ A lvl15",
        ]
    parts += [
        "## MOD — mody przenoszone na cel",
        "1. Merrin → Vel — pełny opis moda",
        "## PATCH — uzupełnienie dawców",
        "- MAGAZYN → Merrin — pełny opis moda",
        "## Kolejność przekładania",
        "1. **MOD:** załóż mod na Vel",
        "2. **PATCH:** załóż mod na Merrin",
        "## Bilans całej operacji — ta sama punktacja przed/po",
        "| Postać | Rola w łańcuchu | Wynik przed | Wynik po | Zmiana |",
        "**ŁĄCZNA ZMIANA: +4.20 pkt.**",
        "## Wpływ na postacie-dawców",
        "- **Merrin — wynik pełnego buildu wg profilu:** 45.00 → 44.20 (-0.80 pkt).",
        "  - Σ modValue modów: 10 → 12 (+2) — surowy wskaźnik jakości modów, nie wynik profilu.",
        "## Założenia projekcji",
        "## Kontrola profili użytych w łańcuchu",
        "- Vel: cached",
    ]
    return "\n".join(parts)


class AccountBalanceTests(unittest.TestCase):
    def test_sums_target_and_all_donors_with_same_profile_score(self):
        validation = [
            {"owner": "VEL", "profileScoreAvailable": True, "profileScoreDelta": 12.5},
            {"owner": "SCORCH", "profileScoreAvailable": True, "profileScoreDelta": -8.0},
            {"owner": "SANA", "profileScoreAvailable": True, "profileScoreDelta": -1.2},
        ]
        items, total = account_balance_summary(
            validation, {"VEL", "SCORCH", "SANA"},
            {"VEL": {"ok": True}, "SCORCH": {"ok": True}, "SANA": {"ok": True}}, {}
        )
        self.assertEqual(len(items), 3)
        self.assertEqual(total, 3.3)

    def test_refuses_to_mix_profile_score_with_modvalue_fallback(self):
        validation = [
            {"owner": "VEL", "profileScoreAvailable": True, "profileScoreDelta": 12.5},
            {"owner": "SCORCH", "profileScoreAvailable": False, "profileScoreDelta": None},
        ]
        items, total = account_balance_summary(
            validation, {"VEL", "SCORCH"}, {"VEL": {"ok": True}}, {}
        )
        self.assertEqual(len(items), 2)
        self.assertIsNone(total)


    def test_blocked_chain_does_not_report_target_as_a_donor(self):
        from mod_analyzer import render_user_report

        report = render_user_report(
            rows=[],
            optimizer={"KLEYA": {"mods": [], "gain": 12.5}},
            chain_result={
                "safe": False,
                "plans": [{"target_owner": "KLEYA", "mod": {"assignedTo": ""}, "moves": []}],
                "validation": [{
                    "owner": "KLEYA", "name": "Kleya",
                    "beforeProfileScore": 0.0, "afterProfileScore": 12.5,
                    "profileScoreDelta": 12.5, "beforeModValue": 0.0,
                    "afterModValue": 64.3, "modValueDelta": 64.3,
                    "setChanges": [],
                }],
                "failed": [("KLEYA", "blocked")],
            },
            profiles={"KLEYA": {}},
            aliases={},
            names={},
            target_ids={"KLEYA"},
            profile_fetch_status={},
            display_name=lambda value: value,
        )
        self.assertNotIn("## Wpływ na postacie-dawców", report)
        self.assertIn("NIEZATWIERDZONY — łańcuch przekładek jest zablokowany", report)

class UserReportValidationTests(unittest.TestCase):
    def test_accepts_complete_vel_style_user_report(self):
        self.assertEqual(validate_report(valid_report(), ["VEL"]), [])

    def test_rejects_technical_optimizer_dump_even_if_six_slot_section_exists(self):
        report = (
            "## Globalny optimizer 6-slotowy\n"
            "## Najważniejsi kandydaci\n"
            "| Akcja | Mod | Źródło | Set | Tier |\n"
            "### VEL — najlepszy wirtualny build 6/6\n"
            "## BEZPIECZNY ŁAŃCUCH — walidacja globalna\n"
            "**STATUS: OK**\n"
        )
        errors = validate_report(report, ["VEL"])
        self.assertTrue(any("raportu użytkowego" in e for e in errors))
        self.assertTrue(any("techniczny raport" in e for e in errors))

    def test_rejects_donor_section_with_only_raw_mod_value(self):
        report = valid_report().replace(
            "- **Merrin — wynik pełnego buildu wg profilu:** 45.00 → 44.20 (-0.80 pkt).",
            "- Merrin: modValue 10 → 12 (+2)",
        ).replace(
            "  - Σ modValue modów: 10 → 12 (+2) — surowy wskaźnik jakości modów, nie wynik profilu.",
            "",
        )
        errors = validate_report(report, ["VEL"])
        self.assertTrue(any("wyniku pełnego buildu dawcy" in e for e in errors))

    def test_rejects_missing_current_mod_or_patch_section(self):
        report = valid_report().replace("- **Obecny mod:** Arrow / Health / primary / secondary / 5★ A lvl15\n", "")
        report = report.replace("## PATCH — uzupełnienie dawców\n", "")
        errors = validate_report(report, ["VEL"])
        self.assertTrue(any("Arrow: brak pełnego opisu obecnego moda." == e for e in errors))
        self.assertTrue(any("## PATCH — uzupełnienie dawców" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
