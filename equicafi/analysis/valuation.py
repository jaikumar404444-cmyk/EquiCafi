from __future__ import annotations

import pandas as pd

from .common import average, metric, pct, safe_div, series_for, sorted_periods


def compute_valuation(
    annual_financials: pd.DataFrame,
    balance_sheet: pd.DataFrame,
    cashflow: pd.DataFrame,
    price: float | None,
    shares_outstanding: float | None = None,
    dividends: pd.DataFrame | None = None,
) -> tuple[list, dict[str, dict[str, float]]]:
    revenue_s = series_for(annual_financials, ["total revenue", "operating revenue", "revenue"])
    net_s = series_for(annual_financials, ["net income", "net income common stockholders", "net income applicable to common shares"])
    ebitda_s = series_for(annual_financials, ["ebitda"])
    eps_s = series_for(annual_financials, ["diluted eps", "basic eps"])
    shares_s = series_for(annual_financials, ["diluted average shares", "basic average shares"])
    fcf_s = _fcf_series(cashflow)
    equity_s = series_for(balance_sheet, ["stockholders equity", "stockholders' equity", "common stock equity", "total equity gross minority interest"])
    debt_s = series_for(balance_sheet, ["total debt", "long term debt and capital lease obligation", "long term debt"])
    cash_s = series_for(balance_sheet, ["cash and cash equivalents", "cash cash equivalents and short term investments", "cash"])

    periods = sorted_periods(annual_financials)
    latest = periods[0] if periods else None
    previous = periods[1] if len(periods) > 1 else None

    net = _get(net_s, latest)
    equity = _get(equity_s, latest)
    debt = _get(debt_s, latest)
    cash = _get(cash_s, latest)
    revenue = _get(revenue_s, latest)
    ebitda = _get(ebitda_s, latest)
    fcf = _get(fcf_s, latest)
    eps = _get(eps_s, latest)
    inferred_shares = None
    if eps is None and shares_outstanding:
        eps = safe_div(net, shares_outstanding)
    if eps is None:
        avg_shares = _get(shares_s, latest)
        eps = safe_div(net, avg_shares)
    if eps is not None and net is not None:
        inferred_shares = safe_div(net, eps)

    effective_shares = shares_outstanding or inferred_shares
    market_cap = price * effective_shares if price is not None and effective_shares else None
    net_debt = debt - cash if debt is not None and cash is not None else None
    enterprise_value = market_cap + net_debt if market_cap is not None and net_debt is not None else None

    book_value_per_share = safe_div(equity, effective_shares) if equity is not None and effective_shares else None

    pe = safe_div(price, eps)
    pb = safe_div(price, book_value_per_share)
    ps = safe_div(market_cap, revenue)
    ev_ebitda = safe_div(enterprise_value, ebitda)
    ev_sales = safe_div(enterprise_value, revenue)
    earnings_yield = pct(eps, price)
    fcf_yield = pct(fcf, market_cap)

    dividend_yield = _latest_dividend_yield(dividends, price)

    metrics = [
        metric("P/E", pe, "x", f"P/E is {pe:.2f}x based on the latest available EPS." if pe is not None else None),
        metric("P/B", pb, "x", f"P/B is {pb:.2f}x based on book value." if pb is not None else None),
        metric("P/S", ps, "x", f"P/S is {ps:.2f}x based on market capitalization and revenue." if ps is not None else None),
        metric("EV/EBITDA", ev_ebitda, "x", f"EV/EBITDA is {ev_ebitda:.2f}x." if ev_ebitda is not None else None),
        metric("EV/Sales", ev_sales, "x", f"EV/Sales is {ev_sales:.2f}x." if ev_sales is not None else None),
        metric("Earnings Yield", earnings_yield, "%", f"Earnings yield is {earnings_yield:.2f}%." if earnings_yield is not None else None),
        metric("FCF Yield", fcf_yield, "%", f"FCF yield is {fcf_yield:.2f}%." if fcf_yield is not None else None),
        metric("Dividend Yield", dividend_yield, "%", f"Dividend yield is {dividend_yield:.2f}%." if dividend_yield is not None else None),
    ]

    history: dict[str, dict[str, float]] = {}
    for period in periods:
        period_net = _get(net_s, period)
        period_rev = _get(revenue_s, period)
        period_ebitda = _get(ebitda_s, period)
        period_fcf = _get(fcf_s, period)
        period_equity = _get(equity_s, period)
        period_eps = _get(eps_s, period)
        if period_eps is None:
            period_eps = safe_div(period_net, _get(shares_s, period))
        # Use year/period-end market price if available later via add_price_history.
        history[str(period)] = {
            k: v for k, v in {
                "EPS": period_eps,
                "Revenue": period_rev,
                "Net Profit": period_net,
                "EBITDA": period_ebitda,
                "FCF": period_fcf,
                "Equity": period_equity,
            }.items() if v is not None
        }

    return metrics, history


def add_historical_valuation(
    valuation_history: dict[str, dict[str, float]],
    price_history: pd.DataFrame,
) -> dict[str, dict[str, float]]:
    if not valuation_history or price_history is None or price_history.empty or "Close" not in price_history.columns:
        return valuation_history

    prices = price_history.copy()
    prices.index = pd.to_datetime(prices.index, errors="coerce")
    prices = prices.dropna(subset=["Close"])
    if prices.empty:
        return valuation_history

    year_end_prices = prices.groupby(prices.index.year)["Close"].last()

    for period, values in valuation_history.items():
        year = pd.to_datetime(period, errors="coerce")
        if pd.isna(year):
            try:
                year = pd.Timestamp(f"{period}-12-31")
            except Exception:
                continue
        y = int(year.year)
        price_value = year_end_prices.get(y)
        eps = values.get("EPS")
        if price_value is None:
            continue
        if eps not in (None, 0):
            values["P/E"] = float(price_value / eps)
            values["Earnings Yield"] = float((eps / price_value) * 100)
    return valuation_history


def _fcf_series(cashflow: pd.DataFrame) -> pd.Series | None:
    from .common import series_for
    ocf = series_for(cashflow, ["operating cash flow", "total cash from operating activities", "cash flow from continuing operating activities"])
    capex = series_for(cashflow, ["capital expenditure", "capital expenditures", "investments in property plant and equipment"])
    if ocf is None or capex is None:
        return None
    aligned = pd.concat([ocf.rename("ocf"), capex.rename("capex")], axis=1)
    return aligned["ocf"] - aligned["capex"].abs()


def _get(series: pd.Series | None, period) -> float | None:
    if series is None or period is None:
        return None
    for idx in series.index:
        if str(idx) == str(period):
            v = series.loc[idx]
            return float(v) if pd.notna(v) else None
    try:
        target = pd.to_datetime(period)
        for idx in series.index:
            if pd.to_datetime(idx, errors="coerce") == target:
                v = series.loc[idx]
                return float(v) if pd.notna(v) else None
    except Exception:
        pass
    return None


def _latest_dividend_yield(dividends: pd.DataFrame | None, price: float | None) -> float | None:
    if dividends is None or dividends.empty or price in (None, 0) or "Dividends" not in dividends.columns:
        return None
    s = pd.to_numeric(dividends["Dividends"], errors="coerce").dropna()
    if s.empty:
        return None
    idx = pd.to_datetime(s.index, errors="coerce")
    s.index = idx
    latest = s.index.max()
    if pd.isna(latest):
        return None
    start = latest - pd.DateOffset(years=1)
    trailing = float(s[(s.index > start) & (s.index <= latest)].sum())
    if trailing == 0:
        return 0.0
    return float(trailing / price * 100)
