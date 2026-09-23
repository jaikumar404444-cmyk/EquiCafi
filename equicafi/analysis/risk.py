from __future__ import annotations

import numpy as np
import pandas as pd

from .common import metric, pct, safe_div, series_for


def compute_risk(
    price_history: pd.DataFrame,
    annual_financials: pd.DataFrame,
    balance_sheet: pd.DataFrame,
    cashflow: pd.DataFrame,
) -> list:
    price_metrics = _price_risk(price_history)

    debt = _latest(balance_sheet, ["total debt", "long term debt and capital lease obligation", "long term debt"])
    equity = _latest(balance_sheet, ["stockholders equity", "stockholders' equity", "common stock equity", "total equity gross minority interest"])
    cash = _latest(balance_sheet, ["cash and cash equivalents", "cash cash equivalents and short term investments", "cash"])
    net_debt = debt - cash if debt is not None and cash is not None else None
    ocf = _latest(cashflow, ["operating cash flow", "total cash from operating activities", "cash flow from continuing operating activities"])
    capex = _latest(cashflow, ["capital expenditure", "capital expenditures", "investments in property plant and equipment"])
    fcf = ocf - abs(capex) if ocf is not None and capex is not None else None
    operating_profit = _latest(annual_financials, ["operating income", "operating profit", "ebit"])
    interest = _latest(annual_financials, ["interest expense", "interest expense non operating", "interest expense non-operating"])
    net = _latest(annual_financials, ["net income", "net income common stockholders", "net income applicable to common shares"])
    current_assets = _latest(balance_sheet, ["current assets"])
    current_liabilities = _latest(balance_sheet, ["current liabilities"])
    inventory = _latest(balance_sheet, ["inventory"])

    debt_equity = safe_div(debt, equity)
    interest_coverage = safe_div(operating_profit, abs(interest) if interest is not None else None)
    net_debt_ocf = safe_div(net_debt, ocf)
    fcf_debt = pct(fcf, debt)
    cash_debt = safe_div(cash, debt)
    liquidity = safe_div(current_assets, current_liabilities)
    quick = safe_div((current_assets - inventory) if current_assets is not None and inventory is not None else None, current_liabilities)
    ocf_net = safe_div(ocf, net)
    fcf_net = pct(fcf, net)

    financial_metrics = [
        metric("Debt / Equity", debt_equity, "x", f"Debt-to-equity is {debt_equity:.2f}x." if debt_equity is not None else None),
        metric("Interest Coverage", interest_coverage, "x", f"Operating earnings cover interest expense {interest_coverage:.2f} times." if interest_coverage is not None else None),
        metric("Net Debt / Operating Cash Flow", net_debt_ocf, "x", f"Net debt is {net_debt_ocf:.2f} times operating cash flow." if net_debt_ocf is not None else None),
        metric("FCF / Debt", fcf_debt, "%", f"Free cash flow equals {fcf_debt:.2f}% of debt." if fcf_debt is not None else None),
        metric("Cash / Debt", cash_debt, "x", f"Cash is {cash_debt:.2f} times debt." if cash_debt is not None else None),
        metric("Operating Cash Flow / Net Income", ocf_net, "x", f"Operating cash flow is {ocf_net:.2f} times net income." if ocf_net is not None else None),
        metric("FCF / Net Income", fcf_net, "%", f"Free cash flow is {fcf_net:.2f}% of net income." if fcf_net is not None else None),
        metric("Liquidity Coverage", liquidity, "x", f"Current assets cover current liabilities by {liquidity:.2f}x." if liquidity is not None else None),
        metric("Quick Liquidity Coverage", quick, "x", f"Quick assets cover current liabilities by {quick:.2f}x." if quick is not None else None),
    ]
    return price_metrics + financial_metrics


def _price_risk(price_history: pd.DataFrame) -> list:
    if price_history is None or price_history.empty or "Close" not in price_history.columns:
        names = ["Maximum Drawdown", "Annualized Volatility", "Downside Volatility", "Worst Daily Return", "Positive Session Rate"]
        return [metric(n, None, "%") for n in names]
    close = pd.to_numeric(price_history["Close"], errors="coerce").dropna()
    returns = close.pct_change().dropna()
    if returns.empty:
        return [metric(n, None, "%") for n in ["Maximum Drawdown", "Annualized Volatility", "Downside Volatility", "Worst Daily Return", "Positive Session Rate"]]
    running_peak = close.cummax()
    drawdown = close / running_peak - 1
    max_dd = float(drawdown.min() * 100)
    vol = float(returns.std(ddof=1) * np.sqrt(252) * 100) if len(returns) > 1 else None
    downside = returns[returns < 0]
    downside_vol = float(downside.std(ddof=1) * np.sqrt(252) * 100) if len(downside) > 1 else None
    worst = float(returns.min() * 100)
    positive_rate = float((returns > 0).mean() * 100)
    return [
        metric("Maximum Drawdown", max_dd, "%", f"The largest peak-to-trough decline in the observed sample was {max_dd:.1f}% ."),
        metric("Annualized Volatility", vol, "%", f"Annualized volatility is {vol:.1f}% based on observed daily returns." if vol is not None else None),
        metric("Downside Volatility", downside_vol, "%", f"Downside volatility is {downside_vol:.1f}% based on negative sessions." if downside_vol is not None else None),
        metric("Worst Daily Return", worst, "%", f"The worst observed daily return was {worst:.1f}%."),
        metric("Positive Session Rate", positive_rate, "%", f"{positive_rate:.1f}% of observed sessions had a positive close-to-close return."),
    ]


def _latest(frame: pd.DataFrame, aliases: list[str]) -> float | None:
    s = series_for(frame, aliases)
    if s is None or s.dropna().empty:
        return None
    return float(s.dropna().iloc[0])
