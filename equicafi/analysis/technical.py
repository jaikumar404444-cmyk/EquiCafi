from __future__ import annotations

import numpy as np
import pandas as pd

from .common import metric, pct


def compute_technical(price_history: pd.DataFrame) -> list:
    if price_history is None or price_history.empty or "Close" not in price_history.columns:
        return [
            metric(name, None, unit)
            for name, unit in [
                ("52 Week High", "currency"),
                ("52 Week Low", "currency"),
                ("Distance from 52 Week High", "%"),
                ("Distance from 52 Week Low", "%"),
                ("SMA 20", "currency"),
                ("SMA 50", "currency"),
                ("EMA 20", "currency"),
                ("RSI 14", "index"),
            ]
        ]

    close = pd.to_numeric(price_history["Close"], errors="coerce").dropna()
    if close.empty:
        return [metric(name, None, unit) for name, unit in [
            ("52 Week High", "currency"), ("52 Week Low", "currency"),
            ("Distance from 52 Week High", "%"), ("Distance from 52 Week Low", "%"),
            ("SMA 20", "currency"), ("SMA 50", "currency"), ("EMA 20", "currency"), ("RSI 14", "index")
        ]]

    latest = float(close.iloc[-1])
    trailing = close.iloc[-252:]
    high = float(trailing.max())
    low = float(trailing.min())
    distance_high = pct(latest - high, high)
    distance_low = pct(latest - low, low)
    sma20 = float(close.rolling(20).mean().iloc[-1]) if len(close) >= 20 else None
    sma50 = float(close.rolling(50).mean().iloc[-1]) if len(close) >= 50 else None
    ema20 = float(close.ewm(span=20, adjust=False).mean().iloc[-1]) if len(close) >= 20 else None
    rsi14 = _rsi(close, 14)

    def rel(name: str, value: float | None, unit: str) -> str | None:
        if value is None:
            return None
        return f"{name} is {value:.2f}."

    return [
        metric("52 Week High", high, "currency", f"The trailing 52-week high close is {high:.2f}."),
        metric("52 Week Low", low, "currency", f"The trailing 52-week low close is {low:.2f}."),
        metric("Distance from 52 Week High", distance_high, "%", f"The latest price is {abs(distance_high):.1f}% {'below' if distance_high < 0 else 'above'} the trailing high." if distance_high is not None else None),
        metric("Distance from 52 Week Low", distance_low, "%", f"The latest price is {distance_low:.1f}% above the trailing low." if distance_low is not None else None),
        metric("SMA 20", sma20, "currency", rel("SMA 20", sma20, "currency")),
        metric("SMA 50", sma50, "currency", rel("SMA 50", sma50, "currency")),
        metric("EMA 20", ema20, "currency", rel("EMA 20", ema20, "currency")),
        metric("RSI 14", rsi14, "index", _rsi_observation(rsi14)),
    ]


def _rsi(close: pd.Series, period: int) -> float | None:
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    if avg_loss.iloc[-1] == 0:
        return 100.0 if avg_gain.iloc[-1] > 0 else 50.0
    rs = avg_gain.iloc[-1] / avg_loss.iloc[-1]
    return float(100 - (100 / (1 + rs))) if np.isfinite(rs) else None


def _rsi_observation(value: float | None) -> str | None:
    if value is None:
        return None
    if value < 30:
        band = "weak recent momentum"
    elif value > 70:
        band = "strong recent momentum"
    else:
        band = "mid-range recent momentum"
    return f"RSI 14 is {value:.2f}, describing {band} in the observed price sample." 
