from __future__ import annotations

from math import floor

from equicafi.models import ScenarioResult


def simulate_return(
    capital: float,
    share_price: float,
    annual_return_pct: float,
    years: int,
    scenario: str = "Scenario",
) -> ScenarioResult:
    """Model a hypothetical annual-compounded return on whole-share capital."""
    if capital <= 0:
        raise ValueError("Capital must be greater than zero.")
    if share_price <= 0:
        raise ValueError("Share price must be greater than zero.")
    if years <= 0:
        raise ValueError("Holding period must be greater than zero.")
    if annual_return_pct <= -100:
        raise ValueError("Annual return assumption must be greater than -100%.")

    shares = floor(capital / share_price)
    invested = shares * share_price
    cash_remaining = capital - invested
    annual_rate = annual_return_pct / 100.0
    final_value = invested * ((1 + annual_rate) ** years) + cash_remaining
    profit_loss = final_value - capital
    roi = profit_loss / capital * 100.0
    cagr = ((final_value / capital) ** (1 / years) - 1) * 100.0 if final_value > 0 else -100.0

    return ScenarioResult(
        scenario=scenario,
        capital=float(capital),
        share_price=float(share_price),
        shares=int(shares),
        invested=float(invested),
        cash_remaining=float(cash_remaining),
        annual_return_pct=float(annual_return_pct),
        years=int(years),
        final_value=float(final_value),
        profit_loss=float(profit_loss),
        total_roi_pct=float(roi),
        cagr_pct=float(cagr),
    )
