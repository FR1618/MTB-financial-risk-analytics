"""Public-data portfolio dashboard for M&T Bank financial and credit-quality trends."""

import plotly.express as px
import streamlit as st

from credit_risk import (
    CRE_PRESENTATION_SOURCE,
    EARNINGS_SOURCE,
    build_credit_quality_table,
    criticized_ci_cre_table,
)
from sec_live import show_mtb_sec_panel

st.set_page_config(page_title="M&T Bank | Financial Risk Analytics", layout="wide")

st.title("M&T Bank | Financial Risk Analytics")
st.caption(
    "Independent portfolio project · Official public reporting · "
    "Q3 2026 credit-quality snapshot + refreshed SEC financial facts"
)

risk_df = build_credit_quality_table()
figures = risk_df.set_index("Indicator")

c1, c2, c3, c4 = st.columns(4)
for container, indicator, reverse in [
    (c1, "Net income", False),
    (c2, "Provision for credit losses", True),
    (c3, "Nonaccrual loans", True),
    (c4, "Net charge-offs", True),
]:
    metric = figures.loc[indicator]
    container.metric(
        label=f"{indicator} · Q3 2026",
        value=f"${metric['Q3 2026']:,.0f}M",
        delta=f"{metric['QoQ change (%)']:+.2f}% QoQ",
        delta_color="inverse" if reverse else "normal",
    )

summary_tab, cre_tab, sec_tab, about_tab = st.tabs(
    ["Credit quality", "C&I / CRE trends", "Live SEC facts", "Methodology"]
)

with summary_tab:
    st.subheader("Quarterly financial and credit-quality changes")
    st.caption("USD millions; quarter-on-quarter (QoQ) and year-on-year (YoY) comparisons.")
    st.dataframe(risk_df, hide_index=True, use_container_width=True)
    flags = risk_df[risk_df["Monitoring flag"] == "Review movement"]
    st.metric("Indicators flagged for review", len(flags))
    st.caption(
        "Flags are based on illustrative thresholds: net income decreases greater than 5%, "
        "or other listed indicators increasing more than 10% QoQ. "
        "They are not official M&T risk ratings or evidence of financial distress."
    )
    chart = px.bar(
        risk_df,
        x="Indicator",
        y="QoQ change (%)",
        color="Monitoring flag",
        title="Quarter-over-quarter percentage change — Q3 2026",
        labels={"QoQ change (%)": "QoQ change (%)"},
    )
    st.plotly_chart(chart, use_container_width=True)
    st.download_button(
        "Export credit-quality comparison (CSV)",
        risk_df.to_csv(index=False),
        file_name="mtb_q3_2026_credit_quality.csv",
        mime="text/csv",
    )
    st.markdown(f"[Source: M&T Bank Q3 2026 earnings release]({EARNINGS_SOURCE})")

with cre_tab:
    st.subheader("Criticized commercial & industrial and CRE loans")
    st.warning(
        "This reported series combines commercial & industrial (C&I) and "
        "commercial real estate (CRE) loans. It must not be interpreted as CRE-only exposure."
    )
    cre_df = criticized_ci_cre_table()
    cre_chart = px.bar(
        cre_df,
        x="Quarter",
        y="Criticized loans ($B)",
        title="Criticized C&I + CRE loans · reported five-quarter trend",
    )
    st.plotly_chart(cre_chart, use_container_width=True)
    st.dataframe(cre_df, hide_index=True, use_container_width=True)
    st.caption(
        "As of Q3 2026: $6.1B criticized C&I + CRE loans, "
        "representing 6.6% of the reported combined loan base. "
        "Snapshot values will not update until a new investor presentation is verified."
    )
    st.markdown(f"[Source: M&T Bank Q3 2026 investor presentation, p. 18]({CRE_PRESENTATION_SOURCE})")

with sec_tab:
    show_mtb_sec_panel()
    st.info(
        "The SEC tab refreshes published XBRL financial facts when available. "
        "The other two tabs show a separately verified Q3 2026 historical snapshot."
    )

with about_tab:
    st.subheader("Methods and limitations")
    st.markdown(
        """
**Project purpose:** Compare public M&T Bank earnings and credit-quality disclosures,
calculate QoQ/YoY movements, and illustrate monitoring workflows.

**Data freshness:** The SEC tab retrieves standardized company financial facts with
15-minute caching and a saved CSV fallback. Credit-quality and C&I/CRE charts
are fixed to the **Q3 2026 reporting snapshot** and do not refresh automatically.

**Risk flags:** Simple demonstration rules, not a model of default probability,
not bank-internal classifications, and not investment advice.

**Limitations:** No confidential loan-level data or proprietary credit scoring.
Specialized CRE disclosures are not fully available through the company-wide SEC API.
        """
    )
    st.markdown(f"[Earnings release]({EARNINGS_SOURCE}) | [CRE presentation]({CRE_PRESENTATION_SOURCE})")
