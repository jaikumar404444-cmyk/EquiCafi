from __future__ import annotations

from datetime import date, datetime, timezone

import pandas as pd

from equicafi.analysis import (
    add_historical_valuation,
    build_reasoning,
    compute_fundamentals,
    compute_risk,
    compute_technical,
    compute_valuation,
    historical_reasoning,
)
from equicafi.models import AnalysisResult, CompanyProfile, DataQuality, Metric, PriceSeries
from equicafi.providers import provider_for


class AnalysisService:
    """Orchestrates provider retrieval and all analytical modules."""

    def analyze(self, ticker: str) -> AnalysisResult:
        provider = provider_for(ticker)
        data = provider.fetch(ticker)

        profile = CompanyProfile(
            ticker=data.ticker,
            name=data.company_name or data.ticker,
            exchange=data.exchange,
            sector=data.sector,
            industry=data.industry,
            currency=data.currency,
            website=data.website,
        )
        quality = self._quality(data)

        current_price = self._price_metric(data.current_price, data.currency)
        fundamentals, history = compute_fundamentals(
            data.annual_financials,
            data.balance_sheet,
            data.cashflow,
            data.dividends,
        )

        shares_outstanding = self._shares_from_fast_data(data.current_price, data.annual_financials)
        valuation, valuation_history = compute_valuation(
            data.annual_financials,
            data.balance_sheet,
            data.cashflow,
            data.current_price,
            shares_outstanding=shares_outstanding,
            dividends=data.dividends,
        )
        valuation_history = add_historical_valuation(valuation_history, data.price_history)

        technicals = compute_technical(data.price_history)
        risk = compute_risk(
            data.price_history,
            data.annual_financials,
            data.balance_sheet,
            data.cashflow,
        )

        observations = build_reasoning([*fundamentals, *valuation, *technicals, *risk])
        historical_obs = historical_reasoning(_augment_history(history))

        limitations = list(quality.notes)
        if data.ticker == "DEMO":
            limitations.append("DEMO metrics are synthetic and are provided only to demonstrate the analysis workflow.")
        limitations.append("Provider financial statements may use different line-item conventions across companies.")
        limitations.append("Historical and valuation ratios describe supplied data; they are not forecasts or personalized investment advice.")

        price_history = self._price_model(data.price_history)

        return AnalysisResult(
            company=profile,
            data_quality=quality,
            current_price=current_price,
            fundamentals=fundamentals,
            valuation=valuation,
            technicals=technicals,
            risk=risk,
            observations=observations,
            historical_observations=historical_obs,
            history=_clean_history(history),
            valuation_history=_clean_history(valuation_history),
            price_history=price_history,
            limitations=limitations,
            generated_at=datetime.now(timezone.utc),
        )

    @staticmethod
    def _price_metric(price: float | None, currency: str) -> Metric:
        from equicafi.analysis.common import metric
        return metric(
            "Current Price",
            price,
            currency,
            f"Latest available price is {price:.2f} {currency}." if price is not None else None,
        )

    @staticmethod
    def _quality(data) -> DataQuality:
        notes = []
        if data.synthetic:
            return DataQuality(
                source=data.source,
                status="synthetic demo data",
                quality="high",
                notes=["Synthetic demonstration dataset; not live market data."],
            )
        if data.company_name == data.ticker:
            notes.append("Company profile name was unavailable; the ticker is used as a safe fallback.")
        if data.annual_financials.empty:
            notes.append("Annual financial statements are unavailable.")
        if data.balance_sheet.empty:
            notes.append("Balance-sheet data is unavailable.")
        if data.cashflow.empty:
            notes.append("Cash-flow data is unavailable.")
        if data.price_history.empty:
            notes.append("Historical market-price data is unavailable.")
        missing_sets = sum(bool(x) for x in [data.annual_financials.empty, data.balance_sheet.empty, data.cashflow.empty, data.price_history.empty])
        quality = "high" if missing_sets == 0 else "medium" if missing_sets <= 2 else "low"
        return DataQuality(source=data.source, status="provider data", quality=quality, notes=notes)

    @staticmethod
    def _shares_from_fast_data(price: float | None, financials: pd.DataFrame) -> float | None:
        # We deliberately derive shares from latest net income / EPS when both are available,
        # avoiding a second network request solely for shares outstanding.
        if financials.empty:
            return None
        from equicafi.analysis.common import series_for
        net = series_for(financials, ["net income", "net income common stockholders", "net income applicable to common shares"])
        eps = series_for(financials, ["diluted eps", "basic eps"])
        if net is None or eps is None:
            return None
        try:
            n = float(net.dropna().iloc[0])
            e = float(eps.dropna().iloc[0])
            if e == 0:
                return None
            return abs(n / e)
        except Exception:
            return None

    @staticmethod
    def _price_model(frame: pd.DataFrame) -> PriceSeries | None:
        if frame is None or frame.empty or "Close" not in frame.columns:
            return None
        close = pd.to_numeric(frame["Close"], errors="coerce").dropna()
        if close.empty:
            return None
        dates = []
        for idx in close.index:
            try:
                if hasattr(idx, "date"):
                    dates.append(idx.date())
                else:
                    dates.append(str(idx))
            except Exception:
                dates.append(str(idx))
        return PriceSeries(dates=dates, close=[float(v) for v in close.tolist()])


def _augment_history(history: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    out = {}
    for period, values in history.items():
        v = dict(values)
        revenue = v.get("Revenue")
        gross = v.get("Gross Profit")
        op = v.get("Operating Profit")
        net = v.get("Net Profit")
        assets = v.get("Total Assets")
        equity = v.get("Equity")
        debt = v.get("Debt")
        cash = v.get("Cash")
        if revenue:
            if gross is not None:
                v["Gross Margin"] = gross / revenue * 100
            if op is not None:
                v["Operating Margin"] = op / revenue * 100
            if net is not None:
                v["Net Margin"] = net / revenue * 100
        if net is not None and equity:
            v["ROE"] = net / equity * 100
        if net is not None and assets:
            v["ROA"] = net / assets * 100
        if op is not None and equity is not None and debt is not None and cash is not None:
            capital = equity + debt - cash
            if capital:
                v["ROCE"] = op / capital * 100
        out[period] = v
    return out


def _clean_history(history: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    return {
        str(k): {str(metric): float(value) for metric, value in values.items() if value is not None}
        for k, values in history.items()
    }
