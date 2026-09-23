# EQUICAFI

### Equity Intelligence Engine

**EQUICAFI** is an educational equity-research platform that brings fundamental analysis, valuation, historical trends, technical indicators, risk metrics, cross-metric reasoning, and hypothetical scenario modelling into a single structured research workspace.

> Research the business. Understand the numbers. Connect the signals.

---

## Overview

Financial analysis usually means jumping between financial statements, ratios, charts, and multiple data sources just to build a coherent picture of a company. EQUICAFI brings these perspectives together into one guided research workflow, so a company can be examined from multiple angles instead of relying on a single number or ratio in isolation.

It is built as both a **research tool** and a **learning tool** — every major metric comes with a plain-language explanation alongside its formal definition, so the platform is useful whether you're a student, a developer exploring the codebase, or someone just getting comfortable with equity analysis.

**Research workflow:**

```
Company → Fundamentals → Financial Structure → History → Valuation → Technicals & Risk → Reasoning → Capital Lab
```

---

## What EQUICAFI Does

### Fundamental Analysis
Operating performance, profitability, efficiency, and cash generation.

| Category | Metrics |
|---|---|
| Growth & Profitability | Revenue, Revenue Growth, Gross Profit, Gross Margin, Operating Profit, Operating Margin, Net Profit, Net Margin, EPS, EPS Growth |
| Returns | ROE, ROA, ROCE |
| Cash Flow | Operating Cash Flow, Capex, Free Cash Flow, FCF / Net Income, Operating Cash Flow / Net Income |

### Financial Structure & Coverage
Leverage, liquidity, and debt servicing.

- Debt / Equity
- Interest Coverage
- Net Debt / Operating Cash Flow
- FCF / Debt
- Cash / Debt
- Liquidity Coverage
- Quick Liquidity Coverage

### Historical Analysis
Tracks how financial and valuation metrics evolve over time, giving context to recent performance rather than viewing it in isolation.

### Valuation
How the market prices a company relative to its fundamentals.

- P/E, P/B, P/S
- EV / EBITDA, EV / Sales
- Earnings Yield, FCF Yield, Dividend Yield

### Technical Analysis
Observed market price behaviour.

- Current Price, 52-Week High/Low, Distance from High/Low
- SMA 20, SMA 50, EMA 20
- RSI 14

### Risk Analysis
Observed market and financial risk.

- Maximum Drawdown, Annualized Volatility, Downside Volatility
- Worst Daily Return, Positive Session Rate
- Debt / Equity, Interest Coverage, Liquidity & Cash-flow measures

### Cross-Metric Reasoning
Rather than treating each number in isolation, EQUICAFI connects related signals — for example, reading **Revenue Growth + Margins + Cash Flow + Leverage + Valuation** together to understand how they interact and what that combination might suggest about the business.

### Capital Lab
A **hypothetical scenario-modelling** environment for exploring "what if" mathematics:

- Hypothetical capital and whole-share deployment
- Remaining cash after deployment
- Annual return assumptions
- Final value, Profit / Loss, Total ROI, CAGR

> Capital Lab is mathematical scenario analysis for educational exploration. It does not determine a personal investment amount and does not provide personalised investment advice.

---

## Designed to Explain, Not Just Display

For supported metrics, the dashboard breaks each one down into:

| Layer | Purpose |
|---|---|
| **Simple** | A plain-language explanation |
| **Professional** | The formal financial definition |
| **Formula** | How the metric is calculated |
| **Why It Matters** | Why it's useful in analysis |
| **Caveat** | Important context or limitations |

This is what makes EQUICAFI both an analytical workspace and a learning tool, not just a numbers dashboard.

---

## Getting Started

### 1. Enter a Ticker

EQUICAFI is designed primarily for equity-company research. Indian NSE-listed equities can be entered using the provider's ticker convention, `SYMBOL.NS`, for example:

`RELIANCE.NS` · `TCS.NS` · `INFY.NS` · `HDFCBANK.NS` · `ICICIBANK.NS` · `SBIN.NS` · `ITC.NS`

