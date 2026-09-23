from typer.testing import CliRunner

from equicafi.cli import app


def test_cli_analyze_demo():
    runner = CliRunner()
    result = runner.invoke(app, ["analyze", "DEMO", "--no-save"])
    assert result.exit_code == 0
    assert "EQUICAFI Demonstration Holdings" in result.stdout
    assert "Simple:" in result.stdout


def test_cli_history_demo():
    runner = CliRunner()
    result = runner.invoke(app, ["history", "DEMO"])
    assert result.exit_code == 0
    assert "Revenue" in result.stdout


def test_cli_valuation_demo():
    runner = CliRunner()
    result = runner.invoke(app, ["valuation", "DEMO"])
    assert result.exit_code == 0
    assert "P/E" in result.stdout


def test_cli_scenario():
    runner = CliRunner()
    result = runner.invoke(app, ["scenario", "50000", "3500", "5", "10"])
    assert result.exit_code == 0
    assert "total_roi_pct" in result.stdout
