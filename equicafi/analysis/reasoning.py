from __future__ import annotations

from equicafi.models import Metric, Observation


def build_reasoning(metrics: list[Metric], historical: dict[str, dict[str, float]] | None = None) -> list[Observation]:
    values = {m.name: m.value for m in metrics if m.value is not None}
    observations: list[Observation] = []

    roe, roa = values.get("ROE"), values.get("ROA")
    if roe is not None and roa is not None and roe > roa + 3:
        observations.append(Observation(
            title="ROE materially exceeds ROA",
            explanation=(f"ROE is {roe:.1f}% while ROA is {roa:.1f}%. The difference can partly reflect leverage and the different equity and asset bases, so the return profile is best read alongside the balance sheet."),
            related_metrics=["ROE", "ROA", "Debt / Equity"],
            severity="info",
        ))

    revenue_growth = values.get("Revenue Growth")
    op_margin = values.get("Operating Margin")
    prev_margin = _historical_latest_previous(historical or {}, "Operating Margin")
    if revenue_growth is not None and op_margin is not None and prev_margin is not None and revenue_growth > 0 and op_margin < prev_margin:
        observations.append(Observation(
            title="Revenue is growing while operating margin is compressing",
            explanation=(f"Revenue growth is {revenue_growth:.1f}% while operating margin fell from {prev_margin:.1f}% to {op_margin:.1f}%. In simple terms, sales are rising but the business is keeping slightly less operating profit from each rupee of revenue."),
            related_metrics=["Revenue Growth", "Operating Margin"],
            severity="watch",
        ))

    eps_growth = values.get("EPS Growth")
    if revenue_growth is not None and eps_growth is not None and eps_growth > revenue_growth + 3:
        observations.append(Observation(
            title="EPS is growing faster than revenue",
            explanation=(f"Revenue growth is {revenue_growth:.1f}% while EPS growth is {eps_growth:.1f}%. The gap can come from margin changes, share-count changes or non-operating effects; it should be decomposed rather than attributed to one cause."),
            related_metrics=["Revenue Growth", "EPS Growth", "EPS"],
            severity="info",
        ))
    elif revenue_growth is not None and eps_growth is not None and revenue_growth > eps_growth + 3:
        observations.append(Observation(
            title="Revenue is growing faster than EPS",
            explanation=(f"Revenue growth is {revenue_growth:.1f}% while EPS growth is {eps_growth:.1f}%. In simple terms, the top line is expanding faster than profit per share, so margin, financing and share-count effects deserve attention."),
            related_metrics=["Revenue Growth", "EPS Growth", "Operating Margin"],
            severity="watch",
        ))

    fcf_net = values.get("FCF / Net Income")
    if fcf_net is not None and fcf_net < 100:
        observations.append(Observation(
            title="Cash conversion is below accounting profit",
            explanation=(f"Free cash flow is {fcf_net:.1f}% of net income. This does not prove weak earnings quality; it means some accounting profit was absorbed by working-capital movements, capital spending or both."),
            related_metrics=["Free Cash Flow", "Net Profit", "Operating Cash Flow"],
            severity="watch",
        ))

    ocf_net = values.get("Operating Cash Flow / Net Income")
    if ocf_net is not None and fcf_net is not None:
        observations.append(Observation(
            title="Operating cash flow and free cash flow tell different parts of the story",
            explanation=(f"Operating cash flow is {ocf_net:.2f}x net income while free cash flow is {fcf_net:.1f}% of net income. The first shows cash generation from operations; the second also subtracts capital investment."),
            related_metrics=["Operating Cash Flow / Net Income", "FCF / Net Income", "Capital Expenditure"],
            severity="info",
        ))

    pe = values.get("P/E")
    if pe is not None:
        observations.append(Observation(
            title="Valuation needs an earnings-quality check",
            explanation=(f"P/E is {pe:.2f}x. In simple terms, the market price is being compared with current earnings per share. Professional interpretation still requires checking growth, margins, cash flow, leverage and whether current earnings are representative."),
            related_metrics=["P/E", "EPS", "EPS Growth", "Free Cash Flow"],
            severity="info",
        ))

    dd, vol = values.get("Maximum Drawdown"), values.get("Annualized Volatility")
    if dd is not None and vol is not None:
        observations.append(Observation(
            title="Observed market risk should be read from the trading history",
            explanation=(f"The observed price history shows a maximum drawdown of {dd:.1f}% and annualized volatility of {vol:.1f}%. These are descriptions of the selected historical window, not guarantees about future price behaviour."),
            related_metrics=["Maximum Drawdown", "Annualized Volatility"],
            severity="watch",
        ))

    debt_equity = values.get("Debt / Equity")
    coverage = values.get("Interest Coverage")
    if debt_equity is not None and coverage is not None:
        severity = "watch" if debt_equity > 1 or coverage < 3 else "info"
        observations.append(Observation(
            title="Leverage should be interpreted with interest coverage",
            explanation=(f"Debt-to-equity is {debt_equity:.2f}x and interest coverage is {coverage:.2f}x. The first describes financing structure; the second describes the operating-earnings cushion available for interest expense."),
            related_metrics=["Debt / Equity", "Interest Coverage"],
            severity=severity,
        ))

    liquidity = values.get("Liquidity Coverage")
    quick = values.get("Quick Liquidity Coverage")
    if liquidity is not None and quick is not None and liquidity < 1.0:
        observations.append(Observation(
            title="Short-term liquidity is below one-to-one coverage",
            explanation=(f"Current assets cover current liabilities by {liquidity:.2f}x and quick assets cover them by {quick:.2f}x. In simple terms, the balance sheet has less current-asset coverage than current liabilities under this snapshot."),
            related_metrics=["Liquidity Coverage", "Quick Liquidity Coverage"],
            severity="watch",
        ))

    return observations


