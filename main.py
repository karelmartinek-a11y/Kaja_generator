import sys
from pathlib import Path

from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication

from kaja.ui.main_window import MainWindow
from tmp_write_settings import ensure_settings_file


def _register_fonts(root: Path) -> None:
    fonts = [
        root / "resources" / "montserrat_regular.ttf",
        root / "resources" / "montserrat_bold.ttf",
    ]
    for font in fonts:
        if font.exists():
            QFontDatabase.addApplicationFont(str(font))


def main() -> int:
    project_root = Path(__file__).resolve().parent
    ensure_settings_file(project_root)
    _register_fonts(project_root)
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
