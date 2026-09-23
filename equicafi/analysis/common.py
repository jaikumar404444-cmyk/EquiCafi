from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd

from .definitions import metric_template
from equicafi.models import Metric


def metric(
    name: str,
    value: float | None,
    unit: str,
    observation: str | None = None,
) -> Metric:
    d = metric_template(name)
    return Metric(
        name=name,
        value=None if value is None or not np.isfinite(value) else float(value),
        unit=unit,
        status="available" if value is not None and np.isfinite(value) else "unavailable",
        simple_meaning=d.simple,
        professional_definition=d.professional,
        formula=d.formula,
        why_it_matters=d.why,
        caveat=d.caveat,
        observation=observation,
    )


def latest_pair(series: pd.Series | None) -> tuple[float | None, float | None]:
    if series is None or series.empty:
        return None, None
    values = pd.to_numeric(series, errors="coerce").dropna()
    if values.empty:
        return None, None
    return float(values.iloc[0]), float(values.iloc[1]) if len(values) > 1 else None


def sorted_periods(frame: pd.DataFrame) -> list[str]:
    if frame.empty:
        return []
    def key(value: str):
        ts = pd.to_datetime(value, errors="coerce")
        return ts if not pd.isna(ts) else pd.Timestamp.min
    return sorted([str(c) for c in frame.columns], key=key, reverse=True)


def series_for(frame: pd.DataFrame, aliases: list[str]) -> pd.Series | None:
    if frame.empty:
        return None
    lowered = {str(idx).strip().lower(): idx for idx in frame.index}
    for alias in aliases:
        if alias.lower() in lowered:
            return pd.to_numeric(frame.loc[lowered[alias.lower()]], errors="coerce")
    for idx in frame.index:
        text = str(idx).lower()
        if any(alias.lower() in text for alias in aliases):
            return pd.to_numeric(frame.loc[idx], errors="coerce")
    return None


def average(a: float | None, b: float | None) -> float | None:
    if a is None and b is None:
        return None
    if a is None:
        return b
    if b is None:
        return a
    return (a + b) / 2.0


def safe_div(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    result = numerator / denominator
    return float(result) if np.isfinite(result) else None


def pct(numerator: float | None, denominator: float | None) -> float | None:
    value = safe_div(numerator, denominator)
    return None if value is None else value * 100.0
