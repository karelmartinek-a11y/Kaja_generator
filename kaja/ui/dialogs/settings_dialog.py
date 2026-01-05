from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QCheckBox,
    QDoubleSpinBox,
    QWidget,
    QFileDialog,
)
from typing import Callable, Iterable, List

from kaja.core.settings import Settings


class SettingsDialog(QDialog):
    def __init__(self, settings: Settings, parent=None, panic_callback: Callable[[bool], None] | None = None):
        super().__init__(parent)
        self.setWindowTitle("SETTINGS")
        self._settings = settings
        self._panic_callback = panic_callback

        layout = QVBoxLayout(self)
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_container = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_layout.setContentsMargins(8, 8, 8, 8)
        scroll_layout.setSpacing(12)
        scroll_container.setLayout(scroll_layout)
        form = QFormLayout()

        self._db_path = QLineEdit(settings.db_path)
        self._log_max_runs = QSpinBox()
        self._log_max_runs.setMaximum(100000)
        self._log_max_runs.setValue(settings.log_max_runs)

        self._log_max_size = QSpinBox()
        self._log_max_size.setMaximum(100000)
        self._log_max_size.setValue(settings.log_max_size_mb)

        self._retry_attempts = QSpinBox()
        self._retry_attempts.setMaximum(100)
        self._retry_attempts.setValue(settings.retry_max_attempts)

        self._retry_delay = QSpinBox()
        self._retry_delay.setMaximum(3600)
        self._retry_delay.setValue(settings.retry_max_delay_sec)

        self._pricing_url = QLineEdit(settings.pricing_url)
        self._pricing_ttl = QSpinBox()
        self._pricing_ttl.setMaximum(100000)
        self._pricing_ttl.setValue(settings.pricing_cache_ttl_min)

        self._auto_refresh = QCheckBox("Auto-refresh pri startu")
        self._auto_refresh.setChecked(settings.pricing_auto_refresh)
        self._pricing_url.setPlaceholderText("https://.../pricing-table.json")
        self._pricing_url.setToolTip("URL online ceníku (volitelné). Ceník obsahuje sazby pro tokeny, vector store i storage-days.")
        self._pricing_ttl.setToolTip("Jak dlouho se má výsledek ceníku cachovat (minuty).")
        self._auto_refresh.setToolTip("Při spuštění se stáhne nový ceník, pokud je URL dostupná.")

        self._mask_secrets = QCheckBox("Maskovat tajemstvi v logu")
        self._mask_secrets.setChecked(settings.mask_secrets)

        self._encrypt_logs = QCheckBox("Sifrovat logy")
        self._encrypt_logs.setChecked(settings.encrypt_logs)

        self._admin_username = QLineEdit(settings.admin_username)
        self._admin_password = QLineEdit(settings.admin_password)
        self._admin_password.setEchoMode(QLineEdit.Password)
        self._ssh_host = QLineEdit(settings.ssh_host)
        self._ssh_port = QSpinBox()
        self._ssh_port.setRange(1, 65535)
        self._ssh_port.setValue(settings.ssh_port)
        self._ssh_user = QLineEdit(settings.ssh_user or "root")
        self._ssh_key = QLineEdit(settings.ssh_key_path)
        self._ssh_key_browse = QPushButton("Procházet...")
        self._ssh_key_browse.clicked.connect(self._browse_ssh_key)
        self._ssh_password = QLineEdit(settings.ssh_password)
        self._ssh_password.setEchoMode(QLineEdit.Password)
        self._diag_warning_button = QPushButton("Varování diagnostiky")
        self._diag_warning_reset_button = QPushButton("Resetovat varování")
        self._diag_warning_status = QLabel()
        self._diag_warning_status.setWordWrap(True)
        self._diag_warning_widget = QWidget()
        diag_layout = QHBoxLayout(self._diag_warning_widget)
        diag_layout.setContentsMargins(0, 0, 0, 0)
        diag_layout.addWidget(self._diag_warning_button)
        diag_layout.addWidget(self._diag_warning_reset_button)
        diag_layout.addWidget(self._diag_warning_status)
        self._diagnostics_acknowledged = settings.diagnostics_acknowledged
        self._diag_warning_button.clicked.connect(self._show_diag_warning)
        self._diag_warning_reset_button.clicked.connect(self._reset_diag_warning)
        self._update_diag_ack_label()

        self._batch_poll_interval = QSpinBox()
        self._batch_poll_interval.setMaximum(3600)
        self._batch_poll_interval.setValue(settings.batch_poll_interval_sec)     

        self._batch_timeout = QSpinBox()
        self._batch_timeout.setMaximum(100000)
        self._batch_timeout.setValue(settings.batch_timeout_sec)

        self._default_model = QLineEdit(settings.default_model)
        self._default_temperature = QDoubleSpinBox()
        self._default_temperature.setDecimals(2)
        self._default_temperature.setSingleStep(0.05)
        self._default_temperature.setRange(0.0, 2.0)
        self._default_temperature.setValue(settings.default_temperature)

        form.addRow("DB path", self._db_path)
        form.addRow("Log max runs", self._log_max_runs)
        form.addRow("Log max size (MB)", self._log_max_size)
        form.addRow("Retry attempts", self._retry_attempts)
        form.addRow("Retry max delay (sec)", self._retry_delay)
        form.addRow("Pricing URL", self._pricing_url)
        form.addRow("Pricing TTL (min)", self._pricing_ttl)
        form.addRow("Pricing auto-refresh", self._auto_refresh)
        pricing_help = QLabel(
            "Ceník se stahuje z uvedené URL (pokud je vyplněná) nebo z oficiálního OpenAI endpointu"
            " https://pricing.openai.com/pricing.json a pokrývá tokeny, vector store i storage-days."
            " Pokud je online ceník nedostupný, program pokračuje s odhadem a účtenka, UI i manifesty jsou označeny jako neověřeno."
        )
        pricing_help.setWordWrap(True)
        pricing_help.setStyleSheet("color: #fff; font-style: italic;")
        form.addRow("", pricing_help)
        form.addRow("Mask secrets", self._mask_secrets)
        form.addRow("Encrypt logs", self._encrypt_logs)
        form.addRow("Admin uživatel", self._admin_username)
        form.addRow("Admin heslo", self._admin_password)
        ssh_key_layout = QHBoxLayout()
        ssh_key_layout.setContentsMargins(0, 0, 0, 0)
        ssh_key_layout.addWidget(self._ssh_key)
        ssh_key_layout.addWidget(self._ssh_key_browse)
        form.addRow("SSH host", self._ssh_host)
        form.addRow("SSH port", self._ssh_port)
        form.addRow("SSH user", self._ssh_user)
        form.addRow("SSH key", ssh_key_layout)
        form.addRow("SSH password", self._ssh_password)
        form.addRow("Diagnostické varování", self._diag_warning_widget)
        form.addRow("Batch poll interval (sec)", self._batch_poll_interval)
        form.addRow("Batch timeout (sec)", self._batch_timeout)
        form.addRow("Default model", self._default_model)
        form.addRow("Default temperature", self._default_temperature)

        self._allow_ext_in_edit = QPlainTextEdit(self._list_to_text(settings.allow_extensions_in))
        self._deny_ext_in_edit = QPlainTextEdit(self._list_to_text(settings.deny_extensions_in))
        self._allow_paths_in_edit = QPlainTextEdit(self._list_to_text(settings.allow_paths_in))
        self._deny_paths_in_edit = QPlainTextEdit(self._list_to_text(settings.deny_paths_in))
        self._allow_ext_diag_edit = QPlainTextEdit(self._list_to_text(settings.allow_extensions_diag))
        self._deny_ext_diag_edit = QPlainTextEdit(self._list_to_text(settings.deny_extensions_diag))
        self._allow_paths_diag_edit = QPlainTextEdit(self._list_to_text(settings.allow_paths_diag))
        self._deny_paths_diag_edit = QPlainTextEdit(self._list_to_text(settings.deny_paths_diag))
        for edit in (
            self._allow_ext_in_edit,
            self._deny_ext_in_edit,
            self._allow_paths_in_edit,
            self._deny_paths_in_edit,
            self._allow_ext_diag_edit,
            self._deny_ext_diag_edit,
            self._allow_paths_diag_edit,
            self._deny_paths_diag_edit,
        ):
            edit.setPlaceholderText("Enter one pattern per line (e.g., *.env or **/logs/*)")
            edit.setFixedHeight(80)

        security_group = QGroupBox("Security policy (B1/B2/B3)")
        security_layout = QGridLayout()
        security_group.setLayout(security_layout)
        security_layout.addWidget(QLabel("Allow extensions (IN mirror)"), 0, 0)
        security_layout.addWidget(self._allow_ext_in_edit, 0, 1)
        security_layout.addWidget(QLabel("Deny extensions (IN mirror)"), 1, 0)
        security_layout.addWidget(self._deny_ext_in_edit, 1, 1)
        security_layout.addWidget(QLabel("Allow paths (IN mirror)"), 2, 0)
        security_layout.addWidget(self._allow_paths_in_edit, 2, 1)
        security_layout.addWidget(QLabel("Deny paths (IN mirror)"), 3, 0)
        security_layout.addWidget(self._deny_paths_in_edit, 3, 1)
        security_layout.addWidget(QLabel("Allow extensions (Diagnostics)"), 4, 0)
        security_layout.addWidget(self._allow_ext_diag_edit, 4, 1)
        security_layout.addWidget(QLabel("Deny extensions (Diagnostics)"), 5, 0)
        security_layout.addWidget(self._deny_ext_diag_edit, 5, 1)
        security_layout.addWidget(QLabel("Allow paths (Diagnostics)"), 6, 0)
        security_layout.addWidget(self._allow_paths_diag_edit, 6, 1)
        security_layout.addWidget(QLabel("Deny paths (Diagnostics)"), 7, 0)
        security_layout.addWidget(self._deny_paths_diag_edit, 7, 1)

        self._secret_scan_checkbox = QCheckBox("Secret scanner před uploadem")
        self._secret_scan_checkbox.setChecked(settings.secret_scan_enabled)
        self._allow_sensitive_checkbox = QCheckBox("Povolit upload citlivých souborů")
        self._allow_sensitive_checkbox.setChecked(settings.allow_sensitive_uploads)
        self._encryption_key_edit = QLineEdit(settings.log_encryption_key)
        self._encryption_key_edit.setEchoMode(QLineEdit.Password)
        self._encryption_key_edit.setPlaceholderText("Volitelný klíč pro šifrování logů")
        self._panic_include_logs = QCheckBox("Při panic wipe také odebrat logy")
        self._panic_include_logs.setChecked(settings.panic_wipe_include_logs)
        self._panic_wipe_button = QPushButton("Spustit panic wipe")
        self._panic_wipe_button.clicked.connect(self._on_panic_wipe_clicked)

        security_layout.addWidget(self._secret_scan_checkbox, 8, 0, 1, 2)
        security_layout.addWidget(self._allow_sensitive_checkbox, 9, 0, 1, 2)
        security_layout.addWidget(QLabel("Šifrovací klíč (volitelný)"), 10, 0)
        security_layout.addWidget(self._encryption_key_edit, 10, 1)
        security_layout.addWidget(self._panic_include_logs, 11, 0, 1, 2)
        security_layout.addWidget(self._panic_wipe_button, 12, 0, 1, 2)

        self._dry_run_checkbox = QCheckBox("Dry-run pro MODIFY (C1)")
        self._dry_run_checkbox.setChecked(settings.dry_run_modify)
        self._local_hooks_edit = QPlainTextEdit(self._list_to_text(settings.local_post_hooks))
        self._ssh_hooks_edit = QPlainTextEdit(self._list_to_text(settings.ssh_post_hooks))
        for edit in (self._local_hooks_edit, self._ssh_hooks_edit):
            edit.setPlaceholderText("Příkaz na řádek; prázdný řádek odděluje další hook")
            edit.setFixedHeight(80)
        dev_group = QGroupBox("Vývojářský workflow (C1–C3)")
        dev_layout = QGridLayout()
        dev_group.setLayout(dev_layout)
        dev_layout.addWidget(self._dry_run_checkbox, 0, 0, 1, 2)
        dev_layout.addWidget(QLabel("Lokální post-run hooky (test/lint/format)"), 1, 0)
        dev_layout.addWidget(self._local_hooks_edit, 1, 1)
        dev_layout.addWidget(QLabel("SSH post-run hooky (vyžaduje SSH)"), 2, 0)
        dev_layout.addWidget(self._ssh_hooks_edit, 2, 1)

        scroll_layout.addLayout(form)
        scroll_layout.addWidget(security_group)
        scroll_layout.addWidget(dev_group)
        scroll_area.setWidget(scroll_container)
        layout.addWidget(scroll_area)

        buttons = QHBoxLayout()
        save_button = QPushButton("ULOZIT")
        cancel_button = QPushButton("STORNO")
        buttons.addWidget(save_button)
        buttons.addWidget(cancel_button)
        layout.addLayout(buttons)

        save_button.clicked.connect(self._on_save)
        cancel_button.clicked.connect(self.reject)

    def _on_save(self) -> None:
        self._settings.db_path = self._db_path.text().strip()
        self._settings.log_max_runs = int(self._log_max_runs.value())
        self._settings.log_max_size_mb = int(self._log_max_size.value())
        self._settings.retry_max_attempts = int(self._retry_attempts.value())
        self._settings.retry_max_delay_sec = int(self._retry_delay.value())
        self._settings.pricing_url = self._pricing_url.text().strip()
        self._settings.pricing_cache_ttl_min = int(self._pricing_ttl.value())
        self._settings.pricing_auto_refresh = self._auto_refresh.isChecked()
        self._settings.mask_secrets = self._mask_secrets.isChecked()
        self._settings.encrypt_logs = self._encrypt_logs.isChecked()
        self._settings.admin_username = self._admin_username.text().strip()
        self._settings.admin_password = self._admin_password.text()
        self._settings.ssh_host = self._ssh_host.text().strip()
        self._settings.ssh_port = int(self._ssh_port.value())
        self._settings.ssh_user = self._ssh_user.text().strip()
        self._settings.ssh_key_path = self._ssh_key.text().strip()
        self._settings.ssh_password = self._ssh_password.text()
        self._settings.diagnostics_acknowledged = self._diagnostics_acknowledged
        self._settings.batch_poll_interval_sec = int(self._batch_poll_interval.value())
        self._settings.batch_timeout_sec = int(self._batch_timeout.value())
        self._settings.default_model = self._default_model.text().strip()
        self._settings.default_temperature = float(self._default_temperature.value())
        self._settings.allow_extensions_in = self._list_from_edit(self._allow_ext_in_edit)
        self._settings.deny_extensions_in = self._list_from_edit(self._deny_ext_in_edit)
        self._settings.allow_paths_in = self._list_from_edit(self._allow_paths_in_edit)
        self._settings.deny_paths_in = self._list_from_edit(self._deny_paths_in_edit)
        self._settings.allow_extensions_diag = self._list_from_edit(self._allow_ext_diag_edit)
        self._settings.deny_extensions_diag = self._list_from_edit(self._deny_ext_diag_edit)
        self._settings.allow_paths_diag = self._list_from_edit(self._allow_paths_diag_edit)
        self._settings.deny_paths_diag = self._list_from_edit(self._deny_paths_diag_edit)
        self._settings.secret_scan_enabled = self._secret_scan_checkbox.isChecked()
        self._settings.allow_sensitive_uploads = self._allow_sensitive_checkbox.isChecked()
        self._settings.log_encryption_key = self._encryption_key_edit.text().strip()
        self._settings.panic_wipe_include_logs = self._panic_include_logs.isChecked()
        self._settings.dry_run_modify = self._dry_run_checkbox.isChecked()
        self._settings.local_post_hooks = self._list_from_edit(self._local_hooks_edit)
        self._settings.ssh_post_hooks = self._list_from_edit(self._ssh_hooks_edit)
        self.accept()

    def _update_diag_ack_label(self) -> None:
        if self._diagnostics_acknowledged:
            self._diag_warning_status.setText("Varování potvrzeno")
            self._diag_warning_status.setStyleSheet("color: #fff; font-weight: bold;")
        else:
            self._diag_warning_status.setText("Varování nepotvrzeno")
            self._diag_warning_status.setStyleSheet("color: #888; font-weight: bold;")

    def _show_diag_warning(self) -> None:
        text = (
            "Diagnostické snapshoty mohou obsahovat velmi citlivá data. "
            "Potvrďte, že s jejich záznamem a uložením v logu souhlasíte."
        )
        result = QMessageBox.warning(
            self,
            "Varování diagnostiky",
            text,
            QMessageBox.Ok | QMessageBox.Cancel,
        )
        if result == QMessageBox.Ok:
            self._diagnostics_acknowledged = True
            self._update_diag_ack_label()

    def _reset_diag_warning(self) -> None:
        self._diagnostics_acknowledged = False
        self._update_diag_ack_label()

    def _browse_ssh_key(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Vybrat SSH klíč", "", "SSH keys (*.pem *.ppk *.key);;Všechny soubory (*)"
        )
        if path:
            self._ssh_key.setText(path)

    @property
    def settings(self) -> Settings:
        return self._settings

    @staticmethod
    def _list_to_text(items: Iterable[str]) -> str:
        return "\n".join(items)

    def _list_from_edit(self, edit: QPlainTextEdit) -> List[str]:
        return [line.strip() for line in edit.toPlainText().splitlines() if line.strip()]

    def _on_panic_wipe_clicked(self) -> None:
        if self._panic_callback:
            self._panic_callback(self._panic_include_logs.isChecked())
