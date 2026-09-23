from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from equicafi.models import AnalysisResult


class SnapshotRepository:
    """Tiny SQLite snapshot store for reproducible local analysis."""

    def __init__(self, path: str | Path = "data/equicafi.sqlite3") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self):
        return sqlite3.connect(self.path)

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS analysis_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    generated_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                )"""
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_snapshot_ticker ON analysis_snapshots(ticker)")

    def save(self, result: AnalysisResult) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO analysis_snapshots(ticker, generated_at, payload_json) VALUES (?, ?, ?)",
                (result.company.ticker, result.generated_at.isoformat(), json.dumps(result.to_jsonable(), ensure_ascii=False)),
            )
            return int(cur.lastrowid)

    def latest(self, ticker: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT payload_json FROM analysis_snapshots WHERE ticker = ? ORDER BY id DESC LIMIT 1",
                (ticker.upper(),),
            ).fetchone()
        return json.loads(row[0]) if row else None
