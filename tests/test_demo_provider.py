import pandas as pd


def test_demo_provider_shape(demo_data):
    assert demo_data.synthetic is True
    assert demo_data.ticker == "DEMO"
    assert demo_data.company_name
    assert not demo_data.annual_financials.empty
    assert not demo_data.balance_sheet.empty
    assert not demo_data.cashflow.empty
    assert not demo_data.price_history.empty
    assert "Close" in demo_data.price_history.columns
    assert isinstance(demo_data.price_history.index, pd.DatetimeIndex)


def test_demo_provider_rejects_other_ticker():
    from equicafi.providers.demo import DemoProvider
    import pytest
    with pytest.raises(ValueError):
        DemoProvider().fetch("TCS.NS")
