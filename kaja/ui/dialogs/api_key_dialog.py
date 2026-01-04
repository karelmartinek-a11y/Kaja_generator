from __future__ import annotations

import os
import subprocess

from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout


class ApiKeyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("API-KEY")
        layout = QVBoxLayout(self)

        self._input = QLineEdit()
        self._input.setEchoMode(QLineEdit.Password)
        layout.addWidget(QLabel("OpenAI API key"))
        layout.addWidget(self._input)

        button_row = QHBoxLayout()
        save_button = QPushButton("ULOZIT")
        show_button = QPushButton("ZOBRAZ")
        delete_button = QPushButton("SMAZAT")
        cancel_button = QPushButton("STORNO")
        button_row.addWidget(save_button)
        button_row.addWidget(show_button)
        button_row.addWidget(delete_button)
        button_row.addWidget(cancel_button)
        layout.addLayout(button_row)

        save_button.clicked.connect(self._save_key)
        show_button.clicked.connect(self._show_key)
        delete_button.clicked.connect(self._delete_key)
        cancel_button.clicked.connect(self.reject)

    def _save_key(self) -> None:
        api_key = self._input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "API-KEY", "Zadejte API key.")
            return
        os.environ["OPENAI_API_KEY"] = api_key
        success = _set_system_env("OPENAI_API_KEY", api_key)
        if not success:
            QMessageBox.warning(
                self,
                "API-KEY",
                "Nepodarilo se ulozit do registru uzivatele; pouziva se jen pro tento beh.",
            )
        else:
            QMessageBox.information(self, "API-KEY", "API key ulozen.")
            self.accept()

    def _show_key(self) -> None:
        key = os.environ.get("OPENAI_API_KEY", "")
        if not key:
            QMessageBox.warning(self, "API-KEY", "API key neni ulozen.")
            return
        self._input.setText(key)
        self._input.setEchoMode(QLineEdit.Normal)

    def _delete_key(self) -> None:
        os.environ.pop("OPENAI_API_KEY", None)
        _set_system_env("OPENAI_API_KEY", "")
        QMessageBox.information(self, "API-KEY", "API key smazan.")


def _set_system_env(key: str, value: str) -> bool:
    try:
        if value:
            result = subprocess.run(["setx", key, value], capture_output=True, text=True, check=False)
        else:
            result = subprocess.run(["setx", key, ""], capture_output=True, text=True, check=False)
        return result.returncode == 0
    except Exception:
        return False
