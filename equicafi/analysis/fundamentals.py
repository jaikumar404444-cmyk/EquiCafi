from __future__ import annotations

from typing import Any

import pandas as pd

from .common import average, latest_pair, metric, pct, safe_div, series_for, sorted_periods


def compute_fundamentals(
    annual_financials: pd.DataFrame,
    balance_sheet: pd.DataFrame,
    cashflow: pd.DataFrame,
    dividends: pd.DataFrame | None = None,
) -> tuple[list, dict[str, dict[str, float]]]:
    periods = sorted_periods(annual_financials)
    history: dict[str, dict[str, float]] = {}

    revenue_s = series_for(annual_financials, ["total revenue", "operating revenue", "revenue"])
    gross_s = series_for(annual_financials, ["gross profit"])
    op_s = series_for(annual_financials, ["operating income", "operating profit", "ebit"])
    net_s = series_for(annual_financials, ["net income", "net income common stockholders", "net income applicable to common shares"])
    ebitda_s = series_for(annual_financials, ["ebitda"])
    eps_s = series_for(annual_financials, ["diluted eps", "basic eps"])
    shares_s = series_for(annual_financials, ["diluted average shares", "basic average shares"])

    assets_s = series_for(balance_sheet, ["total assets"])
    equity_s = series_for(balance_sheet, ["stockholders equity", "stockholders' equity", "common stock equity", "total equity gross minority interest"])
    debt_s = series_for(balance_sheet, ["total debt", "long term debt and capital lease obligation", "long term debt"])
    cash_s = series_for(balance_sheet, ["cash and cash equivalents", "cash cash equivalents and short term investments", "cash"])
    ca_s = series_for(balance_sheet, ["current assets"])
    cl_s = series_for(balance_sheet, ["current liabilities"])
    inventory_s = series_for(balance_sheet, ["inventory"])

    ocf_s = series_for(cashflow, ["operating cash flow", "total cash from operating activities", "cash flow from continuing operating activities"])
    capex_s = series_for(cashflow, ["capital expenditure", "capital expenditures", "investments in property plant and equipment"])
    interest_s = series_for(annual_financials, ["interest expense", "interest expense non operating", "interest expense non-operating"])

    all_periods = periods
    if not all_periods:
        all_periods = sorted_periods(balance_sheet)

    # Normalize newest-to-oldest for consistent historical maps.
    for period in all_periods:
        value = {
            "Revenue": _get(revenue_s, period),
            "Gross Profit": _get(gross_s, period),
            "Operating Profit": _get(op_s, period),
            "Net Profit": _get(net_s, period),
            "Operating Cash Flow": _get(ocf_s, period),
            "Capital Expenditure": abs(_get(capex_s, period) or 0.0) if _get(capex_s, period) is not None else None,
            "Free Cash Flow": _fcf_at(ocf_s, capex_s, period),
            "Total Assets": _get(assets_s, period),
            "Equity": _get(equity_s, period),
            "Debt": _get(debt_s, period),
            "Cash": _get(cash_s, period),
            "Current Assets": _get(ca_s, period),
            "Current Liabilities": _get(cl_s, period),
            "Inventory": _get(inventory_s, period),
            "Interest Expense": abs(_get(interest_s, period) or 0.0) if _get(interest_s, period) is not None else None,
            "EBITDA": _get(ebitda_s, period),
        }
        ep = _get(eps_s, period)
        if ep is None:
            ni = value["Net Profit"]
            sh = _get(shares_s, period)
            ep = safe_div(ni, sh)
        value["EPS"] = ep
        history[str(period)] = {k: float(v) for k, v in value.items() if v is not None}

    latest = all_periods[0] if all_periods else None
    previous = all_periods[1] if len(all_periods) > 1 else None

    def val(series: pd.Series | None) -> float | None:
        return _get(series, latest)

    def prev(series: pd.Series | None) -> float | None:
        return _get(series, previous)

    revenue = val(revenue_s)
    revenue_prev = prev(revenue_s)
    gross = val(gross_s)
    op = val(op_s)
    net = val(net_s)
    ocf = val(ocf_s)
    capex = val(capex_s)
    fcf = _fcf_at(ocf_s, capex_s, latest)
    assets = val(assets_s)
    equity = val(equity_s)
    debt = val(debt_s)
    cash = val(cash_s)
    ca = val(ca_s)
    cl = val(cl_s)
    inventory = val(inventory_s)
    interest = abs(val(interest_s)) if val(interest_s) is not None else None
    ebitda = val(ebitda_s)
    eps = val(eps_s)
    if eps is None:
        eps = safe_div(net, val(shares_s))
    eps_prev = prev(eps_s)

    revenue_growth = pct(revenue - revenue_prev if revenue is not None and revenue_prev is not None else None, revenue_prev)
    gross_margin = pct(gross, revenue)
    op_margin = pct(op, revenue)
    net_margin = pct(net, revenue)
    roe = pct(net, average(val(net_s), None) if False else average(equity, prev(equity_s)))
    roa = pct(net, average(assets, prev(assets_s)))
    roce = pct(op, _capital_employed(equity, debt, cash, prev(equity_s), prev(debt_s), prev(cash_s)))
    eps_growth = pct(eps - eps_prev if eps is not None and eps_prev not in (None, 0) else None, eps_prev)
    ocf_to_net = safe_div(ocf, net)
    fcf_to_net = pct(fcf, net)
    net_debt = (debt - cash) if debt is not None and cash is not None else None
    debt_equity = safe_div(debt, equity)
    interest_coverage = safe_div(op, interest)
    net_debt_ocf = safe_div(net_debt, ocf)
    fcf_debt = pct(fcf, debt)
    cash_debt = safe_div(cash, debt)
    liquidity = safe_div(ca, cl)
    quick = safe_div((ca - inventory) if ca is not None and inventory is not None else None, cl)

    observation = {
        "revenue_growth": _growth_sentence(revenue_growth),
        "gross_margin": f"Gross margin is {gross_margin:.1f}%" if gross_margin is not None else None,
        "operating_margin": f"Operating margin is {op_margin:.1f}%" if op_margin is not None else None,
        "net_margin": f"Net margin is {net_margin:.1f}%" if net_margin is not None else None,
        "roe": f"ROE is {roe:.1f}%" if roe is not None else None,
        "roce": f"ROCE is {roce:.1f}%" if roce is not None else None,
        "fcf": f"Free cash flow is {fcf:.2f}" if fcf is not None else None,
    }

    metrics = [
        metric("Revenue", revenue, "currency", observation.get("revenue_growth")),
        metric("Revenue Growth", revenue_growth, "%", observation.get("revenue_growth")),
        metric("Gross Profit", gross, "currency", observation.get("gross_margin")),
        metric("Gross Margin", gross_margin, "%", observation.get("gross_margin")),
        metric("Operating Profit", op, "currency", observation.get("operating_margin")),
        metric("Operating Margin", op_margin, "%", observation.get("operating_margin")),
        metric("Net Profit", net, "currency", observation.get("net_margin")),
        metric("Net Margin", net_margin, "%", observation.get("net_margin")),
        metric("EPS", eps, "currency/share", f"EPS is {eps:.2f}" if eps is not None else None),
        metric("EPS Growth", eps_growth, "%", f"EPS growth is {eps_growth:.1f}%" if eps_growth is not None else None),
        metric("ROE", roe, "%", observation.get("roe")),
        metric("ROA", roa, "%", f"ROA is {roa:.1f}%" if roa is not None else None),
        metric("ROCE", roce, "%", observation.get("roce")),
        metric("Operating Cash Flow", ocf, "currency", f"Operating cash flow is {ocf:.2f}" if ocf is not None else None),
        metric("Capital Expenditure", capex, "currency", f"Capital expenditure is {capex:.2f}" if capex is not None else None),
        metric("Free Cash Flow", fcf, "currency", observation.get("fcf")),
        metric("FCF / Net Income", fcf_to_net, "%", f"Free cash flow is {fcf_to_net:.1f}% of net income." if fcf_to_net is not None else None),
        metric("Operating Cash Flow / Net Income", ocf_to_net, "x", f"Operating cash flow is {ocf_to_net:.2f} times net income." if ocf_to_net is not None else None),
        metric("Debt / Equity", debt_equity, "x", f"Debt-to-equity is {debt_equity:.2f}x." if debt_equity is not None else None),
        metric("Interest Coverage", interest_coverage, "x", f"Operating profit covers interest expense {interest_coverage:.2f} times." if interest_coverage is not None else None),
        metric("Net Debt / Operating Cash Flow", net_debt_ocf, "x", f"Net debt is {net_debt_ocf:.2f} times operating cash flow." if net_debt_ocf is not None else None),
        metric("FCF / Debt", fcf_debt, "%", f"Free cash flow is {fcf_debt:.1f}% of debt." if fcf_debt is not None else None),
        metric("Cash / Debt", cash_debt, "x", f"Cash is {cash_debt:.2f} times debt." if cash_debt is not None else None),
        metric("Liquidity Coverage", liquidity, "x", f"Current assets cover current liabilities by {liquidity:.2f}x." if liquidity is not None else None),
        metric("Quick Liquidity Coverage", quick, "x", f"Quick assets cover current liabilities by {quick:.2f}x." if quick is not None else None),
    ]

    # Add dividend yield input only when source has dividend records; actual yield is calculated later after price is known.
    return metrics, history


def _get(series: pd.Series | None, period: Any) -> float | None:
    if series is None or period is None:
        return None
    # Match exact string first, then timestamp-like labels.
    for idx in series.index:
        if str(idx) == str(period):
            value = series.loc[idx]
            return float(value) if pd.notna(value) else None
    try:
        target = pd.to_datetime(period)
        for idx in series.index:
            if pd.to_datetime(idx, errors="coerce") == target:
                value = series.loc[idx]
                return float(value) if pd.notna(value) else None
    except Exception:
        pass
    return None


def _fcf_at(ocf_s: pd.Series | None, capex_s: pd.Series | None, period: Any) -> float | None:
    ocf = _get(ocf_s, period)
    capex = _get(capex_s, period)
    if ocf is None or capex is None:
        return None
    return ocf - abs(capex)


def _capital_employed(equity, debt, cash, prev_equity, prev_debt, prev_cash):
    current = None if equity is None or debt is None or cash is None else equity + debt - cash
    previous = None if prev_equity is None or prev_debt is None or prev_cash is None else prev_equity + prev_debt - prev_cash
    return average(current, previous)


def _growth_sentence(value: float | None) -> str | None:
    return f"Revenue growth is {value:.1f}%" if value is not None else None
