import pytest

from equicafi.services.scenario_service import simulate_return


def test_deployment_and_return():
    result = simulate_return(50000, 3500, 10, 2, "Base")
    assert result.shares == 14
    assert result.invested == 49000
    assert result.cash_remaining == 1000
    assert result.final_value == pytest.approx(60290.0)
    assert result.profit_loss == pytest.approx(10290.0)
    assert result.total_roi_pct == pytest.approx(20.58)


def test_negative_scenario():
    result = simulate_return(10000, 1000, -10, 1)
    assert result.final_value == pytest.approx(9000.0)
    assert result.total_roi_pct == pytest.approx(-10.0)


@pytest.mark.parametrize("capital,price", [(0, 100), (100, 0), (-1, 100)])
def test_invalid_deployment(capital, price):
    with pytest.raises(ValueError):
        simulate_return(capital, price, 10, 1)


def test_invalid_return_assumption():
    with pytest.raises(ValueError):
        simulate_return(1000, 100, -100, 1)
