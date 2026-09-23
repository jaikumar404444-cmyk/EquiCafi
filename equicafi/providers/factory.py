from __future__ import annotations

from .demo import DemoProvider
from .yahoo import YahooFinanceProvider


def provider_for(ticker: str):
    normalized = ticker.strip().upper()
    return DemoProvider() if normalized == "DEMO" else YahooFinanceProvider()
