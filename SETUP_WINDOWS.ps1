$ErrorActionPreference = "Stop"

Write-Host "EQUICAFI Prompt 1 setup" -ForegroundColor Yellow
Write-Host ""

if (-not (Test-Path ".\.venv")) {
    python -m venv .venv
}

Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& ".\.venv\Scripts\Activate.ps1"

python -m pip install --upgrade pip
pip install -e .

Write-Host ""
Write-Host "=== PYTHON ===" -ForegroundColor Cyan
python --version

Write-Host ""
Write-Host "=== SYNTAX ===" -ForegroundColor Cyan
python -m py_compile `
    .\equicafi\models\core.py `
    .\equicafi\analysis\fundamentals.py `
    .\equicafi\analysis\valuation.py `
    .\equicafi\analysis\technical.py `
    .\equicafi\analysis\risk.py `
    .\equicafi\analysis\reasoning.py `
    .\equicafi\providers\yahoo.py `
    .\equicafi\services\analysis_service.py `
    .\equicafi\services\scenario_service.py `
    .\dashboard\app.py

Write-Host "Syntax OK." -ForegroundColor Green

Write-Host ""
Write-Host "=== TESTS ===" -ForegroundColor Cyan
python -m pytest

Write-Host ""
Write-Host "=== DEMO ENGINE ===" -ForegroundColor Cyan
python -m equicafi analyze DEMO --no-save

Write-Host ""
Write-Host "Prompt 1 setup and validation complete." -ForegroundColor Green
Write-Host "Next major phase: Prompt 2 — final dashboard UI/UX." -ForegroundColor Yellow
