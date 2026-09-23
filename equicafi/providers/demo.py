from __future__ import annotations

import numpy as np
import pandas as pd

from .base import ProviderData
from .utils import normalize_ticker


class DemoProvider:
    """Deterministic synthetic company for development and demos."""

    def fetch(self, ticker: str = "DEMO") -> ProviderData:
        ticker = normalize_ticker(ticker)
        if ticker != "DEMO":
            raise ValueError("DemoProvider only supports the DEMO ticker.")

        years = [2021, 2022, 2023, 2024, 2025]
        revenue = [1200.0, 1320.0, 1450.0, 1540.0, 1720.0]
        gross = [696.0, 752.4, 841.0, 940.4, 1066.4]
        operating = [240.0, 263.0, 290.0, 332.0, 392.16]
        net = [175.0, 192.0, 215.0, 251.0, 297.56]
        ocf = [215.0, 228.0, 252.0, 306.0, 342.19]
        capex = [58.0, 61.0, 66.0, 70.0, 100.0]
        assets = [1180.0, 1260.0, 1360.0, 1450.0, 1600.0]
        equity = [640.0, 680.0, 745.0, 850.0, 980.0]
        debt = [190.0, 188.0, 205.0, 210.0, 275.0]
        cash = [145.0, 168.0, 190.0, 240.0, 168.0]
        current_assets = [420.0, 465.0, 510.0, 560.0, 610.0]
        current_liabilities = [315.0, 332.0, 350.0, 420.0, 555.0]
        inventory = [100.0, 108.0, 120.0, 140.0, 175.0]
        interest = [16.0, 17.0, 18.0, 21.0, 29.0]
        shares = [10.0, 10.0, 10.0, 10.0, 10.8]
        dividends = [3.0, 3.2, 3.5, 4.0, 4.5]
        ebitda = [290.0, 314.0, 345.0, 390.0, 450.0]

        financial = pd.DataFrame(
            {
                str(y): [
                    revenue[i], gross[i], operating[i], net[i], ocf[i], capex[i],
                    assets[i], equity[i], debt[i], cash[i], current_assets[i],
                    current_liabilities[i], inventory[i], interest[i], shares[i],
                    dividends[i], ebitda[i],
                ]
                for i, y in enumerate(years)
            },
            index=[
                "Total Revenue", "Gross Profit", "Operating Income", "Net Income",
                "Operating Cash Flow", "Capital Expenditure", "Total Assets",
                "Stockholders Equity", "Total Debt", "Cash And Cash Equivalents",
                "Current Assets", "Current Liabilities", "Inventory",
                "Interest Expense", "Diluted Average Shares", "Dividend Per Share",
                "EBITDA",
            ],
        )

        prices = []
        idx = pd.bdate_range("2021-01-01", "2025-12-31")
        rng = np.random.default_rng(42)
        daily = rng.normal(0.00045, 0.014, len(idx))
        # Smooth upward drift, plus deterministic mild cycles.
        values = 90.0 * np.exp(np.cumsum(daily))
        values *= 1 + 0.025 * np.sin(np.arange(len(idx)) / 60.0)
        prices = pd.Series(values, index=idx, name="Close")
        price_frame = pd.DataFrame({"Close": prices})

        annual_prices = price_frame.groupby(price_frame.index.year)["Close"].last()
        # Keep demo valuation internally sensible by shaping year-end prices.
        target_prices = pd.Series({2021: 720, 2022: 790, 2023: 860, 2024: 1020, 2025: 1250}, dtype=float)
        scale = target_prices.reindex(annual_prices.index).divide(annual_prices)
        price_frame["Close"] = price_frame["Close"] * price_frame.index.year.map(scale).to_numpy()

        dividends_frame = pd.DataFrame(
            {"Dividends": np.repeat(np.array(dividends), 4)},
            index=pd.date_range("2021-03-31", periods=20, freq="QE"),
        )

        return ProviderData(
            ticker="DEMO",
            company_name="EQUICAFI Demonstration Holdings",
            exchange="DEMO",
            sector="Synthetic",
            industry="Demonstration",
            currency="INR",
            website=None,
            current_price=float(price_frame["Close"].iloc[-1]),
            annual_financials=financial,
            balance_sheet=financial.loc[
                [
                    "Total Assets", "Stockholders Equity", "Total Debt",
                    "Cash And Cash Equivalents", "Current Assets",
                    "Current Liabilities", "Inventory",
                ]
            ],
            cashflow=financial.loc[
                ["Operating Cash Flow", "Capital Expenditure", "Net Income"]
            ],
            price_history=price_frame,
            dividends=dividends_frame,
            source="demo",
            synthetic=True,
        )
