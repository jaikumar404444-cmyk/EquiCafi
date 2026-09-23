from __future__ import annotations

from typing import Iterable

from equicafi.models import AnalysisResult, Metric, Observation


def money(value: float | None, currency: str = "INR") -> str:
    if value is None:
        return "—"
    sign = "-" if value < 0 else ""
    x = abs(value)
    if x >= 1_000_000_000_000:
        return f"{sign}{currency} {x/1_000_000_000_000:.2f}T"
    if x >= 1_000_000_000:
        return f"{sign}{currency} {x/1_000_000_000:.2f}B"
    if x >= 1_000_000:
        return f"{sign}{currency} {x/1_000_000:.2f}M"
    if x >= 1_000:
        return f"{sign}{currency} {x:,.0f}"
    return f"{sign}{currency} {x:,.2f}"


def value_text(metric: Metric) -> str:
    if metric.value is None:
        return "—"
    if metric.unit == "currency":
        return money(metric.value)
    if metric.unit == "currency/share":
        return money(metric.value) + "/share"
    if metric.unit == "%":
        return f"{metric.value:.2f}%"
    if metric.unit == "x":
        return f"{metric.value:.2f}x"
    if metric.unit == "index":
        return f"{metric.value:.2f}"
    return f"{metric.value:.2f} {metric.unit}".strip()


def render_metric(metric: Metric) -> str:
    lines = [f"{metric.name:<35} {value_text(metric):>12}"]
    if metric.observation:
        lines.append(f"  • {metric.observation}")
    lines.append(f"  Simple: {metric.simple_meaning}")
    lines.append(f"  Professional: {metric.professional_definition}")
    lines.append(f"  Formula: {metric.formula}")
    lines.append(f"  Why it matters: {metric.why_it_matters}")
    lines.append(f"  Caveat: {metric.caveat}")
    return "\n".join(lines)


def render_report(result: AnalysisResult) -> str:
    lines = [
        f"{result.company.name} [{result.company.ticker}]",
        f"Source: {result.data_quality.source} | Data status: {result.data_quality.status} | Data quality: {result.data_quality.quality}",
        "",
        "EQUICAFI Summary",
        "=" * 70,
        "EQUICAFI is an analytical and educational system. Interpret each metric in context; this output is not personalized investment advice.",
        "",
        "Financial & Valuation",
        "=" * 70,
    ]
    for m in [*result.fundamentals, *result.valuation]:
        lines.append(render_metric(m))
        lines.append("")
    lines.extend(["Technicals & Risk", "=" * 70])
    for m in [*result.technicals, *result.risk]:
        lines.append(render_metric(m))
        lines.append("")
    lines.extend(["Cross-metric observations", "=" * 70])
    for obs in result.observations:
        lines.append(f"• {obs.title}: {obs.explanation}")
    if result.historical_observations:
        lines.extend(["", "Historical observations", "=" * 70])
        for obs in result.historical_observations:
            lines.append(f"• {obs.title}: {obs.explanation}")
    if result.limitations:
        lines.extend(["", "Limitations", "=" * 70])
        for limitation in result.limitations:
            lines.append(f"• {limitation}")
    return "\n".join(lines)
