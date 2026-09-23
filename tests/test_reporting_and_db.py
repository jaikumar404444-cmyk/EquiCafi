from pathlib import Path

from equicafi.database import SnapshotRepository
from equicafi.reporting import render_report
from equicafi.services.analysis_service import AnalysisService


def test_report_contains_dual_language_sections(tmp_path: Path):
    result = AnalysisService().analyze("DEMO")
    text = render_report(result)
    assert "Simple:" in text
    assert "Professional:" in text
    assert "Limitations" in text


def test_snapshot_repository(tmp_path: Path):
    result = AnalysisService().analyze("DEMO")
    repo = SnapshotRepository(tmp_path / "equicafi.sqlite3")
    snapshot_id = repo.save(result)
    assert snapshot_id == 1
    loaded = repo.latest("DEMO")
    assert loaded is not None
    assert loaded["company"]["ticker"] == "DEMO"
