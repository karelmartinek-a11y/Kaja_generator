import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from kaja.ui.main_window import MainWindow
from tmp_write_settings import ensure_settings_file


def main() -> int:
    ensure_settings_file(Path(__file__).resolve().parent)
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
