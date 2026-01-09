from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from PySide6.QtCore import Property, QEasingCurve, QPropertyAnimation, Qt, QSize, Signal, QRectF
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFontDatabase,
    QPainter,
    QPen,
)
from PySide6.QtWidgets import QWidget, QSizePolicy


@dataclass
class _Palette:
    # Styl dle reference (výjimka oproti BW+R): zelená pro ON
    track_off: QColor = field(default_factory=lambda: QColor(185, 185, 190))  # šedá lišta
    track_on: QColor = field(default_factory=lambda: QColor(120, 200, 80))     # zelená lišta
    knob: QColor = field(default_factory=lambda: QColor(240, 240, 240))        # bílý knoflík
    knob_ring: QColor = field(default_factory=lambda: QColor(210, 210, 210))   # jemný okraj knoflíku
    shadow: QColor = field(default_factory=lambda: QColor(0, 0, 0, 70))        # stín
    disabled_overlay: QColor = field(default_factory=lambda: QColor(0, 0, 0, 90))  # ztmavení


class RockerSwitch(QWidget):
    """
    KÁJOVO UI LIB
    COMPONENT: ROCKER SWITCH (2-state, always one selected) – TOGGLE STYLE (příloha)
    FILE:      components/rocker_switch.py
    VERSION:   v0.3 (redesign per reference)

    Účel použití:
      - pouze pro volbu mezi DVĚMA možnostmi
      - vždy musí být zvolena alespoň jedna možnost (binární stav ON/OFF)

    Vzhled:
      - kapslová lišta + kulatý knoflík (toggle)
      - OFF: šedá lišta, knoflík vlevo
      - ON: zelená lišta, knoflík vpravo

    API:
      - set_checked(bool)
      - is_checked() -> bool
      - toggled(bool) [signal]
      - set_on_color(QColor)
      - set_off_color(QColor)
    """

    toggled = Signal(bool)

    _fonts_loaded = False

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.setMinimumSize(64, 36)
        self.setAttribute(Qt.WA_OpaquePaintEvent, False)
        self.setFocusPolicy(Qt.StrongFocus)

        self._ensure_fonts_loaded()

        self._checked: bool = False
        self._hover: bool = False
        self._pressed: bool = False

        self._pal = _Palette()

        # animation 0..1
        self._a: float = 0.0
        self._anim = QPropertyAnimation(self, b"animValue", self)
        self._anim.setDuration(150)
        self._anim.setEasingCurve(QEasingCurve.InOutCubic)

    # ---------------- Qt sizing ----------------

    def sizeHint(self) -> QSize:
        return QSize(92, 44)

    def minimumSizeHint(self) -> QSize:
        return QSize(64, 36)

    # ---------------- Public API ----------------

    def set_checked(self, value: bool) -> None:
        v = bool(value)
        if v == self._checked:
            return
        self._checked = v
        self._animate_to(1.0 if self._checked else 0.0)
        self.toggled.emit(self._checked)
        self.update()

    def is_checked(self) -> bool:
        return bool(self._checked)

    def set_on_color(self, color: QColor) -> None:
        if isinstance(color, QColor):
            self._pal.track_on = QColor(color)
            self.update()

    def set_off_color(self, color: QColor) -> None:
        if isinstance(color, QColor):
            self._pal.track_off = QColor(color)
            self.update()

    # Qt-ish aliases
    def setChecked(self, value: bool) -> None:  # noqa: N802
        self.set_checked(value)

    def isChecked(self) -> bool:  # noqa: N802
        return self.is_checked()

    # ---------------- Internals ----------------

    @classmethod
    def _ensure_fonts_loaded(cls) -> None:
        # komponenta font nepotřebuje, ale držíme hook kvůli konzistenci knihovny
        if cls._fonts_loaded:
            return
        try:
            base = Path(__file__).resolve().parent.parent / "resources"
            reg = base / "montserrat_regular.ttf"
            if reg.exists():
                QFontDatabase.addApplicationFont(str(reg))
        except Exception:
            pass
        cls._fonts_loaded = True

    def _animate_to(self, target: float) -> None:
        self._anim.stop()
        self._anim.setStartValue(float(self._a))
        self._anim.setEndValue(float(target))
        self._anim.start()

    def _toggle(self) -> None:
        if not self.isEnabled():
            return
        self.set_checked(not self._checked)

    # ---------------- Animation property ----------------

    def _get_anim(self) -> float:
        return float(self._a)

    def _set_anim(self, v: float) -> None:
        self._a = max(0.0, min(1.0, float(v)))
        self.update()

    animValue = Property(float, _get_anim, _set_anim)  # noqa: N815

    # ---------------- Events ----------------

    def enterEvent(self, _e) -> None:
        self._hover = True
        self.update()

    def leaveEvent(self, _e) -> None:
        self._hover = False
        self._pressed = False
        self.update()

    def mousePressEvent(self, e) -> None:
        if e.button() == Qt.LeftButton and self.isEnabled():
            self._pressed = True
            self.update()
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e) -> None:
        if e.button() == Qt.LeftButton:
            was_pressed = self._pressed
            self._pressed = False
            if was_pressed and self.rect().contains(e.position().toPoint()):
                self._toggle()
            self.update()
        super().mouseReleaseEvent(e)

    def keyPressEvent(self, e) -> None:
        if e.key() in (Qt.Key_Space, Qt.Key_Return, Qt.Key_Enter):
            self._toggle()
            e.accept()
            return
        super().keyPressEvent(e)

    # ---------------- Paint ----------------

    @staticmethod
    def _lerp(a: float, b: float, t: float) -> float:
        return a + (b - a) * t

    @staticmethod
    def _mix(c1: QColor, c2: QColor, t: float) -> QColor:
        t = max(0.0, min(1.0, float(t)))
        return QColor(
            int(c1.red() + (c2.red() - c1.red()) * t),
            int(c1.green() + (c2.green() - c1.green()) * t),
            int(c1.blue() + (c2.blue() - c1.blue()) * t),
            int(c1.alpha() + (c2.alpha() - c1.alpha()) * t),
        )

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        w = float(self.width())
        h = float(self.height())
        if w < 8 or h < 8:
            return

        # Transparent background (component should sit on any surface)
        p.setPen(Qt.NoPen)
        p.setBrush(Qt.NoBrush)

        size = min(w, h)

        # geometry (toggle: wider than tall)
        pad = max(1.0, size * 0.08)
        track_h = max(10.0, h - 2 * pad)
        track_h = min(track_h, h * 0.82)
        track_w = max(track_h * 1.80, w - 2 * pad)

        # center it
        tx = (w - track_w) * 0.5
        ty = (h - track_h) * 0.5

        r = track_h * 0.5
        track = QRectF(tx, ty, track_w, track_h)

        # knob geometry (slightly bigger than track height in ref)
        knob_d = track_h * 0.92
        knob_r = knob_d * 0.5

        # knob travel range
        left_x = tx + r - knob_r
        right_x = (tx + track_w - r) - knob_r
        kx = self._lerp(left_x, right_x, self._a)
        ky = ty + (track_h - knob_d) * 0.5
        knob = QRectF(kx, ky, knob_d, knob_d)

        # subtle press = move knob 1px down (mechanical)
        if self._pressed and self.isEnabled():
            knob.translate(0.0, max(1.0, track_h * 0.04))

        # track color blend by animation (makes transition smooth)
        track_col = self._mix(self._pal.track_off, self._pal.track_on, self._a)

        # hover = slightly brighten track (still faithful)
        if self._hover and self.isEnabled():
            track_col = self._mix(track_col, QColor(255, 255, 255), 0.10)

        # draw track
        p.setBrush(QBrush(track_col))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(track, r, r)

        # track inner highlight (thin, top)
        hi = QColor(255, 255, 255, 55 if self.isEnabled() else 35)
        pen_hi = QPen(hi, max(1.0, size * 0.018))
        pen_hi.setCapStyle(Qt.RoundCap)
        p.setPen(pen_hi)
        p.setBrush(Qt.NoBrush)
        p.drawLine(
            int(track.left() + r * 0.65),
            int(track.top() + r * 0.55),
            int(track.right() - r * 0.65),
            int(track.top() + r * 0.55),
        )

        # knob shadow
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(self._pal.shadow))
        shadow = QRectF(knob)
        shadow.translate(max(1.0, size * 0.02), max(1.0, size * 0.02))
        p.drawEllipse(shadow)

        # knob face
        p.setBrush(QBrush(self._pal.knob))
        p.setPen(QPen(self._pal.knob_ring, max(1.0, size * 0.02)))
        p.drawEllipse(knob)

        # knob highlight (small specular)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(255, 255, 255, 120)))
        spec = QRectF(knob)
        spec.setWidth(knob.width() * 0.35)
        spec.setHeight(knob.height() * 0.35)
        spec.moveTo(knob.left() + knob.width() * 0.22, knob.top() + knob.height() * 0.18)
        p.drawEllipse(spec)

        # disabled overlay (dim everything)
        if not self.isEnabled():
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(self._pal.disabled_overlay))
            p.drawRoundedRect(track, r, r)

        # focus (thin white dashed outside)
        if self.hasFocus() and self.isEnabled():
            foc = QPen(QColor(255, 255, 255, 90), max(1.0, size * 0.02), Qt.DashLine)
            foc.setCapStyle(Qt.RoundCap)
            foc.setJoinStyle(Qt.RoundJoin)
            p.setPen(foc)
            p.setBrush(Qt.NoBrush)
            out = QRectF(track)
            out.adjust(-pad * 0.6, -pad * 0.6, pad * 0.6, pad * 0.6)
            p.drawRoundedRect(out, out.height() * 0.5, out.height() * 0.5)