def historical_reasoning(history: dict[str, dict[str, float]]) -> list[Observation]:
    if len(history) < 2:
        return []
    periods = list(history.keys())
    latest = history[periods[0]]
    oldest = history[periods[-1]]
    out: list[Observation] = []

    if "Revenue" in latest and "Revenue" in oldest and "Operating Margin" in latest and "Operating Margin" in oldest:
        rev_delta = latest["Revenue"] - oldest["Revenue"]
        if rev_delta > 0 and latest["Operating Margin"] < oldest["Operating Margin"]:
            out.append(Observation(
                title="Revenue increased while operating margin weakened",
                explanation=(f"Revenue moved from {oldest['Revenue']:.2f} to {latest['Revenue']:.2f}, while operating margin moved from {oldest['Operating Margin']:.1f}% to {latest['Operating Margin']:.1f}%."),
                related_metrics=["Revenue", "Operating Margin"],
                severity="watch",
            ))

    if "EPS" in latest and "EPS" in oldest and "Revenue" in latest and "Revenue" in oldest and oldest["EPS"] not in (None, 0) and oldest["Revenue"] not in (None, 0):
        eps_growth = (latest["EPS"] / oldest["EPS"] - 1) * 100
        rev_growth = (latest["Revenue"] / oldest["Revenue"] - 1) * 100
        if eps_growth > rev_growth + 2:
            out.append(Observation(
                title="Per-share earnings outpaced revenue over the observed periods",
                explanation=(f"EPS changed {eps_growth:.1f}% across the observed range versus revenue at {rev_growth:.1f}%. Margin, share-count and financing effects can all influence the gap."),
                related_metrics=["EPS", "Revenue"],
                severity="info",
            ))
    return out


def _historical_latest_previous(history: dict[str, dict[str, float]], name: str) -> float | None:
    for period, values in history.items():
        if name in values:
            # Return the next available period, not the same latest point.
            keys = list(history.keys())
            try:
                i = keys.index(period)
            except ValueError:
                continue
            for next_period in keys[i + 1:]:
                if name in history[next_period]:
                    return history[next_period][name]
            return None
    return None
