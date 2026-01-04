from __future__ import annotations

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget


class SectionCard(QFrame):
    def __init__(self, title: str, content: QWidget, parent=None):
        super().__init__(parent)
        self.setObjectName("sectionCard")
        layout = QVBoxLayout(self)
        header = QLabel(title)
        header.setObjectName("sectionTitle")
        layout.addWidget(header)
        layout.addWidget(content)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
