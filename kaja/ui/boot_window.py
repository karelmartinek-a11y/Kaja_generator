from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import List

from PySide6.QtCore import QPointF, Qt, QTimer
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QPushButton, QStackedLayout, QVBoxLayout, QWidget


@dataclass
class LetterParticle:
    char: str
    position: QPointF
    velocity: QPointF


class VortexLettersWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._letters: List[LetterParticle] = []
        self._timer = QTimer(self)
        self._timer.setInterval(16)
        self._timer.timeout.connect(self._tick)
        self._font = QFont("Montserrat", 22, QFont.Bold)
        self.setFocusPolicy(Qt.NoFocus)

    def start(self) -> None:
        if not self._letters:
            self._spawn_letters()
        if not self._timer.isActive():
            self._timer.start()

    def stop(self) -> None:
        if self._timer.isActive():
            self._timer.stop()

    def _spawn_letters(self) -> None:
        width = max(self.width(), 1)
        height = max(self.height(), 1)
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        self._letters = []
        for _ in range(140):
            pos = QPointF(random.uniform(0, width), random.uniform(0, height))
            vel = QPointF(random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5))
            self._letters.append(LetterParticle(random.choice(alphabet), pos, vel))

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        if not self._letters:
            self._spawn_letters()
        super().resizeEvent(event)

    def _tick(self) -> None:
        if not self._letters:
            self._spawn_letters()
        center = QPointF(self.width() * 0.5, self.height() * 0.5)
        for letter in self._letters:
            dx = letter.position.x() - center.x()
            dy = letter.position.y() - center.y()
            distance = math.hypot(dx, dy) or 1.0
            pull_strength = -0.03
            tangent_strength = 0.18
            pull = QPointF(pull_strength * dx / distance, pull_strength * dy / distance)
            tangent = QPointF(-tangent_strength * dy / distance, tangent_strength * dx / distance)
            jitter = QPointF(random.uniform(-0.05, 0.05), random.uniform(-0.05, 0.05))
            letter.velocity += pull + tangent + jitter
            letter.position += letter.velocity
            if letter.position.x() < -20 or letter.position.x() > self.width() + 20:
                letter.position.setX((letter.position.x() + self.width()) % self.width())
            if letter.position.y() < -20 or letter.position.y() > self.height() + 20:
                letter.position.setY((letter.position.y() + self.height()) % self.height())
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("black"))
        painter.setPen(QColor("#f0f0f0"))
        painter.setFont(self._font)
        for letter in self._letters:
            painter.drawText(letter.position, letter.char)


class BootTerminalWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._base_text = "BOOT: Všechna data z počítače odstraněna"
        self._typed_text = ""
        self._cursor_visible = True
        self._cursor_timer = QTimer(self)
        self._cursor_timer.setInterval(500)
        self._cursor_timer.timeout.connect(self._toggle_cursor)
        self._font = QFont("Courier New", 20)
        self.setFocusPolicy(Qt.StrongFocus)

    def showEvent(self, event) -> None:  # type: ignore[override]
        self._cursor_timer.start()
        self.setFocus(Qt.ActiveWindowFocusReason)
        super().showEvent(event)

    def hideEvent(self, event) -> None:  # type: ignore[override]
        self._cursor_timer.stop()
        super().hideEvent(event)

    def _toggle_cursor(self) -> None:
        self._cursor_visible = not self._cursor_visible
        self.update()

    def keyPressEvent(self, event) -> None:  # type: ignore[override]
        text = event.text()
        if text and text.isprintable():
            self._typed_text += text
            self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("black"))
        painter.setFont(self._font)
        painter.setPen(QColor("#00ff66"))
        cursor = "_" if self._cursor_visible else " "
        full_text = f"{self._base_text}{self._typed_text}{cursor}"
        margin = 24
        painter.drawText(margin, self.height() - margin, full_text)


class BootScreenWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Kaja")
        self._stack = QStackedLayout()

        self._intro_widget = QWidget(self)
        intro_layout = QVBoxLayout(self._intro_widget)
        intro_layout.setContentsMargins(0, 0, 0, 0)
        intro_layout.setAlignment(Qt.AlignCenter)
        intro_layout.addSpacing(10)

        button = QPushButton("PUSH")
        button.setFixedSize(320, 140)
        button.setStyleSheet(
            "QPushButton { background-color: #cc0000; color: white; font-size: 36px; "
            "font-weight: bold; border-radius: 12px; }"
            "QPushButton:pressed { background-color: #990000; }"
        )
        button.clicked.connect(self._start_sequence)

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        button_row.addWidget(button)
        button_row.addStretch(1)
        intro_layout.addLayout(button_row)

        self._letters_widget = VortexLettersWidget(self)
        self._terminal_widget = BootTerminalWidget(self)

        self._stack.addWidget(self._intro_widget)
        self._stack.addWidget(self._letters_widget)
        self._stack.addWidget(self._terminal_widget)

        container = QWidget(self)
        container.setLayout(self._stack)
        container.setStyleSheet("background-color: black;")
        self.setCentralWidget(container)

        self._sequence_timer = QTimer(self)
        self._sequence_timer.setSingleShot(True)
        self._sequence_timer.timeout.connect(self._show_terminal)

    def _start_sequence(self) -> None:
        if self._sequence_timer.isActive():
            return
        self._stack.setCurrentWidget(self._letters_widget)
        self._letters_widget.start()
        self._sequence_timer.start(10_000)

    def _show_terminal(self) -> None:
        self._letters_widget.stop()
        self._stack.setCurrentWidget(self._terminal_widget)