> Being listed on NSE does not guarantee complete data coverage. Availability can vary by security, instrument type, historical period, financial statement availability, and data-provider coverage — some securities may return incomplete or unavailable metrics.

### 2. Click Analyse Equity

EQUICAFI retrieves the available company and market data and builds the research result.

### 3. Start with Overview

Overview gives a compact view of the latest available signals before drilling into a specific area.

### 4. Explore the Research Desk

| Tab | What it shows |
|---|---|
| Overview | Latest key signals |
| Fundamentals | Business performance, profitability, cash flow |
| History | How metrics change over time |
| Valuation | Market-pricing relationships |
| Technicals & Risk | Price behaviour and risk measurements |
| Reasoning | Relationships between multiple financial signals |
| Capital Lab | Hypothetical scenario mathematics |

### Try DEMO Mode

Enter `DEMO` to explore the interface, analytical workflow, metric presentation, reasoning layer, and Capital Lab using synthetic demonstration data. DEMO mode does not represent a real company or live market position.

---

## Architecture

EQUICAFI separates data access, financial calculations, analytical reasoning, persistence, reporting, and presentation:

```
Market Data Providers
        ↓
Analysis Services
        ↓
Fundamentals + Valuation + Technicals + Risk
        ↓
Cross-Metric Reasoning
        ↓
Capital Lab
        ↓
Streamlit Research Dashboard
```

This separation keeps the analytical engine independent of the user interface.

---

## Technology Stack

| Technology | Role |
|---|---|
| Python | Core application |
| Pandas | Data manipulation |
| NumPy | Numerical computation |
| Pydantic | Structured data models |
| yfinance | Market and company data |
| Streamlit | Interactive dashboard |
| Plotly | Data visualization |
| SQLite | Local persistence |
| Pytest | Automated testing |

---

## Project Structure

```
dashboard/            Streamlit interface
equicafi/analysis/     Financial and analytical calculations
equicafi/providers/    Market-data providers
equicafi/services/     Application services
equicafi/database/     Persistence
equicafi/reporting/    Reporting
tests/                 Automated tests
docs/                  Project documentation
```

## Data Provider

The current public-market implementation uses a provider-based architecture, sourcing data via `yfinance` (Yahoo Finance). A synthetic DEMO provider is included separately for interface and workflow exploration. Data availability may vary by security and metric.

---

## Running Locally

**1. Create a virtual environment**

```bash
python -m venv .venv
```

**2. Activate it**

```bash
.venv\Scripts\Activate.ps1
```

**3. Install the project**

```bash
pip install -e .
```

**4. Launch the dashboard**

```bash
streamlit run dashboard\app.py
```

The terminal will display the local application URL.

## Testing

```bash
python -m pytest -q
```

The test suite covers analysis, data providers, fundamentals, valuation, technical calculations, risk calculations, cross-metric reasoning, reporting, database behaviour, and scenario calculations.

---

## Data & Analytical Limitations

EQUICAFI depends on the availability and quality of its underlying market-data provider. Financial and market data may be:

- Unavailable for certain securities
- Incomplete for particular periods
- Revised or delayed
- Insufficient to calculate certain metrics

Different security types can also require different analytical frameworks — for example, banks and other financial institutions typically need sector-specific measures that aren't equivalent to metrics used for industrial or technology companies. Individual metrics should be interpreted in context rather than treated as standalone conclusions, and Capital Lab's outputs are hypothetical scenario mathematics, not investment recommendations.

EQUICAFI is intended for **education, research, and software demonstration**.

---

## Project Philosophy

> Good analysis is not just about finding numbers. It is about understanding the relationships between them.

- **Structure** — organize complex information into a coherent research workflow
- **Explanation** — make important metrics easier to understand
- **Context** — interpret figures alongside related signals
- **Transparency** — make assumptions and limitations visible
- **Education** — help users learn while they research

---

## Project Status

EQUICAFI currently includes an equity analysis engine, market-data provider integration, fundamental analysis, historical analysis, valuation analysis, technical indicators, risk analysis, cross-metric reasoning, a hypothetical Capital Lab, a Streamlit research dashboard, SQLite persistence, and automated testing.

## License

MIT License
