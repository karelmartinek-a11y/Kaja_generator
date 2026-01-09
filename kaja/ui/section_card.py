from __future__ import annotations

from PySide6.QtCore import QPoint, QMargins, QRect, Qt
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPen
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout, QWidget

from .style_tokens import KJA_BORDER_PX, KJA_RADIUS, PALETTE_BLACK, PALETTE_WHITE


class SectionCard(QFrame):
    def __init__(self, title: str, content: QWidget, parent=None):
        super().__init__(parent)
        self.setObjectName("sectionCard")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"background:{PALETTE_BLACK};")
        self._border_radius = KJA_RADIUS
        self._header_label = QLabel(title.upper(), self)
        self._header_label.setObjectName("sectionTitle")
        self._header_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._header_label.setStyleSheet(
            f"color:{PALETTE_WHITE}; border:none; background:{PALETTE_BLACK}; padding:0;"
        )
        self._header_label.setFont(QFont("Montserrat", 12, QFont.Bold))
        self._header_label.raise_()

        self._title_band = self._header_label.sizeHint().height()
        layout = QVBoxLayout(self)
        layout.addWidget(content)
        layout.setContentsMargins(0, self._title_band + 6, 0, 0)
        layout.setSpacing(6)
        self._position_title()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._position_title()

    def _gap_width(self) -> int:
        metrics = QFontMetrics(self._header_label.font())
        return metrics.horizontalAdvance("A")

    def _position_title(self) -> None:
        if not self._header_label:
            return
        m = self.layout().contentsMargins() if self.layout() else QMargins()
        left_margin = max(self._border_radius, m.left())
        right_margin = max(self._border_radius, m.right())
        available = max(0, self.width() - left_margin - right_margin)
        hint = self._header_label.sizeHint()
        width = min(hint.width(), available)
        height = hint.height()
        top_line = self._title_band // 2
        y = max(0, top_line - height // 2)
        self._header_label.setGeometry(left_margin, y, width, height)
