from equicafi.providers.demo import DemoProvider
from equicafi.analysis.valuation import compute_valuation, add_historical_valuation


def test_demo_valuation():
    d = DemoProvider().fetch("DEMO")
    metrics, history = compute_valuation(
        d.annual_financials,
        d.balance_sheet,
        d.cashflow,
        d.current_price,
    )
    names = {m.name for m in metrics}
    assert {"P/E", "P/B", "P/S", "EV/EBITDA", "Earnings Yield", "FCF Yield"}.issubset(names)
    hv = add_historical_valuation(history, d.price_history)
    assert any("P/E" in values for values in hv.values())
    assert next(m for m in metrics if m.name == "P/B").value is not None
