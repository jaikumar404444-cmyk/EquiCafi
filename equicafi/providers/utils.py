from __future__ import annotations

from typing import Any

import pandas as pd


def normalize_ticker(ticker: str) -> str:
    value = ticker.strip().upper()
    if not value:
        raise ValueError("Ticker cannot be empty.")
    return value


def clean_frame(frame: Any) -> pd.DataFrame:
    if frame is None:
        return pd.DataFrame()
    if not isinstance(frame, pd.DataFrame):
        try:
            frame = pd.DataFrame(frame)
        except Exception:
            return pd.DataFrame()
    result = frame.copy()
    if isinstance(result.columns, pd.MultiIndex):
        result.columns = [c[-1] if isinstance(c, tuple) else c for c in result.columns]
    result.index = [str(x) for x in result.index]
    return result


def first_available(frame: pd.DataFrame, aliases: list[str]) -> pd.Series | None:
    if frame.empty:
        return None
    normalized = {str(a).strip().lower(): a for a in aliases}
    for idx in frame.index:
        key = str(idx).strip().lower()
        if key in normalized:
            series = frame.loc[idx]
            if isinstance(series, pd.DataFrame):
                series = series.iloc[0]
            return pd.to_numeric(series, errors="coerce")
    # substring fallback
    for idx in frame.index:
        text = str(idx).strip().lower()
        if any(alias.lower() in text for alias in aliases):
            series = frame.loc[idx]
            if isinstance(series, pd.DataFrame):
                series = series.iloc[0]
            return pd.to_numeric(series, errors="coerce")
    return None


def latest_numeric(series: pd.Series | None) -> float | None:
    if series is None or series.empty:
        return None
    values = pd.to_numeric(series, errors="coerce").dropna()
    if values.empty:
        return None
    return float(values.iloc[0])


def safe_float(value: Any) -> float | None:
    try:
        if pd.isna(value):
            return None
        return float(value)
    except Exception:
        return None
