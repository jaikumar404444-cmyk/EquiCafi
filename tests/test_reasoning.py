from equicafi.analysis.reasoning import build_reasoning, historical_reasoning
from equicafi.analysis.common import metric


def test_reasoning_detects_roe_roa_gap():
    items = [
        metric("ROE", 24.0, "%"),
        metric("ROA", 12.0, "%"),
        metric("Debt / Equity", 0.5, "x"),
    ]
    obs = build_reasoning(items)
    assert any(o.title == "ROE materially exceeds ROA" for o in obs)


def test_historical_reasoning_detects_margin_compression():
    history = {
        "2025": {"Revenue": 1200, "Operating Margin": 20, "EPS": 12},
        "2024": {"Revenue": 1000, "Operating Margin": 21, "EPS": 10},
    }
    obs = historical_reasoning(history)
    assert any("margin" in o.title.lower() for o in obs)
