"""Automated checks for a historical, publicly reported M&T data snapshot."""

import unittest

from credit_risk import build_credit_quality_table, criticized_ci_cre_table


class CreditQualityTest(unittest.TestCase):
    def test_expected_reported_amounts(self):
        df = build_credit_quality_table().set_index("Indicator")
        self.assertEqual(df.loc["Net income", "Q3 2026"], 775)
        self.assertEqual(df.loc["Net charge-offs", "Q2 2026"], 80)
        self.assertEqual(df.loc["Nonaccrual loans", "Q3 2026"], 1298)

    def test_percentage_based_alerts(self):
        df = build_credit_quality_table().set_index("Indicator")
        self.assertAlmostEqual(df.loc["Net income", "QoQ change (%)"], -5.26)
        self.assertAlmostEqual(df.loc["Net charge-offs", "QoQ change (%)"], 58.75)
        self.assertEqual(df.loc["Net income", "Monitoring flag"], "Review movement")
        self.assertEqual(df.loc["Nonaccrual loans", "Monitoring flag"], "Within illustrative threshold")
        self.assertEqual((df["Monitoring flag"] == "Review movement").sum(), 3)

    def test_critized_series_is_combined(self):
        df = criticized_ci_cre_table()
        self.assertEqual(len(df), 5)
        self.assertEqual(df.iloc[-1]["Criticized loans ($B)"], 6.1)
        self.assertEqual(df.iloc[-1]["Share of C&I + CRE loans (%)"], 6.6)


if __name__ == "__main__":
    unittest.main()
