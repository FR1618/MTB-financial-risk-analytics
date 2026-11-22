import pandas as pd
import streamlit as st
import plotly.express as px



# M&T Bank reported financial data
# Source: Q3 2026 Earnings Release
# All amounts in USD millions

risk_data = {
    "Financial Indicator": [
        "Net Income",
        "Provision for Credit Losses",
        "Nonaccrual Loans",
        "Net Charget-offs"
     ],
     "Q3 2025": [792, 125, 1512, 146],
     "Q2 2026": [818, 120, 1208, 80],
     "Q3 2026": [775, 135, 1298, 127]
}

risk_df = pd.DataFrame(risk_data)

# Calculate quarterly dollar change
risk_df["QoQ Change ($M)"] = (
    risk_df["Q3 2026"] - risk_df["Q2 2026"]
)

# Calculate quarterly percentage change
risk_df["QoQ Change (%)"] = (
    risk_df["QoQ Change ($M)"] / risk_df["Q2 2026"] * 100
).round(2)

#Calculate year-over-year percentage change
risk_df["YoY Change (%)"] = (
    (risk_df["Q3 2026"] - risk_df["Q3 2025"])
    / risk_df["Q3 2025"] * 100
).round(2)  

print(risk_df.to_string(index=False))

# Identify potentially adverse financial changes
def classify_risk(row):
    indicators = row["Financial Indicator"]
    change = row["QoQ Change ($M)"]

    if indicators == "Net Income":
        if change < -5:
            return "Review Required"

    else: 
        if change > 10:
            return "Review Required"

    return "Stable"

risk_df["Risk Classification"] = risk_df.apply(classify_risk, axis=1)

st.divider()
st.header("M&T Bank Credit Risk Analysis")

st.dataframe(risk_df, hide_index=True)

risk_alerts = risk_df[
    risk_df["Risk Classification"] == "Review Required"
]

st.metric("indicators Requiring Review", len(risk_alerts))

st.subheader("Quarter-over-Quarter Risk indicators")

fig_risk = px.bar(
    risk_df,
    x="Financial Indicator",
    y="QoQ Change ($M)",
    color="Risk Classification",
    title="Quarter-over-Quarter Change in Financial Indicators",
    labels={"QoQ Change ($M)": "Change in USD Millions"},           
)

st.plotly_chart(fig_risk, use_container_width=True)
