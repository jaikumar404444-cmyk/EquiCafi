from unittest.mock import patch

import pandas as pd

from equicafi.providers.yahoo import YahooFinanceProvider


class FakeFastInfo(dict):
    pass


class FakeTicker:
    def __init__(self, ticker):
        self.ticker = ticker
        self.fast_info = FakeFastInfo({
            "currency": "INR",
            "exchange": "NSI",
            "lastPrice": 1234.5,
        })
        self.info = {
            "longName": "Example Industries Limited",
            "exchange": "NSI",
            "currency": "INR",
            "sector": "Industrials",
            "industry": "Example",
        }
        self.financials = pd.DataFrame(
            {"2025": [1000.0, 200.0, 100.0, 50.0, 4.0]},
            index=["Total Revenue", "Operating Income", "Net Income", "Diluted EPS", "EBITDA"],
        )
        self.balance_sheet = pd.DataFrame(
            {"2025": [500.0, 300.0, 100.0, 20.0]},
            index=["Total Assets", "Stockholders Equity", "Total Debt", "Cash And Cash Equivalents"],
        )
        self.cashflow = pd.DataFrame(
            {"2025": [90.0, -20.0]},
            index=["Operating Cash Flow", "Capital Expenditure"],
        )
        self._history = pd.DataFrame(
            {"Close": [100.0, 101.0, 102.0]},
            index=pd.date_range("2025-01-01", periods=3, freq="D"),
        )
        self.dividends = pd.Series([1.0], index=pd.to_datetime(["2025-06-01"]))

    def history(self, **kwargs):
        return self._history


def test_yahoo_provider_uses_safe_profile_fallbacks():
    with patch("yfinance.Ticker", FakeTicker):
        data = YahooFinanceProvider().fetch("EXAMPLE.NS")
    assert data.company_name == "Example Industries Limited"
    assert data.current_price == 1234.5
    assert not data.price_history.empty


def test_yahoo_provider_does_not_require_info_for_identity():
    fake = FakeTicker("EXAMPLE.NS")
    fake.info = {}
    with patch("yfinance.Ticker", lambda ticker: fake):
        data = YahooFinanceProvider().fetch("EXAMPLE.NS")
    assert data.company_name == "EXAMPLE.NS"
