# EQUICAFI

**Equity Intelligence Engine**

EQUICAFI is an educational and analytical equity research application. The engine combines fundamentals, historical analysis, valuation, technical indicators, risk metrics, cross-metric reasoning and hypothetical capital/return scenarios.

## Current build

This repository is the clean Prompt 1 engine build. Prompt 2 is intended to replace the lightweight dashboard stub with the final EQUICAFI interface, and Prompt 3 is intended for release/deployment work.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .
```

## Verify

```powershell
python -m pytest
python -m equicafi analyze DEMO --no-save
python -m equicafi history DEMO
python -m equicafi valuation DEMO
python -m equicafi scenario 50000 3500 5 10
```

For a real Yahoo Finance ticker:

```powershell
python -m equicafi analyze RELIANCE.NS --no-save
```

## Demo data

`DEMO` is synthetic and exists only to exercise the complete pipeline. It must never be described as live company data.

## Capital / Return Simulator

Capital Lab is a scenario calculator. It accepts user-supplied annual return assumptions and calculates the mathematical outcome. ROI is a percentage; increasing capital scales the rupee gain/loss at the same assumed return rate.

## Scope boundary

EQUICAFI is not a personal investment adviser. It does not select a "best" investment amount or provide personalized buy/sell instructions.
