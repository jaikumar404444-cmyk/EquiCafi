from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Protocol

import pandas as pd


@dataclass
class ProviderData:
    ticker: str
    company_name: str
    exchange: str | None
    sector: str | None
    industry: str | None
    currency: str
    website: str | None
    current_price: float | None
    annual_financials: pd.DataFrame
    balance_sheet: pd.DataFrame
    cashflow: pd.DataFrame
    price_history: pd.DataFrame
    dividends: pd.DataFrame | None = None
    source: str = "unknown"
    synthetic: bool = False
    fetched_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class DataProvider(Protocol):
    def fetch(self, ticker: str) -> ProviderData:
        ...
