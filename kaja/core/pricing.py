from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional


@dataclass
class Receipt:
    run_id: str
    project: str
    model: str
    mode: str
    response_id: str
    total_cost: float
    details_json: str
    created_at: str
    verified_pricing: bool


class PricingStore:
    def __init__(self, db_path: Path) -> None:
        self._path = db_path
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self._path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS receipts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT,
                    project TEXT,
                    model TEXT,
                    mode TEXT,
                    response_id TEXT,
                    total_cost REAL,
                    details_json TEXT,
                    created_at TEXT,
                    verified_pricing INTEGER
                )
                """
            )

    def add_receipt(self, receipt: Receipt) -> None:
        with sqlite3.connect(self._path) as conn:
            conn.execute(
                """
                INSERT INTO receipts
                (run_id, project, model, mode, response_id, total_cost, details_json, created_at, verified_pricing)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    receipt.run_id,
                    receipt.project,
                    receipt.model,
                    receipt.mode,
                    receipt.response_id,
                    receipt.total_cost,
                    receipt.details_json,
                    receipt.created_at,
                    1 if receipt.verified_pricing else 0,
                ),
            )

    def list_receipts(self) -> List[Receipt]:
        with sqlite3.connect(self._path) as conn:
            rows = conn.execute(
                "SELECT run_id, project, model, mode, response_id, total_cost, details_json, created_at, verified_pricing FROM receipts"
            ).fetchall()
        return [
            Receipt(
                run_id=row[0],
                project=row[1],
                model=row[2],
                mode=row[3],
                response_id=row[4],
                total_cost=row[5],
                details_json=row[6],
                created_at=row[7],
                verified_pricing=bool(row[8]),
            )
            for row in rows
        ]

    def delete_receipt(self, run_id: str) -> None:
        with sqlite3.connect(self._path) as conn:
            conn.execute("DELETE FROM receipts WHERE run_id = ?", (run_id,))
