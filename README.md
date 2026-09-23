# EQUICAFI

## Equity Intelligence Engine

EQUICAFI is an educational equity-research application that combines company fundamentals, valuation, historical analysis, technical indicators, risk metrics, cross-metric reasoning, and hypothetical scenario modelling in one research workspace.

The goal is simple: help users understand a company from multiple financial perspectives instead of relying on a single number or ratio.

---

## 🚀 What can EQUICAFI do?

### Fundamental Analysis

Study company performance through:

- Revenue
- Revenue Growth
- Gross Profit
- Gross Margin
- Operating Profit
- Operating Margin
- Net Profit
- Net Margin
- EPS
- EPS Growth
- ROE
- ROA
- ROCE
- Operating Cash Flow
- Capex
- Free Cash Flow
- FCF / Net Income
- Operating Cash Flow / Net Income

### Balance Sheet & Financial Coverage

Examine financial structure through:

- Debt / Equity
- Interest Coverage
- Net Debt / Operating Cash Flow
- FCF / Debt
- Cash / Debt
- Liquidity Coverage
- Quick Liquidity Coverage

### Valuation

Study market-pricing relationships through:

- P/E
- P/B
- P/S
- EV / EBITDA
- EV / Sales
- Earnings Yield
- FCF Yield
- Dividend Yield

### Technical Analysis

Review observed market-price behaviour through:

- Current Price
- 52-Week High
- 52-Week Low
- Distance from High
- Distance from Low
- SMA 20
- SMA 50
- EMA 20
- RSI 14

### Risk Analysis

Review historical market and financial risk through:

- Maximum Drawdown
- Annualized Volatility
- Downside Volatility
- Worst Daily Return
- Positive Session Rate
- Leverage
- Coverage
- Liquidity
- Cash-flow measures

### Cross-Metric Reasoning

EQUICAFI connects multiple metrics into a structured analytical picture.

For example:

> Revenue growth + margins + cash flow + leverage + valuation

The reasoning layer is designed to help users understand how different signals relate to one another.

### Capital Lab

Capital Lab is a hypothetical scenario-modelling tool.

It can model:

- Hypothetical capital
- Whole-share deployment
- Remaining cash
- Annual return assumptions
- Final value
- Profit / Loss
- Total ROI
- CAGR

Capital Lab is mathematical scenario analysis. It does not determine a personal investment amount or provide personalised investment advice.

---

# 🧭 How to use EQUICAFI

Using the application is straightforward.

### Step 1 — Enter a ticker

Enter a supported market ticker in the research desk.

For Indian NSE-listed equity examples, try:

```text
RELIANCE.NS
TCS.NS
INFY.NS
HDFCBANK.NS
ICICIBANK.NS
SBIN.NS
ITC.NS
Step 2 — Analyse the company

Click:

Analyse Equity

EQUICAFI retrieves the available company and market data and builds the research result.

Step 3 — Start with Overview

Overview gives a compact view of the latest available signals.

It is the recommended starting point before exploring the detailed sections.

Step 4 — Explore the research sections

Overview
A compact view of the latest key signals.

Fundamentals
Business performance, profitability and cash-flow metrics.

History
Historical financial and valuation changes.

Valuation
Market-pricing relationships and valuation multiples.

Technicals & Risk
Observed price behaviour, technical indicators and risk measurements.

Reasoning
Relationships between multiple financial signals.

Capital Lab
Hypothetical scenario mathematics.

🔎 Which companies can EQUICAFI analyze?

EQUICAFI is designed primarily for equity-company research.

Many NSE-listed equities can be entered using the provider's ticker format, commonly:

SYMBOL.NS

Examples include:

RELIANCE.NS
TCS.NS
INFY.NS
HDFCBANK.NS
ICICIBANK.NS
SBIN.NS
ITC.NS

However, NSE-listed does not automatically mean every security will have complete coverage.

Data availability depends on the underlying market-data provider and may vary by:

Security
Instrument type
Historical period
Financial statement availability
Metric availability

Some securities may therefore return incomplete or unavailable metrics.

EQUICAFI should be understood as a broad equity-research application with provider-dependent data coverage rather than a guarantee that every listed security will have every metric available.

🧪 DEMO mode

Enter:

DEMO

DEMO uses synthetic demonstration data.

It is intended for exploring the interface and analytical workflow and does not represent a live company or live market position.

🧠 Understanding the metrics

EQUICAFI is designed to explain important metrics rather than simply display numbers.

For major metrics, the dashboard provides:

Simple
A plain-language explanation.

Professional
The formal financial definition.

Formula
How the metric is calculated.

Why it matters
Why analysts use the metric.

Caveat
An important limitation or context point.

This makes EQUICAFI useful as both an analytical and educational research environment.

📚 Example research workflow
Choose a company
       ↓
Overview
       ↓
Fundamentals
       ↓
History
       ↓
Valuation
       ↓
Technicals & Risk
       ↓
Reasoning
       ↓
Capital Lab

The purpose is to examine evidence across multiple dimensions rather than rely on one metric.

🛠️ Technology

EQUICAFI is built with:

Python
Pandas
NumPy
Pydantic
yfinance
Streamlit
Plotly
SQLite
Pytest

The application uses a provider-based architecture so market-data providers are separated from the analysis engine.

🏗️ Project Structure
EQUICAFI/
│
├── dashboard/
│   └── app.py
│
├── equicafi/
│   ├── analysis/
│   ├── database/
│   ├── models/
│   ├── providers/
│   ├── reporting/
│   └── services/
│
├── scripts/
├── tests/
├── docs/
├── requirements.txt
├── pyproject.toml
├── README.md
└── LICENSE

💻 Run EQUICAFI locally

Create the virtual environment:

python -m venv .venv

Activate it:

.venv\Scripts\Activate.ps1

Install the project:

pip install -e .

Start the dashboard:

streamlit run dashboard\app.py

Then open the local URL shown in the terminal.

🧪 Testing

Run the test suite:

python -m pytest -q

The test suite covers analysis, providers, valuation, technical and risk calculations, reasoning, reporting, database behaviour and scenario calculations.

⚠️ Data & Limitations

EQUICAFI depends on the availability and quality of the underlying market-data provider.

Financial and market data may be:

unavailable for some securities
incomplete for some periods
revised
delayed
insufficient to calculate certain metrics

Individual metrics should therefore be interpreted in context rather than treated as standalone conclusions.

Capital Lab uses hypothetical assumptions for mathematical scenario modelling.

EQUICAFI is intended for education, research and software demonstration.

📜 License

MIT License
'@ | Set-Content ".\README.md" -Encoding UTF8


## STEP 2 — Press Enter

After you press Enter, the README will be replaced.

There may be **no big success message**. That's okay.

## STEP 3 — Push it to GitHub

Now paste:

```powershell
git add README.md
git commit -m "Polish public README"
git push