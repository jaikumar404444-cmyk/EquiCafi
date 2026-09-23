from equicafi.providers.demo import DemoProvider
from equicafi.analysis.technical import compute_technical
from equicafi.analysis.risk import compute_risk


def test_technical_metrics_are_computed():
    data = DemoProvider().fetch("DEMO")
    metrics = {m.name: m.value for m in compute_technical(data.price_history)}
    assert metrics["52 Week High"] is not None
    assert metrics["52 Week Low"] is not None


def test_risk_metrics_are_computed():
    data = DemoProvider().fetch("DEMO")
    metrics = {
        m.name: m.value
        for m in compute_risk(data.price_history, data.annual_financials, data.balance_sheet, data.cashflow)
    }
    assert metrics["Annualized Volatility"] is not None
    assert metrics["Maximum Drawdown"] is not None
    assert metrics["FCF / Debt"] is not None
    assert metrics["Liquidity Coverage"] is not None
