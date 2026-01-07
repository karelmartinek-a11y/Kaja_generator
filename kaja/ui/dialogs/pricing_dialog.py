from __future__ import annotations

import json
from typing import Any, Dict, List

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QHeaderView,
    QSizePolicy,
)

from kaja.core.price_catalog import PriceCatalog
from kaja.core.pricing import PricingStore


class PricingDialog(QDialog):
    def __init__(self, store: PricingStore, catalog: PriceCatalog, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CENY")
        self._store = store
        self._catalog = catalog
        self._receipts: List[Any] = []

        layout = QVBoxLayout(self)

        header = QHBoxLayout()
        self._status_label = QLabel()
        header.addWidget(self._status_label, 1)
        self._refresh_catalog_button = QPushButton("Obnovit ceník")
        header.addWidget(self._refresh_catalog_button)
        layout.addLayout(header)

        price_group = QGroupBox("Modelové sazby / ceník")
        price_layout = QVBoxLayout(price_group)
        self._price_table = QTableWidget(0, 6)
        self._price_table.setHorizontalHeaderLabels(
            [
                "Model",
                "Input token (USD)",
                "Output token (USD)",
                "Vector file (USD)",
                "Vector GB (USD)",
                "File API (USD)",
            ]
        )
        self._price_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._price_table.horizontalHeader().setMinimumSectionSize(0)
        price_layout.addWidget(self._price_table)
        layout.addWidget(price_group)

        receipts_group = QGroupBox("Účtenky")
        receipts_layout = QVBoxLayout(receipts_group)
        self._table = QTableWidget(0, 8)
        self._table.setHorizontalHeaderLabels(
            [
                "Run ID",
                "Project",
                "Model",
                "Mode",
                "Response ID",
                "Estimated",
                "Actual",
                "Status",
            ]
        )
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.horizontalHeader().setMinimumSectionSize(0)
        receipts_layout.addWidget(self._table)
        layout.addWidget(receipts_group)

        self._details = QPlainTextEdit()
        self._details.setReadOnly(True)
        self._details.setPlaceholderText("Vyberte účtenku pro zobrazení detailu.")
        self._details.setMinimumSize(0, 0)
        self._details.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self._details)

        toolbar = QHBoxLayout()
        refresh_button = QPushButton("Obnovit účtenky")
        close_button = QPushButton("ZAVŘÍT")
        toolbar.addWidget(refresh_button)
        toolbar.addWidget(close_button)
        layout.addLayout(toolbar)

        refresh_button.clicked.connect(self._refresh_receipts)
        self._refresh_catalog_button.clicked.connect(self._refresh_catalog)
        close_button.clicked.connect(self.accept)
        self._table.selectionModel().selectionChanged.connect(self._on_selection_change)

        self._populate_price_table()
        self._update_status_label()
        self._refresh_receipts()

    def _update_status_label(self) -> None:
        summary = self._catalog.summary()
        status = summary.get("status", "Neznámý")
        source = summary.get("source") or "lokální"
        refreshed = summary.get("last_refreshed") or "nikdy"
        verified = summary.get("verified", False)
        color = "#fff" if verified else "#808080"
        self._status_label.setText(
            f"{status} • Zdroj: {source} • Poslední aktualizace: {refreshed}"
        )
        self._status_label.setStyleSheet(f"color: {color}; font-weight: bold;")

    def _refresh_catalog(self) -> None:
        refreshed = self._catalog.refresh()
        if refreshed:
            QMessageBox.information(self, "Ceník aktualizován", "Ceník byl úspěšně stažen z online zdroje.")
        else:
            QMessageBox.warning(self, "Offline ceník", "Ceník zůstává v režimu odhadu / offline režimu.")
        self._populate_price_table()
        self._update_status_label()

    def _populate_price_table(self) -> None:
        rates_table = self._catalog.model_rate_table()
        self._price_table.setRowCount(len(rates_table))
        for row, (model, rates) in enumerate(sorted(rates_table.items())):
            self._price_table.setItem(row, 0, QTableWidgetItem(model))
            self._price_table.setItem(row, 1, QTableWidgetItem(f"{rates.get('input_token_rate', 0):.6f}"))
            self._price_table.setItem(row, 2, QTableWidgetItem(f"{rates.get('output_token_rate', 0):.6f}"))
            self._price_table.setItem(row, 3, QTableWidgetItem(f"{rates.get('vector_store_file_rate', 0):.6f}"))
            self._price_table.setItem(row, 4, QTableWidgetItem(f"{rates.get('vector_store_gb_rate', 0):.6f}"))
            self._price_table.setItem(row, 5, QTableWidgetItem(f"{rates.get('file_api_rate', 0):.6f}"))

    def _refresh_receipts(self) -> None:
        receipts = self._store.list_receipts()
        self._receipts = [receipt for receipt in receipts]
        self._table.setRowCount(len(receipts))
        for row, receipt in enumerate(receipts):
            details: Dict[str, Any] | None = None
            estimated = None
            actual = None
            try:
                details = json.loads(receipt.details_json)
            except Exception:
                details = None
            if isinstance(details, dict):
                estimated = details.get("run_estimated_total_cost")
                if not isinstance(estimated, (int, float)):
                    estimated = details.get("total_cost")
                actual = details.get("run_actual_total_cost")
                if not isinstance(actual, (int, float)):
                    per_call = details.get("per_call_pricing")
                    if isinstance(per_call, dict):
                        totals = per_call.get("totals")
                        if isinstance(totals, dict):
                            actual_summary = totals.get("actual")
                            if isinstance(actual_summary, dict):
                                actual = actual_summary.get("total_cost")
            if not isinstance(estimated, (int, float)) and not isinstance(actual, (int, float)):
                if isinstance(receipt.total_cost, (int, float)):
                    estimated = receipt.total_cost
            self._table.setItem(row, 0, QTableWidgetItem(receipt.run_id))
            self._table.setItem(row, 1, QTableWidgetItem(receipt.project))
            self._table.setItem(row, 2, QTableWidgetItem(receipt.model))
            self._table.setItem(row, 3, QTableWidgetItem(receipt.mode))
            self._table.setItem(row, 4, QTableWidgetItem(receipt.response_id))
            estimated_text = f"{estimated:.6f}" if isinstance(estimated, (int, float)) else "-"
            actual_text = f"{actual:.6f}" if isinstance(actual, (int, float)) else "-"
            self._table.setItem(row, 5, QTableWidgetItem(estimated_text))
            self._table.setItem(row, 6, QTableWidgetItem(actual_text))
            status_text = "ověřeno" if receipt.verified_pricing else "odhad"
            status_item = QTableWidgetItem(status_text)
            status_color = QColor("#fff") if receipt.verified_pricing else QColor("#808080")
            status_item.setForeground(status_color)
            self._table.setItem(row, 7, status_item)
        if receipts:
            self._table.selectRow(0)
            self._update_details_view(0)
        else:
            self._details.clear()

    def _on_selection_change(self, *_: List[str]) -> None:
        selected = self._table.selectionModel().selectedRows()
        if not selected:
            return
        row = selected[0].row()
        self._update_details_view(row)

    def _update_details_view(self, index: int) -> None:
        if index < 0 or index >= len(self._receipts):
            self._details.setPlainText("Žádný detail k zobrazení.")
            return
        receipt = self._receipts[index]
        try:
            payload = json.loads(receipt.details_json)
            formatted = json.dumps(payload, indent=2, ensure_ascii=False)
        except Exception:
            formatted = receipt.details_json
        summary = self._catalog.summary()
        extras = {
            "pricing_catalog": summary,
            "verified_pricing": receipt.verified_pricing,
        }
        combined = f"{formatted}\n\n{json.dumps(extras, indent=2, ensure_ascii=False)}"
        self._details.setPlainText(combined)
