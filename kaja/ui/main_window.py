from __future__ import annotations

import difflib
import json
import math
import os
import shutil
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from PySide6.QtCore import Qt, QMimeData, QSize, QTimer, QPoint, QRect
from PySide6.QtGui import (
    QCursor,
    QDrag,
    QFont,
    QFontMetrics,
    QGuiApplication,
    QPixmap,
    QPainter,
    QPen,
    QColor,
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QLayout,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QSplitter,
    QAbstractScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QMainWindow,
)

from .. import __version__
from ..core.log_manager import (
    configure_log_encryption,
    init_run,
    log_file_operation,
    log_file_upload,
    log_manifest,
    log_run_index,
    log_run_metadata,
    log_ui_state,
    log_vector_store_entry,
)
from ..core.openai_client import OpenAIClient
from ..core.pipeline import PipelineCancelled, PipelineExecutor, PipelineResult
from ..core.pricing import PricingStore
from ..core.price_catalog import PriceCatalog
from ..core.settings import SettingsStore
from ..core.state import DiagnosticsOptions, FileRecord, RunArtifacts, SshOptions, UiState, VectorStoreRecord
from ..core.diagnostics import (
    DiagnosticPackage,
    collect_ssh_diagnostics,
    collect_windows_diagnostics,
)
from ..core import security
from .dialogs import ProgressDialog
from .dialogs.api_key_dialog import ApiKeyDialog
from .dialogs.pricing_dialog import PricingDialog
from .dialogs.settings_dialog import SettingsDialog
from .section_card import SectionCard
try:
    import winreg
except ImportError:
    winreg = None


