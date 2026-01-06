import logging
import sys
from pathlib import Path

from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication

from kaja.ui.main_window import MainWindow
from tmp_write_settings import ensure_settings_file

LOGGER = logging.getLogger(__name__)


def _is_valid_font(font_path: Path) -> bool:
    try:
        header = font_path.read_bytes()[:4]
    except OSError as exc:
        LOGGER.warning("Unable to read font %s: %s", font_path.name, exc)
        return False
    return header in (b"\x00\x01\x00\x00", b"OTTO")


def _register_fonts(root: Path) -> None:
    fonts = [
        root / "resources" / "montserrat_regular.ttf",
        root / "resources" / "montserrat_bold.ttf",
    ]
    for font in fonts:
        if not font.exists():
            LOGGER.warning("Missing font %s; continue in degraded mode.", font.name)
            continue
        if not _is_valid_font(font):
            LOGGER.warning(
                "%s is not a valid TrueType/OpenType file; skipping registration.",
                font.name,
            )
            continue
        font_id = QFontDatabase.addApplicationFont(str(font))
        if font_id == -1:
            LOGGER.warning("Failed to register font %s; skipping.", font.name)
        else:
            LOGGER.info("Registered font %s with id %d", font.name, font_id)


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="Kája: %(levelname)s: %(message)s")
    project_root = Path(__file__).resolve().parent
    ensure_settings_file(project_root)
    app = QApplication(sys.argv)
    _register_fonts(project_root)
    window = MainWindow()
    window.showMaximized()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
