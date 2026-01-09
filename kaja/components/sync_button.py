from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QSize, QRectF, Signal
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QFontDatabase,
    QPainter,
    QPen,
)
from PySide6.QtWidgets import QWidget, QSizePolicy


@dataclass
class _Palette:
    bg: QColor
    fg: QColor
    border: QColor


class SyncButton(QWidget):
    """
    KÁJOVO UI LIB
    COMPONENT: SYNC BUTTON
    FILE:      components/sync_button.py
    VERSION:   v1.2 (dynamic sizing + aspect ratio lock)

    Varianty:
      - BW (black/white): má 2 výchozí režimy: INACTIVE a ACTIVE
      - RB (red/black): pouze ACTIVE

    ACTIVE stavy:
      - OFF (vypnuto)
      - ON (zapnuto)           -> inverze barev
      - PRESSED (stisknuto)    -> inverze barev

    Chování:
      - MODE_TOGGLE: klik přepíná OFF/ON, při držení je PRESSED
      - MODE_CONTACTOR: ON jen po dobu držení myši uvnitř; pustím/ujedu mimo -> OFF

    DYNAMICKÁ VELIKOST:
      - veškeré poměry (padding, radius, stroke, gap) jsou relativní k velikosti widgetu
      - font se vždy dopočítá tak, aby NIKDY nelezl do okraje (fit-to-box)
      - držení poměru stran (default ON) přes height-for-width
    """

    toggled = Signal(bool)
    pressedChanged = Signal(bool)
    clicked = Signal()

    VARIANT_BW = "bw"
    VARIANT_RB = "redblack"

    MODE_TOGGLE = "toggle"
    MODE_CONTACTOR = "contactor"

    _fonts_loaded = False
    _font_bold: Optional[str] = None

    def __init__(self, parent=None):
        super().__init__(parent)

        # umožni layoutu zužovat i zvětšovat (minimum -> může jít dolů pod sizeHint)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.setMinimumSize(24, 18)
        self.setAttribute(Qt.WA_OpaquePaintEvent, True)
        self.setMouseTracking(True)

        self._ensure_fonts_loaded()

        self._text = "SYNC"
        self._variant = self.VARIANT_BW

        # "výchozí stavy" pro BW: inactive/active (availability)
        self._inactive = False

        # active sub-states
        self._on = False
        self._pressed = False
        self._mouse_inside = False

        self._mode = self.MODE_TOGGLE

        # poměr stran (šířka/výška). Vychozí podle sizeHint: 160/64 = 2.5
        self._aspect_ratio = 160.0 / 64.0
        self._aspect_lock = True
        self._checkable = False

    # ---------------- Qt sizing ----------------

    def sizeHint(self) -> QSize:
        return QSize(160, 64)

    def minimumSizeHint(self) -> QSize:
        return QSize(24, 18)

    def hasHeightForWidth(self) -> bool:
        return bool(self._aspect_lock)

    def heightForWidth(self, w: int) -> int:
        if not self._aspect_lock:
            return super().heightForWidth(w)
        ww = max(1, int(w))
        h = int(round(ww / max(0.0001, float(self._aspect_ratio))))
        return max(1, h)

    def set_aspect_lock(self, enabled: bool) -> None:
        self._aspect_lock = bool(enabled)
        self.updateGeometry()
        self.update()

    def set_aspect_ratio(self, width_over_height: float) -> None:
        r = float(width_over_height)
        if r <= 0:
            return
        self._aspect_ratio = r
        self.updateGeometry()
        self.update()

    # ---------------- Public API ----------------

    def set_text(self, text: str) -> None:
        self._text = str(text).strip() if text is not None else ""
        self.update()

    def set_variant(self, variant: str) -> None:
        v = str(variant).strip().lower()
        if v not in (self.VARIANT_BW, self.VARIANT_RB):
            return
        self._variant = v

        # RB nemá inactive režim (vždy active)
        if self._variant == self.VARIANT_RB:
            self._inactive = False

        self.update()

    def set_inactive(self, inactive: bool) -> None:
        """
        Platí jen pro BW. Pokud je inactive=True:
          - žádné další stavy
          - žádná interakce
        """
        if self._variant != self.VARIANT_BW:
            self._inactive = False
            return
        self._inactive = bool(inactive)
        if self._inactive:
            self._on = False
            self._pressed = False
        self.update()

    def set_mode(self, mode: str) -> None:
        m = str(mode).strip().lower()
        if m not in (self.MODE_TOGGLE, self.MODE_CONTACTOR):
            return
        self._mode = m
        self._checkable = self._mode == self.MODE_TOGGLE

        # při přepnutí do contactoru nechceme zůstat "zapnuté"
        if self._mode == self.MODE_CONTACTOR:
            self._set_on(False, emit=True)
        self.update()

    def setCheckable(self, checkable: bool) -> None:
        desired = bool(checkable)
        self._checkable = desired
        self.set_mode(self.MODE_TOGGLE if desired else self.MODE_CONTACTOR)

    def isCheckable(self) -> bool:
        return bool(self._checkable)

    def setChecked(self, checked: bool) -> None:
        self.set_on(bool(checked))

    def isChecked(self) -> bool:
        return self.is_on()

    def setText(self, text: str) -> None:
        self.set_text(text)

    def text(self) -> str:
        return self._text

    def set_on(self, on: bool) -> None:
        """Programové nastavení (primárně pro MODE_TOGGLE)."""
        if self._inactive:
            return
        self._set_on(bool(on), emit=True)
        self.update()

    def is_on(self) -> bool:
        return bool(self._on)

    def is_inactive(self) -> bool:
        return bool(self._inactive)

    def click(self) -> None:
        if self._inactive:
            return
        if self._mode == self.MODE_TOGGLE:
            self._set_on(not self._on, emit=True)
        self.update()
        self.clicked.emit()

    # ---------------- Internals ----------------

    @classmethod
    def _ensure_fonts_loaded(cls) -> None:
        if cls._fonts_loaded:
            return
        try:
            base = Path(__file__).resolve().parent.parent / "resources"
            font_path_bold = base / "montserrat_bold.ttf"
            if font_path_bold.exists():
                fid = QFontDatabase.addApplicationFont(str(font_path_bold))
                fams = QFontDatabase.applicationFontFamilies(fid)
                if fams:
                    cls._font_bold = fams[0]
        except Exception:
            pass
        cls._fonts_loaded = True

    def _set_on(self, on: bool, emit: bool) -> None:
        new_val = bool(on)
        if new_val == self._on:
            return
        self._on = new_val
        if emit:
            self.toggled.emit(self._on)

    def _set_pressed(self, pressed: bool, emit: bool) -> None:
        new_val = bool(pressed)
        if new_val == self._pressed:
            return
        self._pressed = new_val
        if emit:
            self.pressedChanged.emit(self._pressed)

    def _active_inverted(self) -> bool:
        return (not self._inactive) and (self._on or self._pressed)

    def _pal_active_normal(self) -> _Palette:
        if self._variant == self.VARIANT_RB:
            return _Palette(bg=QColor(0, 0, 0), fg=QColor(255, 0, 0), border=QColor(255, 0, 0))
        return _Palette(bg=QColor(0, 0, 0), fg=QColor(255, 255, 255), border=QColor(255, 255, 255))

    def _pal_active_inverted(self) -> _Palette:
        if self._variant == self.VARIANT_RB:
            return _Palette(bg=QColor(255, 0, 0), fg=QColor(0, 0, 0), border=QColor(255, 0, 0))
        return _Palette(bg=QColor(255, 255, 255), fg=QColor(0, 0, 0), border=QColor(255, 255, 255))

    def _pal_inactive(self) -> _Palette:
        return _Palette(bg=QColor(0, 0, 0), fg=QColor(255, 255, 255), border=QColor(255, 0, 0))

    def _fit_font_pixel_size(self, painter: QPainter, text: str, box: QRectF, target_px: float) -> int:
        margin = max(1.0, min(box.width(), box.height()) * 0.10)
        bw = max(1.0, box.width() - 2 * margin)
        bh = max(1.0, box.height() - 2 * margin)

        if not text:
            return 1

        base_font = QFont(self._font_bold) if self._font_bold else painter.font()
        base_font.setBold(True)
        base_font.setItalic(False)

        hi = max(1, int(target_px))
        lo = 1

        best = 1
        while lo <= hi:
            mid = (lo + hi) // 2
            f = QFont(base_font)
            f.setPixelSize(mid)
            painter.setFont(f)
            fm = painter.fontMetrics()

            tw = fm.horizontalAdvance(text)
            th = fm.height()

            if tw <= bw and th <= bh:
                best = mid
                lo = mid + 1
            else:
                hi = mid - 1

        return max(1, int(best))

    # ---------------- Events ----------------

    def enterEvent(self, _event) -> None:
        self._mouse_inside = True
        self.update()

    def leaveEvent(self, _event) -> None:
        self._mouse_inside = False

        if not self._inactive and self._mode == self.MODE_CONTACTOR:
            self._set_pressed(False, emit=True)
            self._set_on(False, emit=True)

        self.update()

    def mousePressEvent(self, event) -> None:
        if self._inactive:
            event.ignore()
            return
        if event.button() != Qt.LeftButton:
            event.ignore()
            return

        self._set_pressed(True, emit=True)

        if self._mode == self.MODE_CONTACTOR:
            self._set_on(True, emit=True)

        self.update()
        event.accept()

    def mouseReleaseEvent(self, event) -> None:
        if self._inactive:
            event.ignore()
            return
        if event.button() != Qt.LeftButton:
            event.ignore()
            return

        was_pressed = self._pressed
        self._set_pressed(False, emit=True)

        if self._mode == self.MODE_TOGGLE:
            if was_pressed and self._mouse_inside:
                self._set_on(not self._on, emit=True)
        else:
            self._set_on(False, emit=True)

        self.update()
        self.clicked.emit()
        event.accept()

    # ---------------- Paint ----------------

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setRenderHint(QPainter.TextAntialiasing, True)

        w = float(max(1, self.width()))
        h = float(max(1, self.height()))

        window_bg = QColor(0, 0, 0)
        p.fillRect(self.rect(), QBrush(window_bg))

        m = min(w, h)

        pad = m * 0.14
        r = QRectF(pad, pad, max(2.0, w - 2 * pad), max(2.0, h - 2 * pad))

        radius = min(r.height(), r.width()) * 0.22

        base = max(1.0, m * 0.055)
        stroke = max(1.0, base * 0.35)

        inverted = (not self._inactive) and self._active_inverted()

        if self._inactive:
            pal = self._pal_inactive()
        else:
            pal = self._pal_active_inverted() if inverted else self._pal_active_normal()

        if inverted:
            # 1) lem
            p.setPen(QPen(pal.border, stroke, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(r, radius, radius)

            # 2) gap
            gap = max(1.0, stroke * 0.55)
            r_gap = r.adjusted(stroke * 0.55, stroke * 0.55, -stroke * 0.55, -stroke * 0.55)
            p.setPen(QPen(window_bg, gap, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.setBrush(Qt.NoBrush)
            p.drawRoundedRect(
                r_gap,
                max(0.0, radius - stroke * 0.35),
                max(0.0, radius - stroke * 0.35),
            )

            # 3) fill
            inset = stroke + gap
            r_fill = r.adjusted(inset, inset, -inset, -inset)
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(pal.bg))
            p.drawRoundedRect(
                r_fill,
                max(0.0, radius - inset * 0.7),
                max(0.0, radius - inset * 0.7),
            )

            text_box = r_fill
        else:
            p.setPen(QPen(pal.border, stroke, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.setBrush(QBrush(pal.bg))
            p.drawRoundedRect(r, radius, radius)

            inset = stroke * 1.2
            text_box = r.adjusted(inset, inset, -inset, -inset)

        text = self._text
        target_px = max(1.0, r.height() * 0.40)
        px = self._fit_font_pixel_size(p, text, text_box, target_px)

        f = QFont(self._font_bold) if self._font_bold else p.font()
        f.setBold(True)
        f.setItalic(False)
        f.setPixelSize(px)
        p.setFont(f)

        p.setPen(QPen(pal.fg, max(1.0, stroke * 0.25)))
        fm = p.fontMetrics()

        tw = fm.horizontalAdvance(text)
        tx = text_box.center().x() - tw / 2.0
        ty = text_box.center().y() + fm.ascent() * 0.35

        p.drawText(int(tx), int(ty), text)
