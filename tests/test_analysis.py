import pytest

from equicafi.services.analysis_service import AnalysisService


def result():
    return AnalysisService().analyze("DEMO")


def test_demo_analysis_has_core_sections():
    r = result()
    assert r.company.ticker == "DEMO"
    assert r.data_quality.status == "synthetic demo data"
    assert r.current_price.value is not None
    assert any(m.name == "Revenue" and m.value is not None for m in r.fundamentals)
    assert any(m.name == "Free Cash Flow" and m.value is not None for m in r.fundamentals)
    assert any(m.name == "P/E" for m in r.valuation)
    assert any(m.name == "RSI 14" for m in r.technicals)
    assert any(m.name == "Maximum Drawdown" for m in r.risk)


def test_demo_history_exists():
    r = result()
    assert len(r.history) >= 5
    assert "Revenue" in next(iter(r.history.values()))


def test_reasoning_is_structured():
    r = result()
    assert r.observations
    for obs in r.observations:
        assert obs.title
        assert obs.explanation
        assert obs.severity in {"info", "watch", "risk"}
        assert not obs.explanation.startswith("{")


def test_metric_explanations_have_simple_and_professional_language():
    r = result()
    for metric in r.all_metrics():
        assert metric.simple_meaning
        assert metric.professional_definition
        assert metric.formula
        assert metric.why_it_matters
        assert metric.caveat
