"""Live SEC financial-facts panel for an existing M&T Streamlit app.

Source: https://data.sec.gov/api/xbrl/companyfacts/CIK0000036270.json
Figures are reported XBRL facts, not live banking balances or stock quotes.
Only standardized company-wide facts are included, not dimension-specific CRE data.
"""

import os
import re
from datetime import datetime, timezone

import pandas as pd
import requests

SEC_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK0000036270.json"
SOURCE_PAGE = "https://www.sec.gov/search-filings/edgar-application-programming-interfaces"

# The names describe the *exact* SEC taxonomy concepts used below.
# A metric appears only if M&T reports that concept in standardized XBRL.
METRICS = {
    "Total assets": ("Assets", "instant"),
    "Total deposits": ("Deposits", "instant"),
    "Net income": ("NetIncomeLoss", "quarter"),
    "Loans and leases, net": ("LoansAndLeasesReceivableNetReportedAmount", "instant"),
}


def parse_companyfacts(payload: dict) -> pd.DataFrame:
    """Turn quarterly SEC XBRL observations into a validated tidy DataFrame.

    For net income, only actual three-month facts with SEC quarter frames
    are used. This deliberately leaves Q4 blank if Q4 wasn't reported as an
    individual quarter in the API; it does not mistake FY income for Q4.
    """
    if not isinstance(payload, dict) or "facts" not in payload:
        raise ValueError("SEC response does not contain financial facts.")
    if str(payload.get("cik", "")).lstrip("0") != "36270":
        raise ValueError("SEC response is not for M&T Bank Corporation.")

    gaap_facts = payload.get("facts", {}).get("us-gaap", {})
    rows = []
    for label, (tag, kind) in METRICS.items():
        usd = gaap_facts.get(tag, {}).get("units", {}).get("USD", [])
        for fact in usd:
            if fact.get("form") not in ("10-K", "10-Q"):
                continue
            frame = fact.get("frame", "")
            expected = r"CY\d{4}Q[1-4]I" if kind == "instant" else r"CY\d{4}Q[1-4]"
            if not re.fullmatch(expected, frame):
                continue

            if kind == "quarter":
                if not fact.get("start"):
                    continue
                try:
                    days = (pd.Timestamp(fact["end"]) - pd.Timestamp(fact["start"])).days + 1
                except (ValueError, KeyError, TypeError):
                    continue
                if not 70 <= days <= 110:
                    continue

            try:
                end = pd.Timestamp(fact["end"])
                filed = pd.Timestamp(fact["filed"])
                value = float(fact["val"])
            except (ValueError, KeyError, TypeError, OverflowError):
                continue
            if not pd.notna(value) or end > pd.Timestamp.now():
                continue
            rows.append({
                "Metric": label,
                "Quarter": frame.replace("CY", "").replace("I", ""),
                "Period End": end,
                "Value (USD millions)": value / 1_000_000,
                "Filed": filed,
                "SEC Tag": tag,
            })

    if not rows:
        raise ValueError("No recognized quarterly M&T financial facts were returned.")
    df = pd.DataFrame(rows)
    # Prefer the most recently filed fact for each metric and quarter.
    df = df.sort_values(["Metric", "Period End", "Filed"])
    df = df.drop_duplicates(["Metric", "Period End"], keep="last")
    df = df.groupby("Metric", group_keys=False).tail(12)
    validate_metrics(df)
    return df.sort_values(["Metric", "Period End"]).reset_index(drop=True)


def validate_metrics(df: pd.DataFrame) -> None:
    required = {"Metric", "Quarter", "Period End", "Value (USD millions)", "Filed"}
    if not required.issubset(df.columns):
        raise ValueError("Missing required columns in financial dataset.")
    if df.empty or df[list(required)].isna().any().any():
        raise ValueError("Financial dataset is empty or contains missing required values.")
    if df.duplicated(["Metric", "Period End"]).any():
        raise ValueError("Financial dataset contains duplicate metric/quarter combinations.")
    if (df.loc[df["Metric"] != "Net income", "Value (USD millions)"] < 0).any():
        raise ValueError("Balance-sheet indicators must not be negative.")


