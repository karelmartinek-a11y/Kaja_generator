from __future__ import annotations

import time

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QLabel,
    QProgressBar,
    QPushButton,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
    QDialog,
    QHBoxLayout,
)


class ProgressDialog(QDialog):
    stop_requested_changed = Signal(bool)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Kája - průběh běhu")
        self.setWindowModality(Qt.WindowModal)
        self._start_time = time.time()
        self._stop_requested = False

        self._status_label = QLabel("Čekám na spuštění")
        self._eta_label = QLabel("ETA: -")
        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._log_view = QPlainTextEdit()
        self._log_view.setReadOnly(True)
        self._stop_button = QPushButton("STOP")
        self._stop_button.clicked.connect(self._request_stop)
        self._stop_button.setEnabled(True)

        controls = QHBoxLayout()
        controls.addWidget(self._stop_button)
        controls.addStretch()
        controls.addWidget(self._eta_label)

        layout = QVBoxLayout(self)
        layout.addWidget(self._status_label)
        layout.addWidget(self._progress)
        layout.addLayout(controls)
        layout.addWidget(self._log_view)

    @property
    def stop_requested(self) -> bool:
        return self._stop_requested

    def update_progress(self, message: str, ratio: float) -> None:
        percent = max(0.0, min(1.0, ratio)) * 100
        self._progress.setValue(int(percent))
        self._status_label.setText(message)
        elapsed = time.time() - self._start_time
        if ratio > 0:
            eta = (1.0 - min(1.0, ratio)) * elapsed / (ratio + 1e-9)
            self._eta_label.setText(f"ETA: {int(eta)} s")
        self._log_view.appendPlainText(f"{message} ({percent:.1f} %)") if message else None

    def append_log(self, message: str) -> None:
        self._log_view.appendPlainText(message)

    def _request_stop(self) -> None:
        if not self._stop_requested:
            self._stop_requested = True
            self._status_label.setText("Stopping…")
            self.stop_requested_changed.emit(True)

