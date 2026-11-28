"""M&T Bank Q3 2026 reported credit-quality indicators.

This is a fixed historical snapshot, NOT live credit-quality data.
Source: https://ir.mtb.com/news-releases/news-release-details/mt-bank-corporation-nysemtb-announces-third-quarter-2026-results
"""

import pandas as pd

EARNINGS_SOURCE = (
    "https://ir.mtb.com/news-releases/news-release-details/"
    "mt-bank-corporation-nysemtb-announces-third-quarter-2026-results"
)
CRE_PRESENTATION_SOURCE = (
    "https://ir.mtb.com/static-files/5e370b06-317f-4dd2-a3e9-9bccff37b8bb"
)

# Reported amounts in USD millions; not forecasts or synthetic data.
CREDIT_QUALITY = [
    {"Indicator": "Net income", "Q3 2025": 792, "Q2 2026": 818, "Q3 2026": 775},
    {"Indicator": "Provision for credit losses", "Q3 2025": 125, "Q2 2026": 120, "Q3 2026": 135},
    {"Indicator": "Nonaccrual loans", "Q3 2025": 1512, "Q2 2026": 1208, "Q3 2026": 1298},
    {"Indicator": "Net charge-offs", "Q3 2025": 146, "Q2 2026": 80, "Q3 2026": 127},
]

# These amounts and percentages refer to C&I AND CRE combined, not CRE alone.
CRITICIZED_CI_CRE = [
    {"Quarter": "Q3 2025", "Criticized loans ($B)": 7.8, "Share of C&I + CRE loans (%)": 9.1},
    {"Quarter": "Q4 2025", "Criticized loans ($B)": 7.3, "Share of C&I + CRE loans (%)": 8.4},
    {"Quarter": "Q1 2026", "Criticized loans ($B)": 6.6, "Share of C&I + CRE loans (%)": 7.4},
    {"Quarter": "Q2 2026", "Criticized loans ($B)": 5.9, "Share of C&I + CRE loans (%)": 6.5},
    {"Quarter": "Q3 2026", "Criticized loans ($B)": 6.1, "Share of C&I + CRE loans (%)": 6.6},
]


def build_credit_quality_table() -> pd.DataFrame:
    """Calculate reported quarter comparisons and illustrative monitoring flags."""
    df = pd.DataFrame(CREDIT_QUALITY).copy()
    for column in ("Q3 2025", "Q2 2026", "Q3 2026"):
        df[column] = pd.to_numeric(df[column], errors="raise")
        if (df[column] < 0).any():
            raise ValueError(f"Negative amount in {column}")

    df["QoQ change ($M)"] = df["Q3 2026"] - df["Q2 2026"]
    df["QoQ change (%)"] = (df["QoQ change ($M)"] / df["Q2 2026"] * 100).round(2)
    df["YoY change (%)"] = (
        (df["Q3 2026"] - df["Q3 2025"]) / df["Q3 2025"] * 100
    ).round(2)

    # Illustrative monitoring thresholds, NOT official bank credit-risk limits.
    income_drop = (df["Indicator"] == "Net income") & (df["QoQ change (%)"] < -5)
    other_increase = (df["Indicator"] != "Net income") & (df["QoQ change (%)"] > 10)
    df["Monitoring flag"] = "Within illustrative threshold"
    df.loc[income_drop | other_increase, "Monitoring flag"] = "Review movement"
    return df


def criticized_ci_cre_table() -> pd.DataFrame:
    """Five-quarter combined C&I and CRE criticized-loan trends."""
    return pd.DataFrame(CRITICIZED_CI_CRE).copy()