class StatusThermometer(QWidget):
    """Monochrome progress indicator shaped like a thermometer (2.05.000)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._progress = 0.0
        self.setMinimumHeight(16)
        self.setMaximumHeight(16)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def set_progress(self, ratio: float) -> None:
        self._progress = max(0.0, min(1.0, ratio))
        self.update()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(0, 0, -1, -1)
        pen = QPen(QColor("#fff"))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(rect, 8, 8)
        if self._progress:
            fill_width = max(1, int(rect.width() * self._progress))
            fill_rect = QRect(rect.left(), rect.top(), fill_width, rect.height())
            painter.fillRect(fill_rect, QColor("#fff"))


class StatusBar(QFrame):
    """Header status bar that reports time/date plus dynamic progress (5.04.000)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("status_bar")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 6, 16, 6)
        layout.setSpacing(16)
        self._time_label = QLabel()
        self._state_label = QLabel("PROGRAM NIC NEDĚLÁ")
        self._state_label.setAlignment(Qt.AlignCenter)
        self._countdown_label = QLabel("ETA: N/A")
        self._progress_label = QLabel("0%")
        self._thermometer = StatusThermometer(self)
        layout.addWidget(self._time_label)
        layout.addWidget(self._state_label, 1)
        layout.addWidget(self._countdown_label)
        layout.addWidget(self._progress_label)
        layout.addWidget(self._thermometer, 2)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh_time)
        self._timer.start(1000)
        self._progress_start: Optional[datetime] = None
        self._refresh_time()
        self.mark_idle()

    def _refresh_time(self) -> None:
        now = datetime.now()
        self._time_label.setText(
            f"ČAS {now.strftime('%H:%M:%S')}   DATUM {now.strftime('%Y-%m-%d')}"
        )

    def start_progress(self, message: str) -> None:
        self._progress_start = datetime.utcnow()
        self.update_progress(message, 0.0)

    def update_progress(self, message: str, ratio: float) -> None:
        text = (message or "PROCES").upper()
        self._state_label.setText(text)
        self._thermometer.set_progress(ratio)
        percent = int(round(max(0.0, min(1.0, ratio)) * 100))
        self._progress_label.setText(f"{percent}%")
        self._countdown_label.setText(self._compute_eta(ratio))

    def mark_idle(self, message: str = "PROGRAM NIC NEDĚLÁ") -> None:
        self._progress_start = None
        self._state_label.setText(message.upper())
        self._thermometer.set_progress(0.0)
        self._progress_label.setText("0%")
        self._countdown_label.setText("ETA: N/A")

    def _compute_eta(self, ratio: float) -> str:
        if not self._progress_start or ratio <= 0 or ratio >= 1:
            return "ETA: N/A" if ratio < 1 else "ETA: 0s"
        elapsed = (datetime.utcnow() - self._progress_start).total_seconds()
        if not ratio:
            return "ETA: N/A"
        remaining = elapsed * (1.0 - ratio) / ratio
        return f"ETA: {int(remaining)} s"


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Kája – SuperCodex")
        self.setMinimumSize(0, 0)
        self._root_dir = Path(__file__).resolve().parents[2]
        self._settings_store = SettingsStore(self._root_dir)
        self._settings = self._settings_store.load()
        self._price_catalog = PriceCatalog(
            cache_path=self._root_dir / "pricing_cache.json",
            settings=self._settings,
        )
        self._price_catalog.refresh_if_needed(force=self._settings.pricing_auto_refresh)
        self._apply_security_settings()
        self._openai_client: Optional[OpenAIClient] = None
        self._auto_init_done = False

        self._batch_table = self._create_batch_table()
        self._attached_table = self._create_file_table(["Name", "Purpose", "Size"])
        self._file_api_table = self._create_file_table(["ID", "Name", "Purpose", "Size"])
        self._local_files_table = self._create_file_table(["Name", "Path", "Akce"])
        self._vector_list = QListWidget()
        self._vector_detail = QPlainTextEdit()
        self._answare_view = QPlainTextEdit()

        self._attached_files: List[FileRecord] = []
        self._file_api_records: List[FileRecord] = []
        self._vector_stores: List[VectorStoreRecord] = []
        self._vector_store_files: Dict[str, List[str]] = {}
        self._local_files: List[Path] = []
        self._controls_initialized = False
        self._progress_dialog: ProgressDialog | None = None
        self._script_running = False
        self._last_response_text = ""
        self._last_response_id = ""
        self._timeline_entries: List[Dict[str, Any]] = []
        self._last_timeline_log: Optional[str] = None
        self._batch_jobs: List[Dict[str, Any]] = []
        self._diff_view = QPlainTextEdit()
        self._diff_view.setReadOnly(True)
        self._diff_view.setPlainText("Spusťte pipeline pro zobrazení diffu IN ↔ OUT.")
        self._diff_status_label = QLabel("Diff viewer čeká na spuštění runu.")
        self._status_bar = StatusBar(self)
        self._last_run_ui_state: UiState | None = None

        self._init_ui()
        self._apply_manifest_styles()
        self._ensure_api_key_loaded()
        self._refresh_batch_monitor()
        self._refresh_file_api_table()
        self._refresh_attached_table()
        self._refresh_vector_store_view()
        self._apply_settings_to_ssh_fields()
        QTimer.singleShot(200, self._auto_initialize_api_state)

    def minimumSizeHint(self) -> QSize:
        return QSize(0, 0)

    def _init_ui(self) -> None:
        self._init_controls()
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.setSizeConstraint(QLayout.SetNoConstraint)
        root_layout.addWidget(self._build_header())
        root_layout.addWidget(self._build_workspace(), 1)

    def _auto_initialize_api_state(self) -> None:
        if self._auto_init_done:
            return
        key = os.environ.get("OPENAI_API_KEY") or self.api_key_edit.text().strip()
        dialog = ProgressDialog(self)
        dialog.setWindowTitle("Inicializace OpenAI")
        dialog.update_progress("Připravuji spojení…", 0.1)
        dialog.show()
        QApplication.processEvents()
        try:
            if not key:
                self._append_log("Automatická inicializace skipped: API key chybí.")
                return
            client = OpenAIClient(key)
            self._openai_client = client
            dialog.update_progress("Načítám modely…", 0.25)
            QApplication.processEvents()
            models = client.list_models()
            if models:
                self.model_combo.clear()
                self.model_combo.addItems(models)
            dialog.update_progress("Načítám soubory Files API…", 0.45)
            QApplication.processEvents()
            files = client.list_files()
            self._file_api_records = [
                FileRecord(
                    file_id=item.get("id") or item.get("file_id") or str(uuid.uuid4())[:8],
                    filename=item.get("filename") or item.get("name") or "file",
                    purpose=item.get("purpose") or "user data",
                    size_bytes=int(item.get("size") or item.get("bytes") or 0),
                )
                for item in files
            ]
            dialog.update_progress("Načítám vector store…", 0.65)
            QApplication.processEvents()
            stores = client.list_vector_stores()
            self._vector_stores = [
                VectorStoreRecord(
                    store_id=item.get("id") or str(uuid.uuid4())[:8],
                    name=item.get("name") or "vector store",
                    expires_at=item.get("expires_at"),
                )
                for item in stores
            ]
            dialog.update_progress("Načítám batch joby…", 0.85)
            QApplication.processEvents()
            batches = client.list_batch_jobs()
            self._batch_jobs = [
                {
                    "id": job.get("id") or job.get("run_id") or f"batch_{idx}",
                    "status": job.get("status", "unknown"),
                    "created": job.get("created_at") or job.get("start") or "",
                    "eta": job.get("eta") or job.get("duration") or "",
                }
                for idx, job in enumerate(batches)
            ] or self._batch_jobs
            self._refresh_file_api_table()
            self._refresh_vector_store_view()
            self._refresh_batch_monitor()
            self._append_log("Automatická inicializace OpenAI dokončena.")
        except Exception as exc:
            self._append_log(f"Automatická inicializace selhala: {exc}")
            message = f"Nelze načíst data z OpenAI: {exc}"
            if self._is_connection_error(exc):
                message += " Zkontrolujte připojení nebo proxy."
            QMessageBox.warning(self, "Inicializace", message)
        finally:
            dialog.close()
            self._auto_init_done = True

    def _init_controls(self) -> None:
        if self._controls_initialized:
            return
        self._controls_initialized = True
        self.project_name_edit = QLineEdit()
        self.prompt_edit = QPlainTextEdit()
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["GENERATE", "MODIFY", "QA"])
        self.mode_combo.setCurrentText("GENERATE")
        self.send_as_c_checkbox = QCheckBox("SEND AS C (BATCH)")
        self.in_dir_edit = QLineEdit()
        self.out_dir_edit = QLineEdit()
        self.response_id_edit = QLineEdit()
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("API Key")
        self.model_combo = QComboBox()
        self.model_combo.addItems(["gpt-4o", "gpt-4o-mini", "gpt-4o-mini-transcribe"])
        self.temperature_spin = QSpinBox()
        self.temperature_spin.setRange(0, 20)
        self.temperature_spin.setValue(2)
        self.temperature_spin.setSuffix(" ×0.1")
        self.get_models_button = QPushButton("GET MODELS")
        self.go_button = QPushButton("KÁJA GO")
        self.log_edit = QPlainTextEdit()
        self.log_edit.setReadOnly(True)
        self.windows_in_checkbox = QCheckBox("WINDOWS IN")
        self.windows_out_checkbox = QCheckBox("WINDOWS OUT")
        self.ssh_in_checkbox = QCheckBox("SSH IN")
        self.ssh_out_checkbox = QCheckBox("SSH OUT")
        self.windows_in_checkbox.stateChanged.connect(self._on_windows_in_state_changed)
        self.windows_out_checkbox.stateChanged.connect(self._on_windows_out_state_changed)
        self.ssh_in_checkbox.stateChanged.connect(self._on_ssh_in_state_changed)
        self.ssh_out_checkbox.stateChanged.connect(self._on_ssh_out_state_changed)
        self.ssh_host_edit = QLineEdit(self._settings.ssh_host)
        self.ssh_host_edit.setPlaceholderText("IP / hostname")
        self.ssh_port_spin = QSpinBox()
        self.ssh_port_spin.setRange(1, 65535)
        self.ssh_port_spin.setValue(self._settings.ssh_port)
        self.ssh_user_edit = QLineEdit(self._settings.ssh_user or "root")
        self.ssh_key_edit = QLineEdit(self._settings.ssh_key_path)
        self.ssh_key_button = QPushButton("Vybrat")
        self.ssh_key_button.clicked.connect(self._browse_ssh_key)
        self.ssh_password_edit = QLineEdit(self._settings.ssh_password)
        self.ssh_password_edit.setEchoMode(QLineEdit.Password)
        self.in_dir_button = QPushButton("VSTUP")
        self.in_dir_button.clicked.connect(self._pick_in_dir)
        self.in_dir_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.out_dir_button = QPushButton("Výstup")
        self.out_dir_button.clicked.connect(self._pick_out_dir)
        self.out_dir_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.in_equals_out_button = QPushButton("IN=OUT")
        self.in_equals_out_button.clicked.connect(self._on_in_equals_out)
        self.in_equals_out_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.versing_button = QPushButton("VERSING")
        self.versing_button.setCheckable(True)
        self.versing_button.setEnabled(False)
        self.versing_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.versing_button.toggled.connect(self._on_versing_toggled)
        self.api_key_button = QPushButton("API-KEY")
        self.api_key_button.clicked.connect(self._open_api_key_dialog)
        self.pricing_button = QPushButton("$")
        self.pricing_button.clicked.connect(self._show_pricing)
        self.settings_button = QPushButton("NASTAVENÍ")
        self.settings_button.clicked.connect(self._open_settings)
        self.save_button = QPushButton("SAVE")
        self.save_button.clicked.connect(self._on_save_state)
        self.load_button = QPushButton("LOAD")
        self.load_button.clicked.connect(self._on_load_state)
        self.load_request_button = QPushButton("LOAD REQUEST")
        self.load_request_button.clicked.connect(self._on_load_request)
        self.new_button = QPushButton("NEW")
        self.new_button.clicked.connect(self._on_new_clicked)
        self.exit_button = QPushButton("EXIT")
        self.exit_button.setProperty("danger", True)
        self.exit_button.clicked.connect(self._on_exit_clicked)
        for control in (
            self.api_key_button,
            self.pricing_button,
            self.settings_button,
            self.save_button,
            self.load_button,
            self.load_request_button,
            self.new_button,
        ):
            control.setCursor(QCursor(Qt.PointingHandCursor))
            control.setMinimumSize(0, 0)
        self.exit_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.exit_button.setMinimumSize(0, 0)
        self.in_dir_edit.textChanged.connect(self._on_dir_content_changed)
        self.out_dir_edit.textChanged.connect(self._on_dir_content_changed)
        self.get_models_button.clicked.connect(self._on_fetch_models)
        self.go_button.clicked.connect(self._on_go_clicked)
        self._pricing_status_label = QLabel()
        self._pricing_status_label.setWordWrap(True)
        self._pricing_status_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._diag_warning_label = QLabel()
        self._diag_warning_label.setWordWrap(True)

    def _build_config_section(self) -> QWidget:
        self._init_controls()
        return QWidget()
        group = QGroupBox("Konfigurace")
        group_layout = QVBoxLayout(group)
        toolbar = QHBoxLayout()
        self.api_key_button = QPushButton("API-KEY")
        self.api_key_button.clicked.connect(self._open_api_key_dialog)
        self.pricing_button = QPushButton("$")
        self.pricing_button.clicked.connect(self._show_pricing)
        self.settings_button = QPushButton("NASTAVENÍ")
        self.settings_button.clicked.connect(self._open_settings)
        self.save_button = QPushButton("SAVE")
        self.save_button.clicked.connect(self._on_save_state)
        self.load_button = QPushButton("LOAD")
        self.load_button.clicked.connect(self._on_load_state)
        self.load_request_button = QPushButton("LOAD REQUEST")
        self.load_request_button.clicked.connect(self._on_load_request)
        self.exit_button = QPushButton("EXIT")
        self.exit_button.setProperty("danger", True)
        self.exit_button.clicked.connect(self._on_exit_clicked)
        self.new_button = QPushButton("NEW")
        self.new_button.clicked.connect(self._on_new_clicked)
        for control in (
            self.api_key_button,
            self.pricing_button,
            self.settings_button,
            self.save_button,
            self.load_button,
            self.load_request_button,
            self.new_button,
        ):
            control.setCursor(QCursor(Qt.PointingHandCursor))
        self.exit_button.setCursor(QCursor(Qt.PointingHandCursor))
        toolbar.addWidget(self.api_key_button)
        toolbar.addWidget(self.pricing_button)
        toolbar.addWidget(self.settings_button)
        toolbar.addWidget(self.save_button)
        toolbar.addWidget(self.load_button)
        toolbar.addWidget(self.load_request_button)
        toolbar.addStretch()
        toolbar.addWidget(self.exit_button)
        group_layout.addLayout(toolbar)
        layout = QGridLayout()
        layout.setColumnStretch(1, 1)
        self.project_name_edit = QLineEdit()
        self.prompt_edit = QPlainTextEdit()
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["GENERATE", "MODIFY", "QA"])
        self.mode_combo.setCurrentText("GENERATE")
        self.send_as_c_checkbox = QCheckBox("SEND AS C (BATCH)")
        self.in_dir_edit = QLineEdit()
        self.out_dir_edit = QLineEdit()
        self.response_id_edit = QLineEdit()
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("API Key")
        self.model_combo = QComboBox()
        self.model_combo.addItems(["gpt-4o", "gpt-4o-mini", "gpt-4o-mini-transcribe"])
        self.temperature_spin = QSpinBox()
        self.temperature_spin.setRange(0, 20)
        self.temperature_spin.setValue(2)
        self.temperature_spin.setSuffix(" ×0.1")
        self.get_models_button = QPushButton("GET MODELS")
        self.go_button = QPushButton("KÁJA GO")
        self.log_edit = QPlainTextEdit()
        self.log_edit.setReadOnly(True)
        self.windows_in_checkbox = QCheckBox("WINDOWS IN")
        self.windows_out_checkbox = QCheckBox("WINDOWS OUT")
        self.ssh_in_checkbox = QCheckBox("SSH IN")
        self.ssh_out_checkbox = QCheckBox("SSH OUT")
        self.windows_in_checkbox.stateChanged.connect(self._on_windows_in_state_changed)
        self.windows_out_checkbox.stateChanged.connect(self._on_windows_out_state_changed)
        self.ssh_in_checkbox.stateChanged.connect(self._on_ssh_in_state_changed)
        self.ssh_out_checkbox.stateChanged.connect(self._on_ssh_out_state_changed)
        self.ssh_host_edit = QLineEdit(self._settings.ssh_host)
        self.ssh_host_edit.setPlaceholderText("IP / hostname")
        self.ssh_port_spin = QSpinBox()
        self.ssh_port_spin.setRange(1, 65535)
        self.ssh_port_spin.setValue(self._settings.ssh_port)
        self.ssh_user_edit = QLineEdit(self._settings.ssh_user or "root")
        self.ssh_key_edit = QLineEdit(self._settings.ssh_key_path)
        self.ssh_key_button = QPushButton("Vybrat")
        self.ssh_key_button.clicked.connect(self._browse_ssh_key)
        self.ssh_password_edit = QLineEdit(self._settings.ssh_password)
        self.ssh_password_edit.setEchoMode(QLineEdit.Password)
        self.get_models_button.clicked.connect(self._on_fetch_models)
        self.go_button.clicked.connect(self._on_go_clicked)
        layout.addWidget(QLabel("Název projektu"), 0, 0)
        layout.addWidget(self.project_name_edit, 0, 1)
        layout.addWidget(QLabel("MODE / režim"), 1, 0)
        layout.addWidget(self.mode_combo, 1, 1)
        layout.addWidget(self.send_as_c_checkbox, 1, 2)
        layout.addWidget(QLabel("Prompt / specifikace"), 2, 0)
        layout.addWidget(self.prompt_edit, 2, 1, 1, 2)
        layout.addWidget(QLabel("In Adresář"), 3, 0)
        in_layout = QHBoxLayout()
        self.in_dir_button = QPushButton("VSTUP")
        self.in_dir_button.clicked.connect(self._pick_in_dir)
        self.in_dir_button.setCursor(QCursor(Qt.PointingHandCursor))
        in_layout.addWidget(self.in_dir_edit)
        in_layout.addWidget(self.in_dir_button)
        layout.addLayout(in_layout, 3, 1)
        layout.addWidget(QLabel("Out Adresář"), 3, 2)
        out_layout = QHBoxLayout()
        self.out_dir_button = QPushButton("Výstup")
        self.out_dir_button.clicked.connect(self._pick_out_dir)
        self.out_dir_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.in_equals_out_button = QPushButton("IN=OUT")
        self.in_equals_out_button.clicked.connect(self._on_in_equals_out)
        self.in_equals_out_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.versing_button = QPushButton("VERSING")
        self.versing_button.setCheckable(True)
        self.versing_button.setEnabled(False)
        self.versing_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.versing_button.toggled.connect(self._on_versing_toggled)
        self.in_dir_edit.textChanged.connect(self._on_dir_content_changed)
        self.out_dir_edit.textChanged.connect(self._on_dir_content_changed)
        out_layout.addWidget(self.out_dir_edit)
        out_layout.addWidget(self.out_dir_button)
        out_layout.addWidget(self.in_equals_out_button)
        out_layout.addWidget(self.versing_button)
        layout.addLayout(out_layout, 3, 3)
        layout.addWidget(QLabel("Response ID"), 4, 0)
        layout.addWidget(self.response_id_edit, 4, 1)
        layout.addWidget(QLabel("Model"), 4, 2)
        layout.addWidget(self.model_combo, 4, 3)
        layout.addWidget(QLabel("API Key"), 5, 0)
        layout.addWidget(self.api_key_edit, 5, 1)
        layout.addWidget(QLabel("Temperature"), 5, 2)
        layout.addWidget(self.temperature_spin, 5, 3)
        self._pricing_status_label = QLabel()
        self._pricing_status_label.setWordWrap(True)
        self._pricing_status_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self._pricing_status_label, 5, 4, 1, 4)
        layout.addWidget(self.windows_in_checkbox, 6, 0)
        layout.addWidget(self.windows_out_checkbox, 6, 1)
        layout.addWidget(self.ssh_in_checkbox, 6, 2)
        layout.addWidget(self.ssh_out_checkbox, 6, 3)
        self._diag_warning_label = QLabel()
        self._diag_warning_label.setWordWrap(True)
        layout.addWidget(self._diag_warning_label, 7, 0, 1, 4)
        ssh_group = QGroupBox("SSH cíl")
        ssh_layout = QGridLayout(ssh_group)
        ssh_layout.setColumnStretch(1, 1)
        ssh_layout.addWidget(QLabel("Host / IP"), 0, 0)
        ssh_layout.addWidget(self.ssh_host_edit, 0, 1)
        ssh_layout.addWidget(QLabel("Port"), 0, 2)
        ssh_layout.addWidget(self.ssh_port_spin, 0, 3)
        ssh_layout.addWidget(QLabel("Uživatel"), 1, 0)
        ssh_layout.addWidget(self.ssh_user_edit, 1, 1)
        key_layout = QHBoxLayout()
        key_layout.setContentsMargins(0, 0, 0, 0)
        key_layout.addWidget(self.ssh_key_edit)
        key_layout.addWidget(self.ssh_key_button)
        ssh_layout.addWidget(QLabel("SSH klíč"), 2, 0)
        ssh_layout.addLayout(key_layout, 2, 1, 1, 3)
        ssh_layout.addWidget(QLabel("SSH heslo"), 3, 0)
        ssh_layout.addWidget(self.ssh_password_edit, 3, 1)
        layout.addWidget(ssh_group, 8, 0, 1, 6)
        layout.addWidget(self.get_models_button, 9, 2)
        layout.addWidget(self.go_button, 9, 3)
        layout.addWidget(QLabel("Log"), 10, 0)
        layout.addWidget(self.log_edit, 10, 1, 1, 3)
        group_layout.addLayout(layout)
        return group

    def _build_header(self) -> QWidget:
        header = QFrame()
        header.setObjectName("app_header")
        header.setFrameShape(QFrame.StyledPanel)
        header.setStyleSheet(
            "QFrame#app_header { border:2px solid #fff; background:#020202; border-radius:12px; }"
        )
        layout = QVBoxLayout(header)
        layout.setContentsMargins(24, 12, 24, 12)
        layout.setSpacing(10)

        title_block = QWidget()
        title_layout = QVBoxLayout(title_block)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(2)
        title_label = QLabel("KÁJOVO")
        title_font = QFont("Montserrat", 28, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        version_label = QLabel(f"v{__version__}")
        version_font = QFont("Montserrat", 14, QFont.Bold)
        version_label.setFont(version_font)
        version_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title_label)
        title_layout.addWidget(version_label)

        controls_row = QWidget()
        controls_layout = QHBoxLayout(controls_row)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(10)
        for control in (
            self.settings_button,
            self.pricing_button,
            self.save_button,
            self.load_button,
            self.load_request_button,
            self.api_key_button,
            self.new_button,
        ):
            controls_layout.addWidget(control)
        controls_layout.addStretch(1)
        controls_layout.addWidget(self.exit_button)

        layout.addWidget(title_block)
        layout.addWidget(controls_row)
        layout.addWidget(self._status_bar)
        return header

    def _build_workspace(self) -> QWidget:
        sections = [
            SectionDefinition("zadani", "ZADÁNÍ", self._build_assignment_section),
            SectionDefinition("attached_files", "PŘIPOJENÉ SOUBORY", self._build_attached_files_widget),
            SectionDefinition("in_dir", "IN", self._build_in_section),
            SectionDefinition("out_dir", "OUT", self._build_out_section),
            SectionDefinition(
                "diagnostics",
                "DIAGNOSTICS (WINDOWS / SSH)",
                self._build_diagnostics_section,
            ),
            SectionDefinition("model_openai", "MODEL OPENAI", self._build_model_section),
            SectionDefinition("batch_monitor", "BATCH MONITOR", self._build_batch_monitor_widget),
            SectionDefinition("go", "GO", self._build_go_section),
            SectionDefinition("answer", "ANSWARE", self._build_answare_section),
            SectionDefinition("local_files", "LOCAL FILES", self._build_local_files_widget),
            SectionDefinition("file_api", "FILE API", self._build_file_api_widget),
            SectionDefinition("vector_stores", "VECTOR STORES", self._build_vector_store_widget),
            SectionDefinition("timeline", "TIMELINE", self._build_timeline_widget),
            SectionDefinition("diff_viewer", "DIFF VIEWER", self._build_diff_view_widget),
        ]
        return WorkspacePane(sections)

    def _build_assignment_section(self) -> QWidget:
        box = QWidget()
        layout = QVBoxLayout(box)
        layout.addWidget(QLabel("Název projektu"))
        layout.addWidget(self.project_name_edit)
        layout.addWidget(QLabel("Prompt / specifikace"))
        layout.addWidget(self.prompt_edit)
        return box

    def _build_in_section(self) -> QWidget:
        box = QWidget()
        layout = QVBoxLayout(box)
        layout.addWidget(QLabel("In adresář"))
        row = QHBoxLayout()
        row.addWidget(self.in_dir_edit)
        row.addWidget(self.in_dir_button)
        layout.addLayout(row)
        return box

    def _build_out_section(self) -> QWidget:
        box = QWidget()
        layout = QVBoxLayout(box)
        layout.addWidget(QLabel("Out adresář"))
        row = QHBoxLayout()
        row.addWidget(self.out_dir_edit)
        row.addWidget(self.out_dir_button)
        row.addWidget(self.in_equals_out_button)
        row.addWidget(self.versing_button)
        layout.addLayout(row)
        return box

    def _build_model_section(self) -> QWidget:
        box = QWidget()
        layout = QVBoxLayout(box)
        layout.addWidget(QLabel("Model"))
        layout.addWidget(self.model_combo)
        layout.addWidget(QLabel("Temperature"))
        layout.addWidget(self.temperature_spin)
        layout.addWidget(self.get_models_button)
        layout.addWidget(QLabel("API Key"))
        layout.addWidget(self.api_key_edit)
        layout.addWidget(self._pricing_status_label)
        return box

    def _build_go_section(self) -> QWidget:
        box = QWidget()
        layout = QVBoxLayout(box)
        layout.addWidget(QLabel("MODE / režim"))
        layout.addWidget(self.mode_combo)
        layout.addWidget(self.send_as_c_checkbox)
        layout.addWidget(QLabel("Response ID"))
        layout.addWidget(self.response_id_edit)
        layout.addWidget(self.go_button)
        layout.addWidget(QLabel("Log"))
        layout.addWidget(self.log_edit)
        return box

    def _build_diagnostics_section(self) -> QWidget:
        box = QWidget()
        layout = QVBoxLayout(box)
        row = QHBoxLayout()
        row.addWidget(self.windows_in_checkbox)
        row.addWidget(self.windows_out_checkbox)
        row.addWidget(self.ssh_in_checkbox)
        row.addWidget(self.ssh_out_checkbox)
        layout.addLayout(row)
        layout.addWidget(self._diag_warning_label)
        ssh_group = QGroupBox("SSH cíl")
        ssh_layout = QGridLayout(ssh_group)
        ssh_layout.setColumnStretch(1, 1)
        ssh_layout.addWidget(QLabel("Host / IP"), 0, 0)
        ssh_layout.addWidget(self.ssh_host_edit, 0, 1)
        ssh_layout.addWidget(QLabel("Port"), 0, 2)
        ssh_layout.addWidget(self.ssh_port_spin, 0, 3)
        ssh_layout.addWidget(QLabel("Uživatel"), 1, 0)
        ssh_layout.addWidget(self.ssh_user_edit, 1, 1)
        key_layout = QHBoxLayout()
        key_layout.setContentsMargins(0, 0, 0, 0)
        key_layout.addWidget(self.ssh_key_edit)
        key_layout.addWidget(self.ssh_key_button)
        ssh_layout.addWidget(QLabel("SSH klíč"), 2, 0)
        ssh_layout.addLayout(key_layout, 2, 1, 1, 3)
        ssh_layout.addWidget(QLabel("SSH heslo"), 3, 0)
        ssh_layout.addWidget(self.ssh_password_edit, 3, 1)
        layout.addWidget(ssh_group)
        return box

    def _build_local_files_widget(self) -> QWidget:
        box = QWidget()
        layout = QVBoxLayout(box)
        layout.addWidget(self._local_files_table)
        buttons = QHBoxLayout()
        add_button = QPushButton("VLOŽ")
        add_button.clicked.connect(self._add_local_files)
        upload_button = QPushButton("UPLOAD")
        upload_button.clicked.connect(self._upload_local_files)
        buttons.addWidget(add_button)
        buttons.addWidget(upload_button)
        buttons.addStretch()
        layout.addLayout(buttons)
        return box

    def _ensure_api_key_loaded(self) -> None:
        if self.api_key_edit.text().strip():
            return
        key = os.environ.get("OPENAI_API_KEY")
        if key:
            self.api_key_edit.setText(key)
            return
        reg_key = self._read_user_env("OPENAI_API_KEY")
        if not reg_key:
            reg_key = self._read_machine_env("OPENAI_API_KEY")
        if reg_key:
            os.environ["OPENAI_API_KEY"] = reg_key
            self.api_key_edit.setText(reg_key)

    def _read_user_env(self, name: str) -> str | None:
        return self._read_registry_value(winreg.HKEY_CURRENT_USER, name)

    def _read_machine_env(self, name: str) -> str | None:
        return self._read_registry_value(
            winreg.HKEY_LOCAL_MACHINE,
            name,
            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
        )

    def _read_registry_value(
        self,
        root: int,
        name: str,
        subkey: str | None = "Environment",
    ) -> str | None:
        if not winreg:
            return None
        lookup = subkey or "Environment"
        try:
            with winreg.OpenKey(root, lookup) as handle:
                value, _ = winreg.QueryValueEx(handle, name)
        except OSError:
            return None
        return value

    def _is_connection_error(self, exc: Exception) -> bool:
        text = str(exc).lower()
        return "connection error" in text or "connect error" in text

    def _read_user_env(self, name: str) -> str | None:
        if not winreg:
            return None
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as handle:
                value, _ = winreg.QueryValueEx(handle, name)
        except OSError:
            return None
        return value

    def _build_sections_area(self) -> QWidget:
        container = QWidget()
        flow = FlowLayout(container, spacing=18)
        flow.addWidget(SectionCard("BATCH MONITOR", self._build_batch_monitor_widget()))
        flow.addWidget(SectionCard("TIMELINE", self._build_timeline_widget()))
        flow.addWidget(SectionCard("DIFF VIEWER", self._build_diff_view_widget()))
        flow.addWidget(SectionCard("PŘIPOJENÉ SOUBORY", self._build_attached_files_widget()))
        flow.addWidget(SectionCard("FILE API", self._build_file_api_widget()))
        flow.addWidget(SectionCard("VECTOR STORES", self._build_vector_store_widget()))
        wrapper = QScrollArea()
        wrapper.setWidgetResizable(True)
        wrapper.setWidget(container)
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(wrapper)
        return widget

    def _build_batch_monitor_widget(self) -> QWidget:
        box = QWidget()
        layout = QVBoxLayout(box)
        refresh_button = QPushButton("REFRESH")
        refresh_button.clicked.connect(self._refresh_batch_monitor)
        layout.addWidget(refresh_button)
        layout.addWidget(self._batch_table)
        return box

    def _build_timeline_widget(self) -> QWidget:
        box = QWidget()
        layout = QVBoxLayout(box)
        header = QHBoxLayout()
        header.addWidget(QLabel("Run timeline"))
        header.addStretch()
        self._timeline_export_button = QPushButton("EXPORT")
        self._timeline_export_button.clicked.connect(self._on_export_timeline)
        self._timeline_export_button.setCursor(QCursor(Qt.PointingHandCursor))
        header.addWidget(self._timeline_export_button)
        layout.addLayout(header)
        self._timeline_table = QTableWidget(0, 4)
        self._timeline_table.setHorizontalHeaderLabels(
            ["Step", "Result", "Duration", "Details"]
        )
        self._timeline_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._timeline_table.horizontalHeader().setMinimumSectionSize(0)
        layout.addWidget(self._timeline_table)
        self._timeline_status_label = QLabel("Žádná data.")
        layout.addWidget(self._timeline_status_label)
        return box

    def _build_diff_view_widget(self) -> QWidget:
        box = QWidget()
        layout = QVBoxLayout(box)
        header = QHBoxLayout()
        header.addWidget(QLabel("IN ↔ OUT diff"))
        header.addStretch()
        refresh_button = QPushButton("REFRESH")
        refresh_button.setCursor(QCursor(Qt.PointingHandCursor))
        refresh_button.clicked.connect(lambda: self._refresh_diff_view(self._last_run_ui_state))
        header.addWidget(refresh_button)
        layout.addLayout(header)
        layout.addWidget(self._diff_status_label)
        layout.addWidget(self._diff_view)
        return box

    def _build_attached_files_widget(self) -> QWidget:
        box = QWidget()
        layout = QVBoxLayout(box)
        controls = QHBoxLayout()
        add_button = QPushButton("PŘIDEJ")
        add_button.clicked.connect(self._add_attachment)
        remove_button = QPushButton("ODSTRAŇ")
        remove_button.clicked.connect(self._remove_attachment)
        controls.addWidget(add_button)
        controls.addWidget(remove_button)
        controls.addStretch()
        layout.addLayout(controls)
        layout.addWidget(self._attached_table)
        return box

    def _build_file_api_widget(self) -> QWidget:
        box = QWidget()
        layout = QVBoxLayout(box)
        controls = QHBoxLayout()
        attach_button = QPushButton("PŘIPOJ")
        attach_button.clicked.connect(self._attach_selected_file_api)
        delete_button = QPushButton("SMAŽ")
        delete_button.clicked.connect(self._delete_selected_file_api)
        delete_all_button = QPushButton("DEL ALL")
        delete_all_button.clicked.connect(self._delete_all_file_api)
        controls.addWidget(attach_button)
        controls.addWidget(delete_button)
        controls.addWidget(delete_all_button)
        controls.addStretch()
        layout.addLayout(controls)
        layout.addWidget(self._file_api_table)
        return box

    def _build_vector_store_widget(self) -> QWidget:
        box = QWidget()
        layout = QVBoxLayout(box)
        refresh_button = QPushButton("REFRESH")
        refresh_button.clicked.connect(self._refresh_vector_store_view)
        add_file_button = QPushButton("PŘIDEJ SOUBOR")
        add_file_button.clicked.connect(self._add_file_to_vector_store)
        remove_button = QPushButton("ODSTRAŇ SOUBOR")
        remove_button.clicked.connect(self._remove_file_from_vector_store)
        expiry_layout = QHBoxLayout()
        self._expiry_edit = QLineEdit()
        expiry_button = QPushButton("SET EXPIRY")
        expiry_button.clicked.connect(self._set_vector_expiry)
        expiry_layout.addWidget(self._expiry_edit)
        expiry_layout.addWidget(expiry_button)
        layout.addWidget(refresh_button)
        layout.addWidget(self._vector_list)
        layout.addWidget(self._vector_detail)
        layout.addWidget(add_file_button)
        layout.addWidget(remove_button)
        layout.addLayout(expiry_layout)
        self._vector_detail.setReadOnly(True)
        self._vector_list.currentRowChanged.connect(lambda _: self._update_vector_detail())
        return box

    def _build_answare_section(self) -> QWidget:
        group = QGroupBox("ANSWARE")
        layout = QVBoxLayout(group)
        self._answare_view.setReadOnly(True)
        button_layout = QHBoxLayout()
        copy_button = QPushButton("CTRL+C")
        copy_button.clicked.connect(self._copy_answare)
        response_button = QPushButton("RESPONSE")
        response_button.clicked.connect(self._copy_response_id)
        script_button = QPushButton("SCRIPT")
        script_button.clicked.connect(self._run_script_workflow)
        button_layout.addWidget(copy_button)
        button_layout.addWidget(response_button)
        button_layout.addWidget(script_button)
        button_layout.addStretch()
        layout.addWidget(self._answare_view)
        layout.addLayout(button_layout)
        return group

    def _create_batch_table(self) -> QTableWidget:
        table = QTableWidget(0, 5)
        table.setHorizontalHeaderLabels(["Run", "Status", "Started", "Duration", "Akce"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.horizontalHeader().setMinimumSectionSize(0)
        table.setMinimumSize(0, 0)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return table

    def _create_file_table(self, headers: List[str]) -> QTableWidget:
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.horizontalHeader().setMinimumSectionSize(0)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setSelectionMode(QTableWidget.MultiSelection)
        table.verticalHeader().hide()
        table.setMinimumSize(0, 0)
        table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        return table

    def _refresh_local_files_table(self) -> None:
        table = self._local_files_table
        table.setRowCount(0)
        for path in self._local_files:
            row = table.rowCount()
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(path.name))
            table.setItem(row, 1, QTableWidgetItem(str(path)))
            remove_button = QPushButton("X")
            remove_button.clicked.connect(lambda _, p=path: self._remove_local_file(p))
            table.setCellWidget(row, 2, remove_button)

    def _add_local_files(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(self, "Vyberte soubory")
        if not paths:
            return
        for raw in paths:
            path = Path(raw)
            if path not in self._local_files:
                self._local_files.append(path)
        self._refresh_local_files_table()

    def _remove_local_file(self, path: Path) -> None:
        self._local_files = [item for item in self._local_files if item != path]
        self._refresh_local_files_table()

    def _upload_local_files(self) -> None:
        if not self._local_files:
            self._append_log("LOCAL FILES: žádné soubory k uploadu.")
            return
        key = os.environ.get("OPENAI_API_KEY") or self.api_key_edit.text().strip()
        if not key:
            QMessageBox.warning(self, "API key", "API key je povinný pro upload.")
            return
        if not self._openai_client:
            try:
                self._openai_client = OpenAIClient(key)
            except Exception as exc:
                QMessageBox.warning(self, "OpenAI", str(exc))
                return
        uploaded = []
        for path in list(self._local_files):
            try:
                response = self._openai_client.upload_file(path, "user data")
                record = FileRecord(
                    file_id=response.get("id") or response.get("file_id") or str(uuid.uuid4())[:8],
                    filename=response.get("filename") or path.name,
                    purpose=response.get("purpose") or "user data",
                    size_bytes=int(response.get("bytes") or path.stat().st_size),
                )
                self._file_api_records.append(record)
                uploaded.append(path.name)
            except Exception as exc:
                self._append_log(f"LOCAL FILES: upload {path} selhal: {exc}")
        if uploaded:
            self._append_log(f"LOCAL FILES: upload dokončen ({len(uploaded)}).")
        self._refresh_file_api_table()
        self._local_files.clear()
        self._refresh_local_files_table()

    def _add_attachment(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(self, "Vyberte soubory")
        for path in paths:
            record = FileRecord(
                file_id=f"ATT_{uuid.uuid4().hex[:6]}",
                filename=path,
                purpose="user data",
                size_bytes=Path(path).stat().st_size if Path(path).exists() else 0,
            )
            self._attached_files.append(record)
        self._refresh_attached_table()

    def _remove_attachment(self) -> None:
        for item in list(self._attached_table.selectedItems()):
            row = item.row()
            if row < len(self._attached_files):
                self._attached_files.pop(row)
        self._refresh_attached_table()

    def _attach_selected_file_api(self) -> None:
        selected_rows = {item.row() for item in self._file_api_table.selectedItems()}
        for row in sorted(selected_rows, reverse=True):
            if row < len(self._file_api_records):
                record = self._file_api_records.pop(row)
                self._attached_files.append(record)
        self._refresh_file_api_table()
        self._refresh_attached_table()

    def _delete_selected_file_api(self) -> None:
        selected_rows = sorted({item.row() for item in self._file_api_table.selectedItems()}, reverse=True)
        for row in selected_rows:
            if row < len(self._file_api_records):
                self._file_api_records.pop(row)
        self._refresh_file_api_table()

    def _delete_all_file_api(self) -> None:
        self._file_api_records.clear()
        self._refresh_file_api_table()

    def _refresh_batch_monitor(self) -> None:
        self._batch_table.setRowCount(0)
        entries = self._load_run_index_entries()
        self._batch_jobs = entries[:5]
        for job in self._batch_jobs:
            row = self._batch_table.rowCount()
            self._batch_table.insertRow(row)
            run_label = job.get("run_id", "run")
            project = job.get("project")
            mode = job.get("mode")
            run_text = f"{run_label}"
            if project:
                run_text += f" • {project}"
            if mode:
                run_text += f" • {mode}"
            self._batch_table.setItem(row, 0, QTableWidgetItem(run_text))
            self._batch_table.setItem(row, 1, QTableWidgetItem(job.get("status", "unknown")))
            self._batch_table.setItem(row, 2, QTableWidgetItem(job.get("start", "-")))
            duration = job.get("duration_s", 0.0) or 0.0
            self._batch_table.setItem(row, 3, QTableWidgetItem(f"{duration:.2f}s"))
            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            download = QPushButton("DOWNLOAD")
            download.clicked.connect(lambda _, entry=job: self._on_batch_download(entry))
            open_log = QPushButton("OPEN LOG")
            open_log.clicked.connect(lambda _, entry=job: self._on_batch_open_log(entry))
            cancel = QPushButton("CANCEL")
            cancel.clicked.connect(lambda _, entry=job: self._on_batch_cancel(entry))
            for widget in (download, open_log, cancel):
                widget.setCursor(QCursor(Qt.PointingHandCursor))
                actions_layout.addWidget(widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            self._batch_table.setCellWidget(row, 4, actions)

    def _load_run_index_entries(self) -> List[Dict[str, Any]]:
        index_path = self._root_dir / "LOG" / "run_index.json"
        if not index_path.exists():
            return []
        try:
            raw = json.loads(index_path.read_text(encoding="utf-8"))
            if isinstance(raw, list):
                return list(reversed(raw))
        except Exception:
            pass
        return []

    def _on_batch_download(self, entry: Dict[str, Any]) -> None:
        path = entry.get("manifest")
        if not path:
            QMessageBox.information(self, "DOWNLOAD", "Neexistuje manifest.")
            return
        self._safe_open_path(path, "DOWNLOAD")

    def _on_batch_open_log(self, entry: Dict[str, Any]) -> None:
        path = entry.get("log_dir")
        if not path:
            QMessageBox.information(self, "OPEN LOG", "Log adresář chybí.")
            return
        self._safe_open_path(path, "OPEN LOG")

    def _on_batch_cancel(self, entry: Dict[str, Any]) -> None:
        run_id = entry.get("run_id", "unknown")
        self._append_log(f"CANCEL {run_id}")
        QMessageBox.information(self, "CANCEL", f"Běh {run_id} nelze rušit.")

    def _safe_open_path(self, path: str, title: str) -> None:
        candidate = Path(path)
        if not candidate.is_absolute():
            candidate = self._root_dir / path
        if not candidate.exists():
            QMessageBox.warning(self, title, f"Soubor neexistuje: {candidate}")
            return
        try:
            os.startfile(str(candidate))
        except AttributeError:
            QMessageBox.information(self, title, f"Otevřete: {candidate}")
        except OSError:
            QMessageBox.warning(self, title, f"Nepodařilo se otevřít: {candidate}")

    def _refresh_attached_table(self) -> None:
        self._attached_table.setRowCount(0)
        for record in self._attached_files:
            row = self._attached_table.rowCount()
            self._attached_table.insertRow(row)
            self._attached_table.setItem(row, 0, QTableWidgetItem(record.filename))
            self._attached_table.setItem(row, 1, QTableWidgetItem(record.purpose))
            self._attached_table.setItem(row, 2, QTableWidgetItem(f"{record.size_bytes} B"))

    def _refresh_file_api_table(self) -> None:
        self._file_api_table.setRowCount(0)
        for record in self._file_api_records:
            row = self._file_api_table.rowCount()
            self._file_api_table.insertRow(row)
            self._file_api_table.setItem(row, 0, QTableWidgetItem(record.file_id))
            self._file_api_table.setItem(row, 1, QTableWidgetItem(record.filename))
            self._file_api_table.setItem(row, 2, QTableWidgetItem(record.purpose))
            self._file_api_table.setItem(row, 3, QTableWidgetItem(f"{record.size_bytes} B"))

    def _refresh_vector_store_view(self) -> None:
        self._vector_list.clear()
        for store in self._vector_stores:
            self._vector_list.addItem(f"{store.store_id} – {store.name}")
        self._update_vector_detail()

    def _on_vector_selection_changed(self) -> None:
        self._update_vector_detail()

    def _update_vector_detail(self) -> None:
        current = self._vector_list.currentRow()
        if current < 0 or current >= len(self._vector_stores):
            self._vector_detail.setPlainText("")
            return
        store = self._vector_stores[current]
        files = self._vector_store_files.get(store.store_id, [])
        detail = {
            "store_id": store.store_id,
            "name": store.name,
            "expires_at": store.expires_at,
            "files": files,
        }
        self._vector_detail.setPlainText(json.dumps(detail, indent=2, ensure_ascii=False))

    def _add_file_to_vector_store(self) -> None:
        current = self._vector_list.currentRow()
        if current < 0 or not self._file_api_records:
            return
        store = self._vector_stores[current]
        record = self._file_api_records.pop(0)
        self._vector_store_files.setdefault(store.store_id, []).append(record.filename)
        self._append_log(f"Přidáno {record.filename} do {store.store_id}")
        self._refresh_file_api_table()
        self._update_vector_detail()

    def _remove_file_from_vector_store(self) -> None:
        current = self._vector_list.currentRow()
        if current < 0:
            return
        store = self._vector_stores[current]
        files = self._vector_store_files.get(store.store_id, [])
        if files:
            popped = files.pop()
            self._append_log(f"Odebráno {popped} z {store.store_id}")
        self._update_vector_detail()

    def _set_vector_expiry(self) -> None:
        value = self._expiry_edit.text().strip()
        current = self._vector_list.currentRow()
        if current < 0 or not value:
            return
        store = self._vector_stores[current]
        store.expires_at = value
        self._append_log(f"Nastaveno {value} pro {store.store_id}")
        self._update_vector_detail()

    def _on_fetch_models(self) -> None:
        self._append_log("GET MODELS triggered")
        models = ["gpt-4o", "gpt-4o-mini", "gpt-4o-mini-transcribe"]
        self.model_combo.clear()
        self.model_combo.addItems(models)
        self._append_log("Modely aktualizovány")

    def _on_go_clicked(self) -> None:
        mode = "C" if self.send_as_c_checkbox.isChecked() else self.mode_combo.currentText()
        validation = self._validate_inputs(mode)
        if validation:
            QMessageBox.warning(self, "Chyba validace", "\n".join(validation))
            return
        if not self._ensure_diagnostics_prereq():
            return
        ui_state = self._build_ui_state(mode)
        self._last_run_ui_state = ui_state
        if not self.api_key_edit.text().strip():
            QMessageBox.warning(self, "Chyba", "API key je povinný")
            return
        request_snapshot = self._build_request_snapshot(ui_state)
        run_artifacts = init_run(self._root_dir)
        response_id = PipelineExecutor.generate_response_id(mode)
        ui_state_log = log_ui_state(run_artifacts, ui_state, response_id=response_id)
        executor = PipelineExecutor(
            self._root_dir,
            run_artifacts,
            self._append_log,
            settings=self._settings,
            client=self._openai_client,
            initial_logs=[(ui_state_log, "ui_state")],
            security_policy=self._security_policy_for("diagnostics"),
            dry_run_confirmation=self._on_dry_run_summary,
        )
        attachments = [Path(record.filename) for record in self._attached_files]
        vector_ids = [store.store_id for store in self._vector_stores]
        self._progress_dialog = ProgressDialog(self)
        self._progress_dialog.stop_requested_changed.connect(lambda _: self._append_log("STOP requested"))
        self._progress_dialog.show()
        self._status_bar.start_progress("Pipeline připravena")
        idle_message = "PROGRAM NIC NEDĚLÁ"

        try:
            result = executor.execute(
                mode=mode,
                ui_state=ui_state,
                user_spec=self.prompt_edit.toPlainText(),
                attachments=attachments,
                vector_store_ids=vector_ids,
                response_id=response_id,
                progress_callback=self._on_pipeline_progress,
                stop_check=lambda: self._progress_dialog.stop_requested if self._progress_dialog else False,
                request_snapshot=request_snapshot,
            )
            self._handle_pipeline_result(result)
        except PipelineCancelled:
            self._append_log("Pipeline přerušena")
            idle_message = "PIPELINE PŘERUŠENA"
        except Exception as exc:  # pragma: no cover - failure paths
            QMessageBox.critical(self, "Chyba běhu", str(exc))
            idle_message = "CHYBA BĚHU"
        finally:
            if self._progress_dialog:
                self._progress_dialog.close()
                self._progress_dialog = None
            self._status_bar.mark_idle(idle_message)

    def _on_new_clicked(self) -> None:
        self._append_log("Nový projekt připraven.")

    def _on_exit_clicked(self) -> None:
        if not self.close():
            self._append_log("Zavření okna bylo zrušeno.")

    def _on_pipeline_progress(self, message: str, ratio: float) -> None:
        self._status_bar.update_progress(message, ratio)
        if self._progress_dialog:
            self._progress_dialog.update_progress(message, ratio)
        QApplication.processEvents()

    def _handle_pipeline_result(self, result: PipelineResult) -> None:
        self._last_response_id = result.response_id
        self._last_response_text = f"Režim: {result.mode}\nOdeslané soubory: {len(result.files_written)}"
        self._answare_view.setPlainText(f"Response ID: {result.response_id}\n{self._last_response_text}")
        self.response_id_edit.setText(result.response_id)
        self._append_log(f"Pipeline {result.mode} dokončen")
        self._last_timeline_log = result.timeline_log
        self._update_timeline_view(result.timeline or [])
        self._refresh_batch_monitor()
        self._refresh_diff_view(self._last_run_ui_state)

    def _update_timeline_view(self, entries: List[Dict[str, Any]]) -> None:
        self._timeline_table.setRowCount(0)
        for entry in entries:
            row = self._timeline_table.rowCount()
            self._timeline_table.insertRow(row)
            self._timeline_table.setItem(row, 0, QTableWidgetItem(entry.get("step", "")))
            self._timeline_table.setItem(row, 1, QTableWidgetItem(entry.get("result", "")))
            duration = entry.get("duration_s", 0.0) or 0.0
            self._timeline_table.setItem(row, 2, QTableWidgetItem(f"{duration:.2f}s"))
            details = {
                "details": entry.get("details"),
                "ids": entry.get("ids"),
            }
            details_text = json.dumps({k: v for k, v in details.items() if v}, ensure_ascii=False)
            self._timeline_table.setItem(row, 3, QTableWidgetItem(details_text))
        self._timeline_entries = entries
        self._timeline_status_label.setText(f"Poslední timeline ({len(entries)} kroků)")

    def _refresh_diff_view(self, ui_state: UiState | None) -> None:
        if not ui_state:
            self._diff_status_label.setText("Diff viewer čeká na běh.")
            self._diff_view.setPlainText("Spusťte pipeline pro získání diffu.")
            return
        in_dir = ui_state.in_dir.strip()
        out_dir = ui_state.out_dir.strip()
        if not in_dir or not out_dir:
            self._diff_status_label.setText("Diff vyžaduje oba adresáře (IN i OUT).")
            self._diff_view.setPlainText("Nastavte IN i OUT adresář a spusťte pipeline.")
            return
        in_path = Path(in_dir)
        out_path = Path(out_dir)
        in_exists = in_path.exists()
        out_exists = out_path.exists()
        if not in_exists or not out_exists:
            status = "Diff nelze vytvořit (adresář neexistuje)."
            self._diff_status_label.setText(status)
            self._diff_view.setPlainText(
                f"IN existuje: {in_exists}; OUT existuje: {out_exists}"
            )
            return
        in_files = self._collect_directory_files(in_path)
        out_files = self._collect_directory_files(out_path)
        only_in = sorted(set(in_files) - set(out_files))
        only_out = sorted(set(out_files) - set(in_files))
        diff_lines: List[str] = []
        changed = 0
        max_lines = 1200
        for rel in sorted(set(in_files) & set(out_files)):
            in_lines = self._read_file_lines(in_files[rel])
            out_lines = self._read_file_lines(out_files[rel])
            chunk = list(
                difflib.unified_diff(
                    in_lines,
                    out_lines,
                    fromfile=f"IN/{rel}",
                    tofile=f"OUT/{rel}",
                    lineterm="",
                )
            )
            if chunk:
                changed += 1
                diff_lines.append(f"--- Diff: {rel}")
                diff_lines.extend(chunk)
                if len(diff_lines) > max_lines:
                    diff_lines.append("... diff přerušen, výstup zkrácen ...")
                    break
        summary_lines: List[str] = []
        if only_in:
            summary_lines.append("+++ Jen v IN:")
            summary_lines.extend(f"- {path}" for path in only_in[:20])
            if len(only_in) > 20:
                summary_lines.append(f"... +{len(only_in) - 20} dalších souborů")
        if only_out:
            summary_lines.append("+++ Jen v OUT:")
            summary_lines.extend(f"- {path}" for path in only_out[:20])
            if len(only_out) > 20:
                summary_lines.append(f"... +{len(only_out) - 20} dalších souborů")
        if not summary_lines and not diff_lines:
            diff_text = "Adresáře jsou identické."
        else:
            diff_text_parts = summary_lines.copy()
            if summary_lines and diff_lines:
                diff_text_parts.append("")
            diff_text_parts.extend(diff_lines)
            diff_text = "\n".join(diff_text_parts)
        total_files = len(set(in_files) | set(out_files))
        self._diff_status_label.setText(
            f"Diff: {total_files} souborů (changed {changed}, jen v IN {len(only_in)}, jen v OUT {len(only_out)})"
        )
        self._diff_view.setPlainText(diff_text)

    def _on_dry_run_summary(self, summary: Dict[str, Any]) -> bool:
        files = summary.get("files") or []
        risks = summary.get("risks") or []
        details: List[str] = []
        for entry in files[:25]:
            existing = "přepsaný" if entry.get("existing") else "nový"
            purpose = entry.get("purpose") or ""
            details.append(f"- {entry.get('path')} ({existing}) {purpose}")
        if len(files) > 25:
            details.append(f"... dalších {len(files) - 25} souborů")
        if risks:
            details.append("")
            details.append("Rizika:")
            for risk in risks[:10]:
                details.append(f"- {risk.get('path')}: {risk.get('reason')}")
            if len(risks) > 10:
                details.append(f"... dalších {len(risks) - 10} rizik")
        message = QMessageBox(self)
        message.setWindowTitle("Dry-run MODIFY")
        message.setText(f"Dry-run identifikoval {len(files)} souborů. Pokračovat ve generování obsahu?")
        message.setInformativeText("Zkontrolujte seznam souborů a rizika.")
        message.setDetailedText("\n".join(details) if details else "Žádné detailní informace.")
        message.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        message.setDefaultButton(QMessageBox.Yes)
        result = message.exec()
        confirmed = result == QMessageBox.Yes
        if confirmed:
            self._append_log("Dry-run potvrzen; pokračuji generováním.")
        else:
            self._append_log("Dry-run odmítnut; pipeline zrušena.")
        return confirmed

    def _collect_directory_files(self, root: Path) -> Dict[str, Path]:
        mapping: Dict[str, Path] = {}
        for dirpath, _, filenames in os.walk(root):
            for name in filenames:
                candidate = Path(dirpath) / name
                try:
                    rel = candidate.relative_to(root)
                except ValueError:
                    rel = Path(name)
                mapping[str(rel)] = candidate
        return mapping

    def _read_file_lines(self, path: Path) -> List[str]:
        try:
            return path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except Exception:
            return []

    def _on_export_timeline(self) -> None:
        if not self._last_timeline_log:
            QMessageBox.information(self, "TIMELINE", "Žádný timeline k exportu.")
            return
        self._safe_open_path(self._last_timeline_log, "TIMELINE")

    def _copy_answare(self) -> None:
        payload = f"{self._last_response_id}\n{self._last_response_text}"
        QGuiApplication.clipboard().setText(payload)
        self._append_log("ANSWARE zkopírováno")

    def _copy_response_id(self) -> None:
        QGuiApplication.clipboard().setText(self._last_response_id)
        self.response_id_edit.setText(self._last_response_id)
        self._append_log("Response ID zkopírováno")

    def _run_script_workflow(self) -> None:
        if self._script_running:
            self._append_log("SCRIPT běží; počkejte na dokončení.")
            return
        if not self._ensure_diagnostics_prereq():
            return
        scopes = self._selected_diagnostic_scopes()
        if not scopes:
            QMessageBox.information(self, "SCRIPT", "Vyberte WINDOWS nebo SSH diagnostiku.")
            return
        if not self._prompt_script_warning(scopes):
            return
        diag_codes = self._selected_diagnostic_codes()
        diag_base = self._root_dir / "OUT" / "DIAGNOSTICS"
        diag_base.mkdir(parents=True, exist_ok=True)
        run_artifacts = init_run(self._root_dir)
        response_id = self.response_id_edit.text().strip() or PipelineExecutor.generate_response_id("SCRIPT")
        project = self.project_name_edit.text().strip() or "Kája"
        self._append_log(f"Skript diagnostiky spuštěn ({', '.join(scopes)})")
        progress = ProgressDialog(self)
        progress.setWindowTitle("SCRIPT diagnostika")
        progress.stop_requested_changed.connect(lambda _: self._append_log("SCRIPT: STOP požadován."))
        progress.show()
        QApplication.processEvents()
        self._script_running = True
        start_time = datetime.utcnow()
        diag_packages: List[Tuple[str, DiagnosticPackage]] = []
        upload_entries: List[Dict[str, Any]] = []
        errors: List[str] = []
        status = "completed"
        try:
            for index, scope in enumerate(scopes):
                if progress.stop_requested:
                    status = "cancelled"
                    progress.append_log("SCRIPT přerušeno uživatelem.")
                    break
                ratio = 0.05 + (index / len(scopes)) * 0.4
                progress.update_progress(f"Sběr diagnostiky {scope.upper()}", min(ratio, 0.5))
                QApplication.processEvents()
                try:
                    package = self._collect_diagnostic_package(scope, diag_base, project, response_id, diag_codes)
                    diag_packages.append((scope, package))
                    progress.append_log(f"{scope.upper()} snapshot: {package.root.name}")
                except Exception as exc:
                    errors.append(f"{scope}: {exc}")
                    self._append_log(f"Diagnostika {scope} selhala: {exc}")
                    continue
                QApplication.processEvents()
                try:
                    zip_path = self._zip_diagnostic_package(run_artifacts, scope, package, response_id, project)
                    progress.append_log(f"Archiv {scope}: {zip_path.name}")
                except Exception as exc:
                    errors.append(f"{scope} (zip): {exc}")
                    self._append_log(f"Archiv diagnostiky {scope} selhal: {exc}")
                    continue
                QApplication.processEvents()
                entry = self._upload_diagnostic_zip(run_artifacts, scope, zip_path, response_id, project)
                upload_entries.append(entry)
                progress.append_log(f"Upload {scope}: {entry.get('status')}")
                QApplication.processEvents()
        except Exception as exc:
            status = "failed"
            errors.append(str(exc))
            self._append_log(f"Skript diagnostiky skončil chybou: {exc}")
        finally:
            end_time = datetime.utcnow()
            if status not in ("cancelled", "failed"):
                status = "completed" if not errors else "partial"
            manifest_path = self._finalize_script_run(
                run_artifacts,
                project,
                response_id,
                scopes,
                diag_codes,
                diag_packages,
                upload_entries,
                status,
                errors,
                start_time,
                end_time,
            )
            progress.update_progress("Dokončeno", 1.0)
            QApplication.processEvents()
            progress.close()
            self._script_running = False
            self.response_id_edit.setText(response_id)
            self._last_response_id = response_id
            summary_lines = [f"Skript diagnostiky: {status}", f"Scopes: {', '.join(scopes)}"]
            if diag_packages:
                summary_lines.append("Snapshoty:")
                for scope, package in diag_packages:
                    summary_lines.append(f"- {scope.upper()}: {package.root}")
            if upload_entries:
                summary_lines.append("Uploads:")
                for entry in upload_entries:
                    status_text = entry.get("status", "unknown")
                    if status_text == "skipped" and entry.get("reason"):
                        status_text = f"{status_text} ({entry.get('reason')})"
                    summary_lines.append(
                        f"- {entry['scope']}: {status_text} (file_id={entry.get('file_id')})"
                    )
            if errors:
                summary_lines.append("Chyby:")
                summary_lines.extend(errors)
            self._append_log(f"Skript diagnostiky dokončen ({status}); manifest: {manifest_path}")
            QMessageBox.information(self, "SCRIPT", "\n".join(summary_lines))

    def _selected_diagnostic_scopes(self) -> List[str]:
        scopes: List[str] = []
        if self.windows_in_checkbox.isChecked() or self.windows_out_checkbox.isChecked():
            scopes.append("windows")
        if self.ssh_in_checkbox.isChecked() or self.ssh_out_checkbox.isChecked():
            scopes.append("ssh")
        return scopes

    def _selected_diagnostic_codes(self) -> List[str]:
        codes: List[str] = []
        if self.windows_in_checkbox.isChecked():
            codes.append("WINDOWS_IN")
        if self.windows_out_checkbox.isChecked():
            codes.append("WINDOWS_OUT")
        if self.ssh_in_checkbox.isChecked():
            codes.append("SSH_IN")
        if self.ssh_out_checkbox.isChecked():
            codes.append("SSH_OUT")
        return codes

    def _prompt_script_warning(self, scopes: List[str]) -> bool:
        text = (
            f"Tlačítko SCRIPT spustí sběr a upload diagnostických souborů ({', '.join(scopes)}). "
            "Akce je nevratná a obsahuje citlivá data; potvrďte pokračování."
        )
        result = QMessageBox.warning(
            self,
            "Potvrďte diagnostiku",
            text,
            QMessageBox.Ok | QMessageBox.Cancel,
        )
        return result == QMessageBox.Ok

    def _collect_diagnostic_package(
        self,
        scope: str,
        base_out: Path,
        project: str,
        response_id: str,
        diagnostics: List[str],
    ) -> DiagnosticPackage:
        if scope == "windows":
            return collect_windows_diagnostics(
                base_out=base_out,
                source_root=self._root_dir,
                project=project,
                response_id=response_id,
                diagnostics=diagnostics,
                settings=self._settings,
            )
        ssh_options = SshOptions(
            host=self.ssh_host_edit.text().strip(),
            port=self.ssh_port_spin.value(),
            user=self.ssh_user_edit.text().strip() or "root",
            key_path=self.ssh_key_edit.text().strip(),
            password=self.ssh_password_edit.text(),
        )
        return collect_ssh_diagnostics(
            base_out=base_out,
            source_root=self._root_dir,
            project=project,
            response_id=response_id,
            diagnostics=diagnostics,
            settings=self._settings,
            ssh_options=ssh_options,
        )

    def _zip_diagnostic_package(
        self,
        run_artifacts: RunArtifacts,
        scope: str,
        package: DiagnosticPackage,
        response_id: str,
        project: str,
    ) -> Path:
        zip_target = package.root.parent / f"{package.root.name}.zip"
        base_name = str(zip_target.with_suffix(""))
        archive = Path(shutil.make_archive(base_name, "zip", root_dir=package.root))
        payload = {
            "action": "zip_diagnostic_package",
            "scope": scope,
            "path": str(archive.relative_to(self._root_dir)),
            "absolute_path": str(archive),
            "response_id": response_id,
            "project": project,
        }
        log_file_operation(run_artifacts, payload)
        return archive

    def _upload_diagnostic_zip(
        self,
        run_artifacts: RunArtifacts,
        scope: str,
        zip_path: Path,
        response_id: str,
        project: str,
    ) -> Dict[str, Any]:
        entry: Dict[str, Any] = {
            "scope": scope,
            "zip_path": str(zip_path),
            "status": "skipped",
            "vector_store_ids": [],
            "project": project,
            "response_id": response_id,
            "uploaded_at": None,
            "file_id": None,
        }
        policy = self._security_policy_for("diagnostics")
        if policy:
            report = policy.evaluate_archive(zip_path)
            if report.findings:
                reasons = "; ".join(f"{finding.path or zip_path.name}: {finding.reason}" for finding in report.findings)
                security.record_security_event(run_artifacts, scope, str(zip_path), report, blocked=report.blocked)
                if report.blocked:
                    entry.update({"status": "blocked", "reason": reasons})
                    self._append_log(f"Security policy zablokovala upload {scope}: {reasons}")
                    return entry
                self._append_log(f"Security upozornění pro {scope}: {reasons}")
        if not self._openai_client:
            entry["reason"] = "OpenAI client není nakonfigurován."
            return entry
        try:
            upload_result = self._openai_client.upload_file(zip_path, purpose="diagnostics")
            file_id = upload_result.get("id") or upload_result.get("file_id")
            entry.update(
                {
                    "status": "uploaded",
                    "file_id": file_id,
                    "uploaded_at": datetime.utcnow().isoformat(),
                }
            )
            payload = {
                "scope": scope,
                "project": project,
                "response_id": response_id,
                "local_path": str(zip_path),
                "file_id": file_id,
                "purpose": "diagnostics",
                "size": zip_path.stat().st_size,
                "uploaded_at": entry["uploaded_at"],
            }
            log_file_upload(run_artifacts, payload)
            vector_store_ids = [
                store.store_id for store in self._vector_stores if store.store_id
            ]
            for store_id in vector_store_ids:
                if not file_id:
                    break
                try:
                    self._openai_client.add_vector_store_file(store_id, file_id)
                    entry["vector_store_ids"].append(store_id)
                    vs_payload = {
                        "scope": scope,
                        "project": project,
                        "response_id": response_id,
                        "vector_store_id": store_id,
                        "file_id": file_id,
                        "added_at": datetime.utcnow().isoformat(),
                    }
                    log_vector_store_entry(run_artifacts, vs_payload)
                except Exception as exc:
                    self._append_log(f"Vector store attach ({store_id}) selhalo: {exc}")
            return entry
        except Exception as exc:
            entry.update(
                {
                    "status": "failed",
                    "error": str(exc),
                    "uploaded_at": datetime.utcnow().isoformat(),
                }
            )
            self._append_log(f"Upload diagnostiky ({scope}) selhal: {exc}")
            return entry

    def _finalize_script_run(
        self,
        run_artifacts: RunArtifacts,
        project: str,
        response_id: str,
        scopes: List[str],
        diag_codes: List[str],
        diag_packages: List[Tuple[str, DiagnosticPackage]],
        upload_entries: List[Dict[str, Any]],
        status: str,
        errors: List[str],
        start_time: datetime,
        end_time: datetime,
    ) -> Path:
        metadata = {
            "project": project,
            "mode": "SCRIPT",
            "response_id": response_id,
            "diagnostic_scopes": scopes,
            "diagnostics": diag_codes,
            "status": status,
        }
        log_run_metadata(run_artifacts, metadata)
        packages_info = []
        for scope, package in diag_packages:
            upload_entry = next((entry for entry in upload_entries if entry.get("scope") == scope), {})
            packages_info.append(
                {
                    "scope": scope,
                    "root": str(package.root),
                    "manifest": str(package.manifest_path),
                    "submission": str(package.submission_path),
                    "notes": package.notes,
                    "metadata": package.metadata,
                    "archive": upload_entry.get("zip_path"),
                    "upload": upload_entry,
                }
            )
        manifest_payload = {
            "project": project,
            "response_id": response_id,
            "scopes": scopes,
            "status": status,
            "diagnostics": diag_codes,
            "packages": packages_info,
            "uploads": upload_entries,
            "errors": errors,
            "started_at": start_time.isoformat(),
            "ended_at": end_time.isoformat(),
            "duration_s": round((end_time - start_time).total_seconds(), 3),
        }
        manifest_path = log_manifest(run_artifacts, manifest_payload, "script_run_manifest")
        manifest_ref = str(manifest_path.relative_to(self._root_dir))
        log_dir_ref = str(Path(run_artifacts.log_dir).relative_to(self._root_dir))
        run_index_entry = {
            "run_id": run_artifacts.run_id,
            "project": project,
            "mode": "SCRIPT",
            "response_id": response_id,
            "status": status,
            "start": start_time.isoformat(),
            "end": end_time.isoformat(),
            "manifest": manifest_ref,
            "log_dir": log_dir_ref,
            "diagnostics": diag_codes,
        }
        log_run_index(self._root_dir, run_index_entry)
        return manifest_path

    def _open_api_key_dialog(self) -> None:
        dialog = ApiKeyDialog(self)
        dialog.exec()

    def _on_save_state(self) -> None:
        ui_state = self._build_ui_state(self.mode_combo.currentText())
        payload = self._serialize_run_state(ui_state)
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Uložit stav",
            str(self._root_dir / "state.json"),
            "Kája stav (*.json);;JSON (*.json);;Všechny soubory (*)",
        )
        if not path:
            return
        try:
            Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            self._append_log(f"Stav uložen do {path}")
        except Exception as exc:
            QMessageBox.warning(self, "SAVE", f"Nepodařilo se uložit stav: {exc}")

    def _on_load_state(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Načíst stav",
            str(self._root_dir),
            "Kája stav (*.json);;JSON (*.json);;Všechny soubory (*)",
        )
        if not path:
            return
        try:
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
            self._apply_loaded_state(payload)
            self._append_log(f"Stav načten z {path}")
        except Exception as exc:
            QMessageBox.warning(self, "LOAD", f"Nepodařilo se načíst stav: {exc}")

    def _on_load_request(self) -> None:
        default = self._root_dir / "LOG"
        if not default.exists():
            default = self._root_dir
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Načíst request",
            str(default),
            "Log soubory (*.json);;Všechny soubory (*)",
        )
        if not path:
            return
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            payload = data.get("payload", {})
            snapshot = payload.get("ui_state_snapshot")
            if not snapshot:
                QMessageBox.warning(self, "LOAD REQUEST", "Request log neobsahuje snapshot.")
                return
            self._apply_loaded_state(snapshot)
            last_response = snapshot.get("ui_state", {}).get("response_id", "")
            self.response_id_edit.clear()
            self._append_log(f"Load request: {Path(path).name}; předchozí Response ID {last_response}")
        except Exception as exc:
            QMessageBox.warning(self, "LOAD REQUEST", f"Nepodařilo se načíst request: {exc}")

    def _serialize_run_state(self, ui_state: UiState) -> Dict[str, Any]:
        return {
            "ui_state": asdict(ui_state),
            "attached_files": [asdict(record) for record in self._attached_files],
            "file_api_records": [asdict(record) for record in self._file_api_records],
            "vector_stores": [asdict(store) for store in self._vector_stores],
            "vector_store_files": dict(self._vector_store_files),
            "batch_jobs": self._batch_jobs,
        }

    def _build_request_snapshot(self, ui_state: UiState) -> Dict[str, Any]:
        return self._serialize_run_state(ui_state)

    def _apply_loaded_state(self, state: Dict[str, Any]) -> None:
        ui_state = state.get("ui_state", {})
        diagnostics = ui_state.get("diagnostics", {})
        ssh = ui_state.get("ssh", {})
        self.project_name_edit.setText(ui_state.get("project_name", ""))
        self.prompt_edit.setPlainText(ui_state.get("prompt_text", ""))
        self.mode_combo.setCurrentText(ui_state.get("mode", self.mode_combo.currentText()))
        self.send_as_c_checkbox.setChecked(bool(ui_state.get("send_as_c")))
        self.in_dir_edit.setText(ui_state.get("in_dir", ""))
        self.out_dir_edit.setText(ui_state.get("out_dir", ""))
        self.response_id_edit.clear()
        self.model_combo.setCurrentText(ui_state.get("model", self.model_combo.currentText()))
        self.windows_in_checkbox.setChecked(bool(diagnostics.get("windows_in")))
        self.windows_out_checkbox.setChecked(bool(diagnostics.get("windows_out")))
        self.ssh_in_checkbox.setChecked(bool(diagnostics.get("ssh_in")))
        self.ssh_out_checkbox.setChecked(bool(diagnostics.get("ssh_out")))
        self.ssh_host_edit.setText(ssh.get("host", self.ssh_host_edit.text()))
        self.ssh_port_spin.setValue(int(ssh.get("port", self.ssh_port_spin.value())))
        self.ssh_user_edit.setText(ssh.get("user", self.ssh_user_edit.text()))
        self.ssh_key_edit.setText(ssh.get("key_path", self.ssh_key_edit.text()))
        self.ssh_password_edit.setText(ssh.get("password", self.ssh_password_edit.text()))
        self.versing_button.setChecked(bool(ui_state.get("versing_enabled")))
        self._update_versing_button_state()
        self._attached_files = self._file_records_from_list(state.get("attached_files", []))
        self._file_api_records = self._file_records_from_list(state.get("file_api_records", []))
        self._vector_stores = self._vector_records_from_list(state.get("vector_stores", []))
        raw_store_files = state.get("vector_store_files", {})
        self._vector_store_files = {str(k): list(v) for k, v in raw_store_files.items()}
        self._batch_jobs = state.get("batch_jobs", self._batch_jobs)
        self._refresh_attached_table()
        self._refresh_file_api_table()
        self._refresh_vector_store_view()
        self._refresh_batch_monitor()
        self._append_log("Stav obnoven ze souboru.")

    def _file_records_from_list(self, data: List[Dict[str, Any]]) -> List[FileRecord]:
        records: List[FileRecord] = []
        for entry in data:
            try:
                records.append(
                    FileRecord(
                        file_id=str(entry.get("file_id", "")),
                        filename=str(entry.get("filename", "")),
                        purpose=str(entry.get("purpose", "")),
                        size_bytes=int(entry.get("size_bytes", 0)),
                    )
                )
            except Exception:
                continue
        return records

    def _vector_records_from_list(self, data: List[Dict[str, Any]]) -> List[VectorStoreRecord]:
        stores: List[VectorStoreRecord] = []
        for entry in data:
            try:
                stores.append(
                    VectorStoreRecord(
                        store_id=str(entry.get("store_id", "")),
                        name=str(entry.get("name", "")),
                        expires_at=entry.get("expires_at"),
                    )
                )
            except Exception:
                continue
        return stores

    def _browse_ssh_key(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Vyberte SSH klíč", "", "SSH keys (*.pem *.ppk *.key);;Všechny soubory (*)"
        )
        if path:
            self.ssh_key_edit.setText(path)

    def _pick_in_dir(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self,
            "Vyberte vstupní adresář",
            self.in_dir_edit.text() or str(self._root_dir),
        )
        if path:
            self.in_dir_edit.setText(path)

    def _pick_out_dir(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self,
            "Vyberte výstupní adresář",
            self.out_dir_edit.text() or self.in_dir_edit.text() or str(self._root_dir),
        )
        if path:
            self.out_dir_edit.setText(path)

    def _on_in_equals_out(self) -> None:
        source = self.in_dir_edit.text().strip()
        if source:
            self.out_dir_edit.setText(source)

    def _on_dir_content_changed(self) -> None:
        self._update_versing_button_state()

    def _update_versing_button_state(self) -> None:
        same = bool(self.in_dir_edit.text().strip() and self.out_dir_edit.text().strip() and self.in_dir_edit.text().strip() == self.out_dir_edit.text().strip())
        self.versing_button.setEnabled(same)
        if not same and self.versing_button.isChecked():
            self.versing_button.setChecked(False)

    def _on_versing_toggled(self, checked: bool) -> None:
        state = "aktivní" if checked else "vypnutý"
        self._append_log(f"VERSING {state}")

    def _build_ui_state(self, mode: str) -> UiState:
        diagnostics = DiagnosticsOptions(
            windows_in=self.windows_in_checkbox.isChecked(),
            windows_out=self.windows_out_checkbox.isChecked(),
            ssh_in=self.ssh_in_checkbox.isChecked(),
            ssh_out=self.ssh_out_checkbox.isChecked(),
        )
        ssh_options = SshOptions(
            host=self.ssh_host_edit.text().strip(),
            port=self.ssh_port_spin.value(),
            user=self.ssh_user_edit.text().strip() or "root",
            key_path=self.ssh_key_edit.text().strip(),
            password=self.ssh_password_edit.text(),
        )
        return UiState(
            project_name=self.project_name_edit.text().strip(),
            prompt_text=self.prompt_edit.toPlainText().strip(),
            in_dir=self.in_dir_edit.text().strip(),
            out_dir=self.out_dir_edit.text().strip(),
            mode=mode,
            model=self.model_combo.currentText(),
            diagnostics=diagnostics,
            versing_enabled=self.versing_button.isChecked(),
            attached_file_ids=[record.file_id for record in self._attached_files],
            ssh=ssh_options,
        )

    def _validate_inputs(self, mode: str) -> List[str]:
        errors: List[str] = []
        has_in = bool(self.in_dir_edit.text().strip())
        has_out = bool(self.out_dir_edit.text().strip())
        if mode == "GENERATE":
            if has_in:
                errors.append("GENERATE nesmí mít IN adresář")
            if not has_out:
                errors.append("GENERATE vyžaduje OUT adresář")
        elif mode == "MODIFY":
            if not has_in or not has_out:
                errors.append("MODIFY vyžaduje IN i OUT adresář")
        elif mode == "QA":
            if has_in or has_out:
                errors.append("QA nesmí mít IN ani OUT adresář")
        elif mode == "C":
            if has_in:
                errors.append("SEND AS C nesmí používat IN adresář")
            if not has_out:
                errors.append("SEND AS C vyžaduje OUT adresář")
            if self._attached_files:
                errors.append("SEND AS C musí mít prázdné připojené soubory")

        diag = [self.windows_in_checkbox.isChecked(), self.windows_out_checkbox.isChecked()]
        diag += [self.ssh_in_checkbox.isChecked(), self.ssh_out_checkbox.isChecked()]
        if sum(diag[:2]) and sum(diag[2:]):
            errors.append("Nelze kombinovat WINDOWS a SSH diagnostiku")
        if self.windows_in_checkbox.isChecked() and not has_in:
            errors.append("WINDOWS IN vyžaduje IN adresář")
        if self.windows_out_checkbox.isChecked() and not has_out:
            errors.append("WINDOWS OUT vyžaduje OUT adresář")
        if self.ssh_in_checkbox.isChecked() and not has_in:
            errors.append("SSH IN vyžaduje IN adresář")
        if self.ssh_out_checkbox.isChecked() and not has_out:
            errors.append("SSH OUT vyžaduje OUT adresář")
        if self.ssh_in_checkbox.isChecked() or self.ssh_out_checkbox.isChecked():
            if not self.ssh_host_edit.text().strip():
                errors.append("SSH diagnostika vyžaduje hostitel/IP")
            if not (
                self.ssh_key_edit.text().strip() or self.ssh_password_edit.text().strip()
            ):
                errors.append("SSH diagnostika vyžaduje SSH klíč nebo heslo")
        return errors

    def _append_log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_edit.appendPlainText(f"[{timestamp}] {message}")

    def _resolve_pricing_db_path(self) -> Path:
        db_path = Path(self._settings.db_path)
        if not db_path.is_absolute():
            db_path = self._root_dir / db_path
        return db_path

    def _show_pricing(self) -> None:
        store = PricingStore(self._resolve_pricing_db_path())
        dialog = PricingDialog(store, self._price_catalog, self)
        dialog.exec()
        self._update_pricing_status_label()

    def _open_settings(self) -> None:
        dialog = SettingsDialog(self._settings, self, panic_callback=self._on_panic_wipe_requested)
        if dialog.exec() == QDialog.Accepted:
            self._settings_store.save(self._settings)
            self._append_log("Nastavení uloženo.")
            refreshed = self._price_catalog.refresh()
            if refreshed:
                self._append_log("Ceník byl aktualizován podle nových nastavení.")
            else:
                self._append_log("Ceník je v režimu offline/odhad.")
            self._apply_settings_to_ssh_fields()
            self._refresh_diag_warning_label()
            self._update_pricing_status_label()
            self._apply_security_settings()

    def _refresh_diag_warning_label(self) -> None:
        if not hasattr(self, "_diag_warning_label"):
            return
        ack = self._settings.diagnostics_acknowledged
        admin_user = self._settings.admin_username or "není zadán"
        status = "potvrzeno" if ack else "nepotvrzeno"
        self._diag_warning_label.setText(
            f"Diagnostické varování {status}; admin: {admin_user}"
        )
        color = "#0a0" if ack else "#a00"
        self._diag_warning_label.setStyleSheet(f"color: {color}; font-weight: bold;")

    def _update_pricing_status_label(self) -> None:
        summary = self._price_catalog.summary()
        status = summary.get("status", "Neznámý")
        source = summary.get("source") or "lokální"
        refreshed = summary.get("last_refreshed") or "nikdy"
        verified = summary.get("verified", False)
        color = "#0a0" if verified else "#fa0"
        text = f"Ceník: {status}; Zdroj: {source}; Aktuálně: {refreshed}"
        self._pricing_status_label.setText(text)
        self._pricing_status_label.setStyleSheet(f"color: {color}; font-weight: bold;")

    def _apply_settings_to_ssh_fields(self) -> None:
        self.ssh_host_edit.setText(self._settings.ssh_host)
        self.ssh_port_spin.setValue(self._settings.ssh_port or 22)
        self.ssh_user_edit.setText(self._settings.ssh_user or "root")
        self.ssh_key_edit.setText(self._settings.ssh_key_path)
        self.ssh_password_edit.setText(self._settings.ssh_password)

    def _apply_security_settings(self) -> None:
        configure_log_encryption(self._settings.log_encryption_key or None)     
        self._security_policies = {
            "diagnostics": security.policy_from_settings(self._settings, "diagnostics"),
            "in": security.policy_from_settings(self._settings, "in"),
        }

    def _apply_manifest_styles(self) -> None:
        font = QFont("Montserrat")
        font.setWeight(QFont.Weight.Normal)
        app = QApplication.instance()
        if app:
            app.setFont(font)
        style = """
QMainWindow, QWidget, QDialog, QScrollArea {
    background: #010101;
    color: #fff;
    font-family: 'Montserrat';
}
QLabel {
    color: #fff;
}
QGroupBox {
    border: 2px solid #fff;
    border-radius: 14px;
    margin-top: 24px;
    padding: 12px;
    background: #010101;
}
QLineEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
    background: #010101;
    color: #fff;
    border: 1px solid #fff;
    border-radius: 10px;
    selection-background-color: #fff;
    selection-color: #000;
}
QPlainTextEdit {
    border-radius: 12px;
}
QTableWidget {
    border: 1px solid #fff;
    background: #010101;
    gridline-color: #fff;
}
QHeaderView::section {
    background: #030303;
    color: #fff;
    border: 1px solid #fff;
    padding: 6px;
    font-weight: bold;
}
QCheckBox::indicator, QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #fff;
    border-radius: 4px;
    background: #010101;
}
QCheckBox::indicator:checked, QRadioButton::indicator:checked {
    background: #fff;
}
QCheckBox::indicator:disabled, QRadioButton::indicator:disabled {
    border-color: #f00;
}
QPushButton {
    background: #000;
    color: #fff;
    border: 2px solid #fff;
    border-radius: 12px;
    padding: 6px 14px;
    min-height: 30px;
}
QPushButton:pressed,
QPushButton:checked,
QPushButton[active="true"] {
    background: #fff;
    color: #000;
    border-color: #fff;
}
QPushButton:disabled {
    border-color: #f00;
    color: #888;
    background: #000;
}
QPushButton[danger="true"] {
    background: #f00;
    border-color: #f00;
    color: #000;
    font-weight: bold;
}
QPushButton[danger="true"]:pressed,
QPushButton[danger="true"][active="true"] {
    background: #000;
    color: #f00;
    border-color: #f00;
}
QPushButton[park_control="true"] {
    border: none;
    border-radius: 14px;
    background: #030303;
    color: #fff;
    padding: 0;
}
QPushButton[park_control="true"][active="true"] {
    background: #fff;
    color: #000;
}
QProgressBar {
    border: 1px solid #fff;
    border-radius: 10px;
    background: #010101;
    color: #fff;
}
QProgressBar::chunk {
    background: #fff;
}
QFrame#status_bar, QStatusBar {
    border: 1px solid #fff;
    border-radius: 12px;
    background: #010101;
}
QFrame#status_bar QLabel {
    color: #fff;
}
"""
        self.setStyleSheet(style)

    def _security_policy_for(self, context: str) -> security.SecurityPolicy | None:
        return self._security_policies.get(context)

    def _on_panic_wipe_requested(self, include_logs: bool) -> None:
        self.panic_wipe(include_logs)

    def panic_wipe(self, include_logs: bool) -> None:
        text = "Panic wipe odstraní místní cache (OUT, pricing_cache.json, tmp)."
        if include_logs:
            text += " Logy budou také odstraněny."
        text += " Pokračovat?"
        result = QMessageBox.warning(
            self,
            "Panic wipe",
            text,
            QMessageBox.Yes | QMessageBox.No,
        )
        if result != QMessageBox.Yes:
            return
        targets = [
            self._root_dir / "OUT",
            self._root_dir / "pricing_cache.json",
            self._root_dir / "tmp",
        ]
        if include_logs:
            targets.append(self._root_dir / "LOG")
        deleted = []
        for target in targets:
            if not target.exists():
                continue
            try:
                if target.is_dir():
                    shutil.rmtree(target, ignore_errors=True)
                else:
                    target.unlink(missing_ok=True)
                deleted.append(str(target.relative_to(self._root_dir)))
            except Exception as exc:
                self._append_log(f"Panic wipe: nelze odstranit {target}: {exc}")
        self._append_log(f"Panic wipe dokončen. Odstraněno: {', '.join(deleted)}")

    def _on_windows_in_state_changed(self, state: int) -> None:
        if not self.windows_in_checkbox.isChecked() and self.windows_out_checkbox.isChecked():
            self._append_log("WINDOWS OUT závisí na WINDOWS IN; WINDOWS OUT vypnuto.")
            self.windows_out_checkbox.setChecked(False)
        self._refresh_diag_warning_label()

    def _on_windows_out_state_changed(self, state: int) -> None:
        if self.windows_out_checkbox.isChecked() and not self.windows_in_checkbox.isChecked():
            self.windows_in_checkbox.setChecked(True)
            self._append_log("WINDOWS OUT vyžaduje WINDOWS IN; WINDOWS IN aktivováno.")
        self._refresh_diag_warning_label()

    def _on_ssh_in_state_changed(self, state: int) -> None:
        if not self.ssh_in_checkbox.isChecked() and self.ssh_out_checkbox.isChecked():
            self._append_log("SSH OUT závisí na SSH IN; SSH OUT vypnuto.")
            self.ssh_out_checkbox.setChecked(False)
        self._refresh_diag_warning_label()

    def _on_ssh_out_state_changed(self, state: int) -> None:
        if self.ssh_out_checkbox.isChecked() and not self.ssh_in_checkbox.isChecked():
            self.ssh_in_checkbox.setChecked(True)
            self._append_log("SSH OUT vyžaduje SSH IN; SSH IN aktivováno.")
        self._refresh_diag_warning_label()

    def _ensure_diagnostics_prereq(self) -> bool:
        diag_active = any(
            [
                self.windows_in_checkbox.isChecked(),
                self.windows_out_checkbox.isChecked(),
                self.ssh_in_checkbox.isChecked(),
                self.ssh_out_checkbox.isChecked(),
            ]
        )
        if not diag_active:
            return True
        if not self._settings.diagnostics_acknowledged:
            if not self._prompt_diagnostics_ack():
                return False
        if (self.windows_in_checkbox.isChecked() or self.windows_out_checkbox.isChecked()) and (
            not self._settings.admin_username or not self._settings.admin_password
        ):
            QMessageBox.warning(
                self,
                "Administrátorská práva chybí",
                "Pro WINDOWS diagnostiku nastavte administrátorského uživatele v Nastavení.",
            )
            return False
        return True

    def _prompt_diagnostics_ack(self) -> bool:
        text = (
            "Diagnostická data mohou obsahovat velmi citlivé informace. "
            "Potvrďte, že s jejich uložením v LOG a manifestu souhlasíte."
        )
        result = QMessageBox.warning(
            self,
            "Citlivé diagnostické data",
            text,
            QMessageBox.Ok | QMessageBox.Cancel,
        )
        if result == QMessageBox.Ok:
            self._settings.diagnostics_acknowledged = True
            self._settings_store.save(self._settings)
            self._append_log("Diagnostické varování potvrzeno.")
            self._refresh_diag_warning_label()
            return True
        self._append_log("Diagnostické varování odmítnuto.")
        return False


SECTION_MIME_TYPE = "application/x-kaja-section"


@dataclass(frozen=True)
class SectionDefinition:
    section_id: str
    title: str
    builder: Callable[[], QWidget]


class SectionDragHandle(QLabel):
    def __init__(self, section_id: str, title: str, workspace: "WorkspacePane"):
        super().__init__(title.upper())
        self._section_id = section_id
        self._workspace = workspace
        self._drag_start = None
        self.setCursor(QCursor(Qt.OpenHandCursor))
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        font = QFont("Montserrat", 12, QFont.Bold)
        self.setFont(font)
        self.setStyleSheet("color:#fff; border:none;")

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self._drag_start = event.pos()
            self.setCursor(QCursor(Qt.ClosedHandCursor))
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self.setCursor(QCursor(Qt.OpenHandCursor))
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if not (event.buttons() & Qt.LeftButton):
            return
        if not self._drag_start:
            return
        if (event.pos() - self._drag_start).manhattanLength() < QApplication.startDragDistance():
            return
        self._workspace.start_section_drag(self._section_id, self)


class SectionWidget(QFrame):
    def __init__(
        self,
        section_id: str,
        title: str,
        content: QWidget,
        workspace: "WorkspacePane",
    ):
        super().__init__()
        self._section_id = section_id
        self._workspace = workspace
        self.setObjectName("section_frame")
        self.setMinimumSize(0, 0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._border_radius = 12
        self._layout = QVBoxLayout(self)
        self._base_margin = 10
        self._base_spacing = 8
        self._apply_section_scale()
        self._layout.setSizeConstraint(QLayout.SetNoConstraint)

        header = QFrame()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(6)
        self._drag_handle = SectionDragHandle(section_id, title, workspace)
        header_layout.addWidget(self._drag_handle)
        header_layout.addStretch()
        self._layout.addWidget(header)
        content.setMinimumSize(0, 0)
        content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        if content.layout():
            content.layout().setSizeConstraint(QLayout.SetNoConstraint)
        self._relax_widget_constraints(content)
        for child in content.findChildren(QWidget):
            self._relax_widget_constraints(child)
        self._layout.addWidget(content, 1)

    @property
    def section_id(self) -> str:
        return self._section_id

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._apply_section_scale()

    def _apply_section_scale(self) -> None:
        scale = 0.0
        span = min(self.width(), self.height())
        if span > 0:
            scale = min(1.0, span / 400)
        margin = max(0, int(self._base_margin * scale))
        spacing = max(0, int(self._base_spacing * scale))
        self._layout.setContentsMargins(margin, margin, margin, margin)
        self._layout.setSpacing(spacing)

    @staticmethod
    def _relax_widget_constraints(widget: QWidget) -> None:
        widget.setMinimumSize(0, 0)
        policy = widget.sizePolicy()
        if policy.horizontalPolicy() in (QSizePolicy.Fixed, QSizePolicy.Minimum, QSizePolicy.Maximum):
            policy.setHorizontalPolicy(QSizePolicy.Expanding)
        if policy.verticalPolicy() in (QSizePolicy.Fixed, QSizePolicy.Minimum, QSizePolicy.Maximum):
            policy.setVerticalPolicy(QSizePolicy.Expanding)
        if isinstance(widget, QAbstractScrollArea):
            policy.setHorizontalPolicy(QSizePolicy.Expanding)
            policy.setVerticalPolicy(QSizePolicy.Expanding)
        widget.setSizePolicy(policy)

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(0, 0, -1, -1)
        pen = QPen(QColor("#fff"))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(rect, self._border_radius, self._border_radius)

        if not self._drag_handle:
            return
        gap = self._gap_width()
        label_pos = self._drag_handle.mapTo(self, QPoint(0, 0))
        label_left = label_pos.x()
        label_right = label_left + self._drag_handle.width()
        gap_start = max(rect.left() + self._border_radius, label_left - gap)
        gap_end = min(rect.right() - self._border_radius, label_right + gap)

        if gap_end > gap_start:
            fill_rect = QRect(gap_start, rect.top(), max(1, gap_end - gap_start), self._border_radius)
            painter.fillRect(fill_rect, QColor("#010101"))
        left_end = gap_start
        right_start = gap_end
        if left_end > rect.left() + self._border_radius:
            painter.drawLine(rect.left() + self._border_radius, rect.top(), left_end, rect.top())
        if right_start < rect.right() - self._border_radius:
            painter.drawLine(right_start, rect.top(), rect.right() - self._border_radius, rect.top())

    def _gap_width(self) -> int:
        font = self._drag_handle.font()
        metrics = QFontMetrics(font)
        return max(8, metrics.horizontalAdvance("A"))


class ParkTile(QFrame):
    def __init__(self, section_id: str, title: str, workspace: "WorkspacePane"):
        super().__init__()
        self._section_id = section_id
        self._workspace = workspace
        self.setObjectName("park_tile")
        self.setFrameShape(QFrame.NoFrame)
        self.setStyleSheet(
            "QFrame#park_tile { background:#010101; border:1px solid #fff; border-radius:12px; }"
        )
        self.setCursor(QCursor(Qt.OpenHandCursor))
        self.setMinimumSize(0, 0)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._label = QLabel(title)
        self._label.setAlignment(Qt.AlignCenter)
        self._label.setWordWrap(True)
        self._label.setStyleSheet("color:#fff; font-weight: bold;")
        self._label.setMinimumSize(0, 0)
        self._label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        layout.addWidget(self._label, 1)
        self._drag_start = None

    def label_text(self) -> str:
        return self._label.text()

    def apply_style(self, font_size: int, padding: int) -> None:
        font = self._label.font()
        font.setPointSize(max(1, font_size))
        self._label.setFont(font)
        self._label.setStyleSheet(f"color:#fff; padding:{max(0, padding)}px;")

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self._drag_start = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if not (event.buttons() & Qt.LeftButton):
            return
        if not self._drag_start:
            return
        if (event.pos() - self._drag_start).manhattanLength() < QApplication.startDragDistance():
            return
        self._workspace.start_section_drag(self._section_id, self)


class ParkGrid(QWidget):
    def __init__(self, workspace: "WorkspacePane") -> None:
        super().__init__()
        self._workspace = workspace
        self._tiles: List[ParkTile] = []
        self._spacing = 8
        self.setAcceptDrops(True)
        self.setMinimumSize(0, 0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_tiles(self, tiles: List[ParkTile]) -> None:
        for tile in self._tiles:
            tile.hide()
        self._tiles = tiles
        for tile in self._tiles:
            if tile.parent() is not self:
                tile.setParent(self)
            tile.show()
        self._relayout()

    def set_spacing(self, spacing: int) -> None:
        self._spacing = spacing
        self._relayout()

    def dragEnterEvent(self, event) -> None:
        if self._workspace.has_section_mime(event.mimeData()):
            event.acceptProposedAction()

    def dragMoveEvent(self, event) -> None:
        if self._workspace.has_section_mime(event.mimeData()):
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:
        section_id = self._workspace.extract_section_id(event.mimeData())
        if section_id:
            self._workspace.move_section_to_park(section_id)
            event.acceptProposedAction()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._relayout()

    def sizeHint(self) -> QSize:
        return QSize(0, 0)

    def minimumSizeHint(self) -> QSize:
        return QSize(0, 0)

    def _relayout(self) -> None:
        count = len(self._tiles)
        if count == 0:
            return
        width = max(1, self.width())
        height = max(1, self.height())
        spacing = self._spacing
        best_cols = 1
        best_size = 0
        max_cols = min(2, count)
        for cols in range(1, max_cols + 1):
            rows = math.ceil(count / cols)
            tile_size = min(
                (width - spacing * (cols - 1)) / cols,
                (height - spacing * (rows - 1)) / rows,
            )
            if tile_size > best_size:
                best_size = tile_size
                best_cols = cols
        tile_size = max(4, int(best_size))
        padding = max(2, int(tile_size * 0.08))
        available_width = max(1, tile_size - 2 * padding)
        available_height = max(1, tile_size - 2 * padding)
        font_size = self._compute_global_font_size(
            available_width,
            available_height,
            [tile.label_text() for tile in self._tiles],
        )
        rows = math.ceil(count / best_cols)
        grid_width = tile_size * best_cols + spacing * (best_cols - 1)
        grid_height = tile_size * rows + spacing * (rows - 1)
        offset_x = max(0, int((width - grid_width) / 2))
        offset_y = max(0, int((height - grid_height) / 2))
        for index, tile in enumerate(self._tiles):
            tile.apply_style(font_size, padding)
            row = index // best_cols
            col = index % best_cols
            x = offset_x + col * (tile_size + spacing)
            y = offset_y + row * (tile_size + spacing)
            tile.setGeometry(x, y, tile_size, tile_size)

    def _compute_global_font_size(
        self, width: int, height: int, texts: List[str]
    ) -> int:
        if not texts:
            return 1
        low, high = 1, max(1, height)
        best = 1
        base_font = self.font()
        while low <= high:
            mid = (low + high) // 2
            font = QFont(base_font)
            font.setPointSize(mid)
            metrics = QFontMetrics(font)
            fits = True
            for text in texts:
                rect = metrics.boundingRect(
                    0,
                    0,
                    width,
                    height,
                    Qt.AlignCenter | Qt.TextWordWrap,
                    text,
                )
                if rect.width() > width or rect.height() > height:
                    fits = False
                    break
            if fits:
                best = mid
                low = mid + 1
            else:
                high = mid - 1
        return best


class ColumnArea(QFrame):
    def __init__(self, workspace: "WorkspacePane", index: int) -> None:
        super().__init__()
        self._workspace = workspace
        self._index = index
        self.setAcceptDrops(True)
        self.setFrameShape(QFrame.NoFrame)
        self.setStyleSheet("background:#030303; border:1px solid #fff; border-radius:12px;")
        self.setMinimumSize(0, 0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._layout = QVBoxLayout(self)
        self._base_margin = 10
        self._layout.setSpacing(0)
        self._layout.setSizeConstraint(QLayout.SetNoConstraint)
        self._splitter = QSplitter(Qt.Vertical)
        self._splitter.setChildrenCollapsible(True)
        self._splitter.setHandleWidth(6)
        self._splitter.setMinimumSize(0, 0)
        self._splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._splitter.setStyleSheet(
            "QSplitter::handle { background:#fff; }"
            "QSplitter::handle:horizontal { width:6px; }"
            "QSplitter::handle:vertical { height:6px; }"
        )
        self._layout.addWidget(self._splitter)
        self._apply_column_scale()

    def set_index(self, index: int) -> None:
        self._index = index

    def section_widgets(self) -> List[SectionWidget]:
        widgets: List[SectionWidget] = []
        for idx in range(self._splitter.count()):
            widget = self._splitter.widget(idx)
            if isinstance(widget, SectionWidget):
                widgets.append(widget)
        return widgets

    def add_section(self, widget: SectionWidget) -> None:
        sizes = self._splitter.sizes()
        self._splitter.addWidget(widget)
        self._sync_section_sizes(sizes)

    def remove_section(self, widget: SectionWidget) -> None:
        sizes = self._splitter.sizes()
        index = self._splitter.indexOf(widget)
        if index < 0:
            return
        widget.setParent(None)
        self._sync_section_sizes(sizes, removed_index=index)

    def _sync_section_sizes(self, previous_sizes: List[int], removed_index: int | None = None) -> None:
        sizes = list(previous_sizes)
        if removed_index is not None and 0 <= removed_index < len(sizes):
            sizes.pop(removed_index)
        count = self._splitter.count()
        if count == 0:
            return
        if count > len(sizes):
            default_size = 1
            if sizes:
                default_size = max(1, int(sum(sizes) / len(sizes)))
            sizes.append(default_size)
        if len(sizes) != count:
            sizes = [1] * count
        self._splitter.setSizes(sizes)
        for index in range(count):
            self._splitter.setStretchFactor(index, 1)

    def dragEnterEvent(self, event) -> None:
        if self._workspace.has_section_mime(event.mimeData()):
            event.acceptProposedAction()

    def dragMoveEvent(self, event) -> None:
        if self._workspace.has_section_mime(event.mimeData()):
            event.acceptProposedAction()

    def dropEvent(self, event) -> None:
        section_id = self._workspace.extract_section_id(event.mimeData())
        if section_id:
            self._workspace.move_section_to_column(section_id, self._index)
            event.acceptProposedAction()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._apply_column_scale()

    def _apply_column_scale(self) -> None:
        scale = 0.0
        span = min(self.width(), self.height())
        if span > 0:
            scale = min(1.0, span / 400)
        margin = max(0, int(self._base_margin * scale))
        self._layout.setContentsMargins(margin, margin, margin, margin)



class WorkspacePane(QWidget):
    _min_columns = 1
    _max_columns = 4

    def __init__(self, sections: List[SectionDefinition]) -> None:
        super().__init__()
        self.setMinimumSize(0, 0)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._sections = sections
        self._section_order = [section.section_id for section in sections]
        self._section_defs = {section.section_id: section for section in sections}
        self._section_locations: Dict[str, Optional[int]] = {
            section.section_id: None for section in sections
        }
        self._section_widgets: Dict[str, SectionWidget] = {}
        self._park_tiles = {
            section.section_id: ParkTile(section.section_id, section.title, self)
            for section in sections
        }
        self._palette_scale = 1.0

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._columns_splitter = QSplitter(Qt.Horizontal)
        self._columns_splitter.setHandleWidth(6)
        self._columns_splitter.setChildrenCollapsible(True)
        self._columns_splitter.setStyleSheet(
            "QSplitter::handle { background:#fff; }"
            "QSplitter::handle:horizontal { width:6px; }"
            "QSplitter::handle:vertical { height:6px; }"
        )
        layout.addWidget(self._columns_splitter)

        self._palette_frame = QFrame()
        self._palette_frame.setObjectName("park_panel")
        self._palette_frame.setFrameShape(QFrame.NoFrame)
        self._palette_frame.setStyleSheet(
            "QFrame#park_panel { border:2px solid #fff; border-radius:12px; background:#010101; }"
            "QFrame#park_panel * { border: none; }"
        )
        self._palette_layout = QVBoxLayout(self._palette_frame)
        self._palette_layout.setContentsMargins(12, 12, 12, 12)
        self._palette_layout.setSpacing(12)

        self._header_label = QLabel("PARKOVIŠTĚ")
        header_label_font = QFont("Montserrat", 10, QFont.Bold)
        self._header_label.setFont(header_label_font)
        self._header_label.setStyleSheet("border:none;")
        self._header_label.setAlignment(Qt.AlignCenter)
        self._palette_layout.addWidget(self._header_label)

        self._park_grid = ParkGrid(self)
        self._palette_layout.addWidget(self._park_grid, 1)

        control_holder = QWidget()
        self._control_layout = QHBoxLayout(control_holder)
        self._control_layout.setContentsMargins(0, 0, 0, 0)
        self._control_layout.setSpacing(6)
        self._column_buttons: List[QPushButton] = []
        for number in range(1, 5):
            button = QPushButton(str(number))
            button.setCheckable(True)
            button.setMinimumSize(0, 0)
            button.setCursor(QCursor(Qt.PointingHandCursor))
            button.clicked.connect(partial(self._set_column_count, number))
            button.setProperty("park_control", True)
            self._control_layout.addWidget(button)
            self._column_buttons.append(button)
        self._palette_layout.addWidget(control_holder)

        layout.addWidget(self._palette_frame)
        self._columns: List[ColumnArea] = []
        self._active_columns = 0
        self._set_column_count(1)
        self._update_palette_width(self.width() or 800)
        self._update_park_tiles()

    def start_section_drag(self, section_id: str, source: QWidget) -> None:
        mime = QMimeData()
        mime.setData(SECTION_MIME_TYPE, section_id.encode("utf-8"))
        drag = QDrag(source)
        drag.setMimeData(mime)
        pixmap = source.grab()
        if not pixmap.isNull():
            drag.setPixmap(pixmap)
            drag.setHotSpot(pixmap.rect().center())
        drag.exec(Qt.MoveAction)

    def has_section_mime(self, mime: QMimeData) -> bool:
        return mime.hasFormat(SECTION_MIME_TYPE)

    def extract_section_id(self, mime: QMimeData) -> Optional[str]:
        if not mime.hasFormat(SECTION_MIME_TYPE):
            return None
        raw = bytes(mime.data(SECTION_MIME_TYPE))
        section_id = raw.decode("utf-8")
        if section_id not in self._section_defs:
            return None
        return section_id

    def move_section_to_column(self, section_id: str, column_index: int) -> None:
        if section_id not in self._section_defs:
            return
        if column_index < 0 or column_index >= len(self._columns):
            return
        if self._section_locations.get(section_id) == column_index:
            return
        self._detach_section(section_id)
        widget = self._get_section_widget(section_id)
        column = self._columns[column_index]
        column.add_section(widget)
        widget.show()
        self._section_locations[section_id] = column_index
        self._update_park_tiles()

    def move_section_to_park(self, section_id: str) -> None:
        if section_id not in self._section_defs:
            return
        if self._section_locations.get(section_id) is None:
            return
        self._detach_section(section_id)
        widget = self._section_widgets.get(section_id)
        if widget:
            widget.hide()
        self._section_locations[section_id] = None
        self._update_park_tiles()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._update_palette_width(event.size().width())

    def _set_column_count(self, count: int) -> None:
        target = max(self._min_columns, min(self._max_columns, count))
        while len(self._columns) < target:
            column = ColumnArea(self, len(self._columns))
            self._columns_splitter.addWidget(column)
            self._columns.append(column)
        while len(self._columns) > target:
            column = self._columns.pop()
            for widget in column.section_widgets():
                self.move_section_to_park(widget.section_id)
            column.setParent(None)
            column.deleteLater()
        for idx, column in enumerate(self._columns):
            column.set_index(idx)
        self._active_columns = target
        self._sync_column_buttons()
        self._rebalance_columns()

    def _sync_column_buttons(self) -> None:
        for index, button in enumerate(self._column_buttons, start=1):
            active = index <= self._active_columns
            button.setChecked(active)
            button.setProperty("active", active)
            button.style().unpolish(button)
            button.style().polish(button)

    def _rebalance_columns(self) -> None:
        count = len(self._columns)
        if count == 0:
            return
        self._columns_splitter.setSizes([1] * count)
        for index in range(count):
            self._columns_splitter.setStretchFactor(index, 1)

    def _get_section_widget(self, section_id: str) -> SectionWidget:
        widget = self._section_widgets.get(section_id)
        if widget:
            return widget
        definition = self._section_defs[section_id]
        content = definition.builder()
        widget = SectionWidget(section_id, definition.title, content, self)
        self._section_widgets[section_id] = widget
        return widget

    def _detach_section(self, section_id: str) -> None:
        widget = self._section_widgets.get(section_id)
        if not widget:
            return
        parent = widget.parentWidget()
        if isinstance(parent, QSplitter) and isinstance(parent.parentWidget(), ColumnArea):
            parent.parentWidget().remove_section(widget)
            return
        if isinstance(parent, ColumnArea):
            parent.remove_section(widget)
            return
        widget.setParent(None)

    def _update_park_tiles(self) -> None:
        tiles = [
            self._park_tiles[section_id]
            for section_id in self._section_order
            if self._section_locations.get(section_id) is None
        ]
        self._park_grid.set_tiles(tiles)

    def _update_palette_width(self, total_width: int) -> None:
        palette_width = max(0, int(total_width / 11))
        palette_width = min(palette_width, total_width)
        self._palette_frame.setFixedWidth(palette_width)
        self._apply_palette_scale()

    def _apply_palette_scale(self) -> None:
        base_width = 220
        scale = max(0.0, self._palette_frame.width() / base_width)
        self._palette_scale = scale
        margin = max(0, int(12 * scale))
        spacing = max(0, int(12 * scale))
        self._palette_layout.setContentsMargins(margin, margin, margin, margin)
        self._palette_layout.setSpacing(spacing)
        header_font = self._header_label.font()
        header_font.setPointSize(max(1, int(10 * scale)))
        self._header_label.setFont(header_font)
        button_font = self._column_buttons[0].font() if self._column_buttons else QFont()
        button_font.setPointSize(max(1, int(12 * scale)))
        for button in self._column_buttons:
            button.setFont(button_font)
        self._control_layout.setSpacing(max(0, int(6 * scale)))
        self._park_grid.set_spacing(max(0, int(8 * scale)))


