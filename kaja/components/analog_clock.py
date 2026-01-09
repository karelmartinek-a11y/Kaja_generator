import math
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QTimer, Qt, QPointF, QSize
from PySide6.QtGui import QBrush, QColor, QFont, QFontDatabase, QPainter, QPen
from PySide6.QtWidgets import QWidget, QSizePolicy


class AnalogClock(QWidget):
    """
    KÁJOVO UI LIB
    COMPONENT: ANALOG CLOCK
    VERSION:   MASTER v1.0 (candidate)

    - plně škálovatelný analogový ciferník
    - černobílý design (+ červená výjimka)
    - realistický střed ručiček + uchycení sekundové na trn
    - signatura "Kájovo" navázaná na geometrii ciferníku
    """

    _fonts_loaded = False
    _font_regular: str | None = None

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(60, 60)
        self.setAttribute(Qt.WA_OpaquePaintEvent, True)

        self._ensure_fonts_loaded()

        self._smooth_seconds = True
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.update)
        self._timer.start(16)

    # ---------------- Qt sizing API ----------------

    def sizeHint(self) -> QSize:
        return QSize(240, 240)

    def minimumSizeHint(self) -> QSize:
        return QSize(60, 60)

    # ---------------- Public API (demo compatibility) ----------------

    def set_fixed_time(self, dt: datetime | None) -> None:
        self.update()

    def set_smooth_seconds(self, enabled: bool) -> None:
        self._smooth_seconds = bool(enabled)
        self._timer.start(16 if enabled else 1000)
        self.update()

    # ---------------- Internals ----------------

    @classmethod
    def _ensure_fonts_loaded(cls) -> None:
        if cls._fonts_loaded:
            return
        try:
            base = Path(__file__).resolve().parent.parent / "resources"
            font_path = base / "montserrat_regular.ttf"
            if font_path.exists():
                fid = QFontDatabase.addApplicationFont(str(font_path))
                fams = QFontDatabase.applicationFontFamilies(fid)
                if fams:
                    cls._font_regular = fams[0]
        except Exception:
            pass
        cls._fonts_loaded = True

    @staticmethod
    def _angle(value: float, max_value: float) -> float:
        """0 je nahoře, směr po směru hodin"""
        return 2.0 * math.pi * (value / max_value) - (math.pi / 2.0)

    @staticmethod
    def _polar(cx: float, cy: float, r: float, a: float) -> QPointF:
        return QPointF(cx + math.cos(a) * r, cy + math.sin(a) * r)

    @staticmethod
    def _handwriting_font() -> str | None:
        for fam in (
            "Segoe Script",
            "Bradley Hand ITC",
            "Lucida Handwriting",
            "Brush Script MT",
            "Segoe Print",
            "Comic Sans MS",
        ):
            if QFontDatabase.hasFamily(fam):
                return fam
        return None

    # ---------------- Paint ----------------

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setRenderHint(QPainter.TextAntialiasing, True)

        w = float(self.width())
        h = float(self.height())
        size = min(w, h)

        # Background
        p.fillRect(self.rect(), QBrush(Qt.black))
        if size < 20:
            return

        # Global geometry
        cx, cy = w / 2.0, h / 2.0
        pad = size * 0.06
        r = (size / 2.0) - pad
        if r <= 2:
            return

        # Soft scale for extreme downsizing
        scale = max(0.45, min(1.0, size / 240.0))

        # ---------------------------------------------------------
        # Dial (outer circle)
        # ---------------------------------------------------------
        base_tick = max(0.8, size * 0.0030) * scale
        dial_pen = QPen(Qt.white, base_tick * 4.5)
        dial_pen.setCapStyle(Qt.RoundCap)
        dial_pen.setJoinStyle(Qt.RoundJoin)
        p.setPen(dial_pen)
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(cx, cy), r, r)

        # ---------------------------------------------------------
        # Index marks
        # ---------------------------------------------------------
        minute_len = r * 0.03 * 1.20
        hour_len = r * 0.045 * 1.20
        major_len = hour_len * 2.0

        pen_min = QPen(Qt.white, max(0.6, base_tick * 0.5))
        pen_hour = QPen(Qt.white, max(0.8, base_tick * 1.2))
        pen_min.setCapStyle(Qt.RoundCap)
        pen_hour.setCapStyle(Qt.RoundCap)

        for i in range(60):
            a = self._angle(i, 60.0)
            start = self._polar(cx, cy, r, a)

            if i % 5 == 0:
                p.setPen(pen_hour)
                ln = major_len if i in (0, 15, 30, 45) else hour_len
            else:
                p.setPen(pen_min)
                ln = minute_len

            end = self._polar(cx, cy, r - ln, a)
            p.drawLine(start, end)

        # ---------------------------------------------------------
        # Time
        # ---------------------------------------------------------
        now = datetime.now()
        sec = now.second + (now.microsecond / 1_000_000.0 if self._smooth_seconds else 0.0)
        minute = now.minute + sec / 60.0
        hour = (now.hour % 12) + minute / 60.0

        a_s = self._angle(sec, 60.0)
        a_m = self._angle(minute, 60.0)
        a_h = self._angle(hour, 12.0)

        # ---------------------------------------------------------
        # Hands geometry
        # ---------------------------------------------------------
        len_h = r * 0.56
        len_m = r * 0.80
        len_s = max(0.0, (r - major_len) - 1.0)  # pixel-precise

        w_h = max(0.9, size * 0.0040) * scale
        w_m = max(1.1, size * 0.0052) * scale
        w_s = max(1.0, size * 0.0042) * scale

        pen_h = QPen(Qt.white, w_h)
        pen_m = QPen(Qt.white, w_m)
        pen_s = QPen(QColor(255, 0, 0), w_s)
        for pen in (pen_h, pen_m, pen_s):
            pen.setCapStyle(Qt.RoundCap)
            pen.setJoinStyle(Qt.RoundJoin)

        # ---------------------------------------------------------
        # Central hub (realistic) + seconds spindle
        # ---------------------------------------------------------
        hub_r = max(5.0, size * 0.045) * 0.56

        # red rim (1 px)
        p.setPen(QPen(QColor(255, 0, 0), 1))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(cx, cy), hub_r + 1.0, hub_r + 1.0)

        # white washer
        washer_w = max(1.0, size * 0.0065) * scale
        p.setPen(QPen(Qt.white, washer_w))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(cx, cy), hub_r - 0.5, hub_r - 0.5)

        # black plug (base)
        plug_r = max(0.0, hub_r - washer_w * 0.9)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(Qt.black))
        p.drawEllipse(QPointF(cx, cy), plug_r, plug_r)

        # ---------------------------------------------------------
        # Draw hands (order)
        # ---------------------------------------------------------
        # hour
        p.setPen(pen_h)
        p.drawLine(QPointF(cx, cy), self._polar(cx, cy, len_h, a_h))

        # minute
        p.setPen(pen_m)
        p.drawLine(QPointF(cx, cy), self._polar(cx, cy, len_m, a_m))

        # seconds hand goes to center (mechanical mounting on spindle)
        p.setPen(pen_s)
        tail = self._polar(cx, cy, r * 0.16, a_s + math.pi)
        head = self._polar(cx, cy, len_s, a_s)
        p.drawLine(tail, head)

        # seconds mounting: red collar (circular enlargement) + black spindle tip (dot)
        # collar sits ON TOP of seconds hand to "pin" it mechanically
        collar_r = max(1.2, hub_r * 0.42)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(255, 0, 0)))
        p.drawEllipse(QPointF(cx, cy), collar_r, collar_r)

        spindle_r = max(0.7, collar_r * 0.22)
        p.setBrush(QBrush(Qt.black))
        p.drawEllipse(QPointF(cx, cy), spindle_r, spindle_r)

        # small white pin highlight (very subtle, keeps BW+red rule)
        highlight_r = max(0.4, spindle_r * 0.35)
        highlight_pos = QPointF(cx - spindle_r * 0.25, cy - spindle_r * 0.25)
        p.setBrush(QBrush(Qt.white))
        p.drawEllipse(highlight_pos, highlight_r, highlight_r)

        # ---------------------------------------------------------
        # Signature "Kájovo" (fully geometric, proportional)
        # ---------------------------------------------------------
        fam = self._handwriting_font() or self._font_regular
        f = QFont(fam) if fam else p.font()

        # was: r * 0.12 * 0.85  => now additionally -30% overall => *0.70
        f_px = max(6.0, r * 0.12 * 0.85 * 0.70)
        f.setPixelSize(int(f_px))
        f.setItalic(True)
        f.setBold(False)

        p.setFont(f)
        p.setPen(QPen(Qt.white, max(1.0, base_tick * 0.6)))

        fm = p.fontMetrics()
        text = "Kájovo"
        rest = "ájovo"
        total_w = fm.horizontalAdvance(text)

        sig_angle = self._angle(34.0, 60.0)
        sig_r = (r - major_len) - (r * 0.10)
        pos = self._polar(cx, cy, sig_r, sig_angle)

        p.save()

        # mirror over vertical axis of the whole component
        p.translate(cx, 0.0)
        p.scale(-1.0, 1.0)
        p.translate(-cx, 0.0)

        # place on tangent
        p.translate(pos)
        p.rotate(math.degrees(sig_angle) + 90.0)

        # mirror over signature horizontal axis
        p.scale(1.0, -1.0)

        # rotate along signature axis: "posuň doprava o 10°" relative to previous (-15°) => -5°
        p.rotate(-5.0)

        # "K" print-like, rest cursive
        k_font = QFont(f)
        k_font.setItalic(False)
        k_font.setPixelSize(int(f_px * 1.05))

        x0 = -total_w * 0.5
        y0 = fm.ascent() * 0.35

        p.setFont(k_font)
        k_w = p.fontMetrics().horizontalAdvance("K")
        p.drawText(x0, y0, "K")

        # right side drop (kept proportional)
        p.setFont(f)
        p.drawText(x0 + k_w, y0 + f_px * 0.15, rest)

        p.restore()
