from __future__ import annotations

from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QColor, QFont, QFontMetrics, QPainter, QPen
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget


class SectionCard(QFrame):
    def __init__(self, title: str, content: QWidget, parent=None):
        super().__init__(parent)
        self.setObjectName("sectionCard")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background:#010101;")
        self._border_radius = 12
        layout = QVBoxLayout(self)
        header_row = QHBoxLayout()
        header_row.setContentsMargins(0, 0, 0, 0)
        header_row.setSpacing(6)
        self._header_label = QLabel(title.upper())
        self._header_label.setObjectName("sectionTitle")
        self._header_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._header_label.setStyleSheet("color:#fff; border:none;")
        self._header_label.setFont(QFont("Montserrat", 12, QFont.Bold))
        header_row.addWidget(self._header_label)
        header_row.addStretch()
        layout.addLayout(header_row)
        layout.addWidget(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

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

        if not self._header_label:
            return
        gap = self._gap_width()
        label_pos = self._header_label.mapTo(self, QPoint(0, 0))
        label_left = label_pos.x()
        label_right = label_left + self._header_label.width()
        gap_start = max(rect.left() + self._border_radius, label_left - gap)
        gap_end = min(rect.right() - self._border_radius, label_right + gap)

        if gap_end > gap_start:
            fill_rect = QRect(
                gap_start,
                rect.top(),
                max(1, gap_end - gap_start),
                self._border_radius,
            )
            painter.fillRect(fill_rect, QColor("#010101"))
        left_end = gap_start
        right_start = gap_end
        if left_end > rect.left() + self._border_radius:
            painter.drawLine(rect.left() + self._border_radius, rect.top(), left_end, rect.top())
        if right_start < rect.right() - self._border_radius:
            painter.drawLine(
                right_start,
                rect.top(),
                rect.right() - self._border_radius,
                rect.top(),
            )

    def _gap_width(self) -> int:
        metrics = QFontMetrics(self._header_label.font())
        return max(8, metrics.horizontalAdvance("A"))
