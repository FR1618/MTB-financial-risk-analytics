# M&T Bank — Financial Risk Analytics Dashboard
### Live Dashboard
[Explore the M&T Bank Financial Risk Analytics Dashboard](https://fr1618-mtb-risk.streamlit.app/)


**A self-directed financial analytics portfolio project** built with Python, Pandas, Plotly, and Streamlit.

## Business question

How did M&T Bank's publicly reported financial performance and credit-quality indicators change, and which movements deserve further investigation?

## Features

- **Quarterly credit-quality comparison:** net income, provisions for credit losses, nonaccrual loans, and net charge-offs for Q3 2025, Q2 2026, and Q3 2026.
- **QoQ/YoY analysis:** dollar and percentage changes, with illustrative monitoring flags.
- **Criticized C&I + CRE loan trends:** five-quarter chart and reported share of the combined C&I/CRE loan base. **Not CRE-only figures.**
- **SEC financial facts:** retrieves standardized company XBRL facts from the SEC API, caches responses for 15 minutes, validates required fields, and can fall back to a previously saved CSV.
- **Interactive visualization and CSV export:** Streamlit dashboard and Plotly charts.

## Tech stack

Python · Pandas · Plotly · Streamlit · SEC XBRL API · Git / GitHub

## Data sources

- [M&T Bank Q3 2026 earnings release](https://ir.mtb.com/news-releases/news-release-details/mt-bank-corporation-nysemtb-announces-third-quarter-2026-results)
- [M&T Bank Q3 2026 earnings presentation, p. 18](https://ir.mtb.com/static-files/5e370b06-317f-4dd2-a3e9-9bccff37b8bb)
- [SEC Company Facts for M&T Bank Corporation](https://data.sec.gov/api/xbrl/companyfacts/CIK0000036270.json)

## Accuracy and limitations

- Credit-quality and C&I/CRE data are an **historical Q3 2026 snapshot**; they do **not** update automatically. The SEC financial facts section can refresh on demand and uses a cached copy for up to 15 minutes.
- Risk flags use illustrative rules: more than a 5% QoQ decrease in net income or more than a 10% QoQ increase in other selected indicators. These are **not M&T Bank's internal risk thresholds**.
- The criticized-loan time series combines commercial & industrial (C&I) **and** commercial real estate (CRE) loans. It does not isolate CRE.
- The saved CSV backup is a **manual snapshot**, not a persistently auto-updating database. If SEC retrieval fails, the app labels backup data as potentially outdated.
- This is a portfolio analysis using public information, not an official M&T Bank product or investment advice.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

On Windows, if `python` is not recognized but the Python launcher is available, try `py -m pip install -r requirements.txt` and `py -m streamlit run app.py`.

For SEC requests, set a `SEC_USER_AGENT` with your name and a valid contact email using environment variables or Streamlit secrets:

```toml
SEC_USER_AGENT = "Your Name your-real-email@example.com"
```

Do not commit personal contact details or secrets into the public repository.

## Test

```bash
python -m unittest discover -s tests -v
```

The GitHub Actions workflow runs syntax checks and credit-calculation tests when code is pushed.

## Potential next steps

Add source-specific extraction for CRE-only balances and criticized loans; save validated datasets to persistent cloud storage; and extend historical coverage.