def retrieve_sec_metrics(user_agent: str) -> tuple[pd.DataFrame, str]:
    """Fetch, parse and validate one official SEC companyfacts response."""
    if not user_agent or "@" not in user_agent:
        raise ValueError("Configure SEC_USER_AGENT with your name/organization and contact email.")
    response = requests.get(
        SEC_URL,
        headers={
            "User-Agent": user_agent,
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate",
        },
        timeout=30,
    )
    response.raise_for_status()
    df = parse_companyfacts(response.json())
    checked_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return df, checked_at


def show_mtb_sec_panel() -> None:
    """Add this panel to the end of an existing Streamlit app."""
    import streamlit as st

    st.divider()
    st.header("M&T Bank — Updated SEC Financial Data")
    st.caption("SEC-reported financial data, not real-time bank account balances or market prices.")

    user_agent = os.getenv("SEC_USER_AGENT", "")
    if not user_agent:
        try:
            user_agent = st.secrets.get("SEC_USER_AGENT", "")
        except Exception:
            user_agent = ""
    if not user_agent:
        st.info("One-time setup: Add SEC_USER_AGENT to your Streamlit app secrets, then reopen this page.")
        return

    @st.cache_data(ttl=900, show_spinner="Checking SEC financial data...")
    def _cached_fetch(agent: str) -> tuple[pd.DataFrame, str]:
        return retrieve_sec_metrics(agent)

    if st.button("Check for new SEC data now", key="sec_manual_refresh"):
        _cached_fetch.clear()

    try:
        df, checked_at = _cached_fetch(user_agent)
        validate_metrics(df)
    except (requests.RequestException, ValueError, TypeError) as exc:
        try:
            df = pd.read_csv("data/mtb_financial_backup.csv")

            df["Period End"] = pd.to_datetime(df["Period End"])
            df["Filed"] = pd.to_datetime(df["Filed"])
            df["Value (USD millions)"] = pd.to_numeric(
                df["Value (USD millions)"], errors="raise"
            )

            validate_metrics(df)
            checked_at = "Unavailable — using saved backup"

            st.warning(
                "SEC connection unavailable. Showing saved financial data, "
                "which may be outdated."
            )

        except (OSError, ValueError, TypeError, KeyError) as backup_error:
            st.error("Both SEC data and backup recovery failed.")
            st.caption(f"Backup error: {backup_error}"
            return

    latest_period = df["Period End"].max().date().isoformat()
    latest_filing = df["Filed"].max().date().isoformat()
    a, b, c = st.columns(3)
    a.metric("Most recent period", latest_period)
    b.metric("Most recent filing date", latest_filing)
    c.metric("Metrics available", df["Metric"].nunique())
    st.caption(f"SEC checked: {checked_at}. Results cached up to 15 minutes; use the button to check sooner.")

    metrics = sorted(df["Metric"].unique())
    selected = st.selectbox("Financial indicator", metrics, key="sec_metric_selector")
    subset = df[df["Metric"] == selected].sort_values("Period End")
    st.line_chart(subset, x="Quarter", y="Value (USD millions)")
    st.dataframe(
        df.sort_values(["Period End", "Metric"], ascending=[False, True]).assign(
            **{"Period End": lambda d: d["Period End"].dt.strftime("%Y-%m-%d"),
               "Filed": lambda d: d["Filed"].dt.strftime("%Y-%m-%d")}
        ),
        hide_index=True,
        use_container_width=True,
    )
    st.caption(f"Source: {SEC_URL}. Some quarters or specialized CRE measures may be unavailable in this API.")
    st.caption(f"SEC API documentation: {SOURCE_PAGE}")
