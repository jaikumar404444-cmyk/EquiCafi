from __future__ import annotations

import json
from pathlib import Path

import typer

from equicafi.database import SnapshotRepository
from equicafi.reporting import render_report
from equicafi.services.analysis_service import AnalysisService
from equicafi.services.scenario_service import simulate_return

app = typer.Typer(help="EQUICAFI — Equity Intelligence Engine")


def _analysis(ticker: str):
    return AnalysisService().analyze(ticker.strip().upper())


@app.command()
def analyze(
    ticker: str,
    save: bool = typer.Option(True, "--save/--no-save", help="Save the structured result to local SQLite."),
    json_output: Path | None = typer.Option(None, "--json-output", help="Write the structured analysis to JSON."),
):
    """Run a complete equity analysis."""
    result = _analysis(ticker)
    print(render_report(result))
    if save:
        snapshot_id = SnapshotRepository().save(result)
        print(f"\nSnapshot saved locally as #{snapshot_id}.")
    if json_output:
        json_output.parent.mkdir(parents=True, exist_ok=True)
        json_output.write_text(json.dumps(result.to_jsonable(), indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"JSON report written to {json_output}")


@app.command()
def history(ticker: str):
    """Show the historical financial series detected for a ticker."""
    result = _analysis(ticker)
    if not result.history:
        print("No historical financial series were available.")
        raise typer.Exit()
    for period, values in result.history.items():
        print(f"\n{period}")
        for name, value in values.items():
            print(f"  {name:<30} {value:,.2f}")


@app.command()
def valuation(ticker: str):
    """Show current and historical valuation metrics."""
    result = _analysis(ticker)
    print("Current valuation")
    print("=" * 60)
    for metric in result.valuation:
        value = "—" if metric.value is None else f"{metric.value:.2f}{'%' if metric.unit == '%' else 'x' if metric.unit == 'x' else ''}"
        print(f"{metric.name:<28} {value:>12}")
    print("\nHistorical valuation")
    print("=" * 60)
    for period, values in result.valuation_history.items():
        pe = values.get("P/E")
        ey = values.get("Earnings Yield")
        if pe is not None or ey is not None:
            print(f"{period}: P/E={pe:.2f}x" if pe is not None else f"{period}: P/E=—", end="")
            print(f", Earnings Yield={ey:.2f}%" if ey is not None else ", Earnings Yield=—")


@app.command("scenario")
def scenario(
    capital: float,
    share_price: float,
    years: int,
    annual_return_pct: float,
):
    """Calculate one hypothetical capital/return scenario."""
    result = simulate_return(capital, share_price, annual_return_pct, years)
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    app()
