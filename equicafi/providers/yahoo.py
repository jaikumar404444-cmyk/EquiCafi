from __future__ import annotations

import pandas as pd
import yfinance as yf

from .base import ProviderData
from .utils import clean_frame, normalize_ticker, safe_float


class YahooFinanceProvider:
    """Yahoo Finance provider with defensive fallbacks."""

    def fetch(self, ticker: str) -> ProviderData:
        ticker = normalize_ticker(ticker)
        if ticker == "DEMO":
            raise ValueError("Use DemoProvider for DEMO.")

        stock = yf.Ticker(ticker)

        try:
            info = stock.info or {}
        except Exception:
            info = {}

        try:
            fast = dict(stock.fast_info)
        except Exception:
            fast = {}

        name = (
            info.get("longName")
            or info.get("shortName")
            or fast.get("shortName")
            or ticker
        )
        exchange = info.get("exchange") or fast.get("exchange")
        currency = info.get("currency") or fast.get("currency") or "INR"
        sector = info.get("sector")
        industry = info.get("industry")
        website = info.get("website")

        current_price = safe_float(
            fast.get("lastPrice")
            or info.get("currentPrice")
            or info.get("regularMarketPrice")
        )

        try:
            financials = clean_frame(stock.financials)
        except Exception:
            financials = pd.DataFrame()

        try:
            balance_sheet = clean_frame(stock.balance_sheet)
        except Exception:
            balance_sheet = pd.DataFrame()

        try:
            cashflow = clean_frame(stock.cashflow)
        except Exception:
            cashflow = pd.DataFrame()

        try:
            history = stock.history(period="5y", auto_adjust=False)
            history = history[[c for c in ["Close", "Adj Close", "Volume"] if c in history.columns]].copy()
            if "Close" in history.columns:
                history["Close"] = pd.to_numeric(history["Close"], errors="coerce")
            history = history.dropna(how="all")
        except Exception:
            history = pd.DataFrame()

        try:
            dividends = stock.dividends.to_frame("Dividends")
        except Exception:
            dividends = pd.DataFrame()

        if history.empty and current_price is None:
            raise ValueError(f"No usable Yahoo Finance price data was returned for {ticker}.")

        # A failed info endpoint should not kill the analysis when the ticker exists.
        # The profile falls back to the ticker symbol and fast_info values.
        return ProviderData(
            ticker=ticker,
            company_name=str(name),
            exchange=str(exchange) if exchange else None,
            sector=str(sector) if sector else None,
            industry=str(industry) if industry else None,
            currency=str(currency),
            website=str(website) if website else None,
            current_price=current_price,
            annual_financials=financials,
            balance_sheet=balance_sheet,
            cashflow=cashflow,
            price_history=history,
            dividends=dividends,
            source="yahoo_finance",
            synthetic=False,
        )
