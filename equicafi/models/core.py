from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

Severity = Literal["info", "watch", "risk"]


class Metric(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    value: float | None = None
    unit: str = ""
    status: Literal["available", "unavailable"] = "available"
    simple_meaning: str
    professional_definition: str
    formula: str
    why_it_matters: str
    caveat: str
    observation: str | None = None


class Observation(BaseModel):
    title: str
    explanation: str
    related_metrics: list[str] = Field(default_factory=list)
    severity: Severity = "info"


class CompanyProfile(BaseModel):
    ticker: str
    name: str
    exchange: str | None = None
    sector: str | None = None
    industry: str | None = None
    currency: str = "INR"
    website: str | None = None


class DataQuality(BaseModel):
    source: str
    status: str
    quality: Literal["high", "medium", "low", "unknown"]
    notes: list[str] = Field(default_factory=list)


class PriceSeries(BaseModel):
    dates: list[date | datetime | str]
    close: list[float]


class ScenarioResult(BaseModel):
    scenario: str
    capital: float
    share_price: float
    shares: int
    invested: float
    cash_remaining: float
    annual_return_pct: float
    years: int
    final_value: float
    profit_loss: float
    total_roi_pct: float
    cagr_pct: float


class AnalysisResult(BaseModel):
    company: CompanyProfile
    data_quality: DataQuality
    current_price: Metric
    fundamentals: list[Metric] = Field(default_factory=list)
    valuation: list[Metric] = Field(default_factory=list)
    technicals: list[Metric] = Field(default_factory=list)
    risk: list[Metric] = Field(default_factory=list)
    observations: list[Observation] = Field(default_factory=list)
    historical_observations: list[Observation] = Field(default_factory=list)
    history: dict[str, dict[str, float]] = Field(default_factory=dict)
    valuation_history: dict[str, dict[str, float]] = Field(default_factory=dict)
    price_history: PriceSeries | None = None
    limitations: list[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def all_metrics(self) -> list[Metric]:
        return [self.current_price, *self.fundamentals, *self.valuation, *self.technicals, *self.risk]

    def metric(self, name: str) -> Metric | None:
        normalized = name.strip().lower()
        for metric in self.all_metrics():
            if metric.name.strip().lower() == normalized:
                return metric
        return None

    def to_jsonable(self) -> dict[str, Any]:
        return self.model_dump(mode="json")
