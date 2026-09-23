$ErrorActionPreference = "Stop"
python -m py_compile .\equicafi\models\core.py .\equicafi\providers\yahoo.py .\equicafi\services\analysis_service.py .\equicafi\services\scenario_service.py .\dashboard\app.py
python -m pytest
