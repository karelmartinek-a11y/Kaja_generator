from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QTimer, Qt, QSize, QRectF, QPointF, QTime
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QFontDatabase,
    QPainter,
    QPen,
    QPainterPath,
)
from PySide6.QtWidgets import QWidget, QSizePolicy


@dataclass
class _TimeModel:
    elapsed_s: int = 0
    total_s: int = 0
    eta_s: Optional[int] = None


class ProcessThermometer(QWidget):
    """
    KÁJOVO UI LIB
    COMPONENT: PROCESS THERMOMETER
    FILE:      components/process_thermometer.py
    VERSION:   v1.0 (authorization candidate, hardened calculations)

    Fix (A+B only; C unchanged):
      - Výpočty času/procent jsou SAMOKOREKČNÍ:
          * pokud progress >= 100 %, zbývající čas je vždy 0
          * pokud elapsed >= total, zbývající čas je vždy 0 a progress je 100 %
          * pokud je zadané ETA, ale nesedí s progress/elapsed/total, komponenta to zklampuje tak,
            aby na 100 % byl vždy odpočet 00:00:00
      - Zarovnání rtuti na stupnici:
          * 0 % = první dílek stupnice (scale_start)
          * 100 % = poslední dílek stupnice (scale_end)

    Demo:
      - hour-clock běží jen v MODE_TIME (B) a drží konzistenci total/elapsed/eta/progress.
    """

    MODE_PERCENT = "percent"              # Varianta A
    MODE_TIME = "time_estimate"           # Varianta B
    MODE_INDETERMINATE = "indeterminate"  # Varianta C

    _fonts_loaded = False
    _font_regular: str | None = None

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(360, 170)
        self.setAttribute(Qt.WA_OpaquePaintEvent, True)

        self._ensure_fonts_loaded()

        self._mode: str = self.MODE_PERCENT
        self._progress: float = 1.0
        self._status: str = "Inicializace"
        self._time = _TimeModel()

        # Demo hour-clock only for MODE_TIME (prevents fighting with MODE_PERCENT animations)
        self._demo_hour_clock_enabled: bool = True

        # Indeterminate animation
        self._t: float = 0.0
        self._dir: float = 1.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(16)

    # ---------------- Qt sizing ----------------

    def sizeHint(self) -> QSize:
        return QSize(980, 340)

    def minimumSizeHint(self) -> QSize:
        return QSize(360, 170)

    # ---------------- Public API ----------------

    def set_mode(self, mode: str) -> None:
        m = str(mode).strip().lower()
        if m not in (self.MODE_PERCENT, self.MODE_TIME, self.MODE_INDETERMINATE):
            return
        self._mode = m
        self.update()

    def set_indeterminate(self, active: bool = True) -> None:
        self._mode = self.MODE_INDETERMINATE if bool(active) else self.MODE_PERCENT
        self.update()

    def set_progress(self, value: float) -> None:
        # External progress -> disable demo clock to avoid conflicts
        self._demo_hour_clock_enabled = False
        try:
            v = float(value)
        except Exception:
            return
        self._progress = max(0.0, min(1.0, v))
        self.update()

    def set_status(self, text: str) -> None:
        self._status = str(text)
        self.update()

    def set_time_elapsed_total(self, elapsed_seconds: int, total_seconds: int) -> None:
        self._demo_hour_clock_enabled = False
        e = max(0, int(elapsed_seconds))
        t = max(0, int(total_seconds))

        self._time.elapsed_s = e
        self._time.total_s = t
        self._time.eta_s = None

        if t > 0:
            # keep progress consistent with time input
            self._progress = max(0.0, min(1.0, e / float(t)))
        self.update()

    def set_eta_seconds(self, remaining_seconds: Optional[int]) -> None:
        self._demo_hour_clock_enabled = False
        self._time.eta_s = None if remaining_seconds is None else max(0, int(remaining_seconds))
        self.update()

    def set_demo_hour_clock_enabled(self, enabled: bool) -> None:
        self._demo_hour_clock_enabled = bool(enabled)
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

    def _tick(self) -> None:
        # Demo hour-clock: MODE_TIME only
        if self._demo_hour_clock_enabled and self._mode == self.MODE_TIME:
            now = QTime.currentTime()
            s_in_hour = now.minute() * 60 + now.second()     # 0..3599
            total_s = 3600
            rem_s = max(0, total_s - s_in_hour)

            self._time.elapsed_s = int(s_in_hour)
            self._time.total_s = int(total_s)
            self._time.eta_s = int(rem_s)

            self._progress = max(0.0, min(1.0, s_in_hour / float(total_s)))

            if not (self._status or "").strip():
                self._status = "Zpracování…"

            self.update()

        # Indeterminate ping-pong
        if self._mode == self.MODE_INDETERMINATE:
            self._t += 0.003 * self._dir
            if self._t >= 1.0:
                self._t = 1.0
                self._dir = -1.0
            elif self._t <= 0.0:
                self._t = 0.0
                self._dir = 1.0
            self.update()

    @staticmethod
    def _fmt_hhmmss(seconds: int) -> str:
        t = max(0, int(seconds))
        hh = t // 3600
        mm = (t % 3600) // 60
        ss = t % 60
        return f"{hh:02d}:{mm:02d}:{ss:02d}"

    @staticmethod
    def _capsule_path(x: float, y: float, w: float, h: float) -> QPainterPath:
        path = QPainterPath()
        if w <= 0 or h <= 0:
            return path
        r = h * 0.5
        path.addRoundedRect(QRectF(x, y, w, h), r, r)
        return path

    @staticmethod
    def _outline_path_with_taper(x0: float, y_mid: float, L: float, H: float) -> dict:
        top = y_mid - H * 0.5
        bot = y_mid + H * 0.5

        taper_len = L * 0.08
        tip_h = H * 0.28
        tip_top = y_mid - tip_h * 0.5
        tip_bot = y_mid + tip_h * 0.5

        trans_len_base = max(L * 0.10, H * 1.2)
        trans_len = trans_len_base * 0.25

        x_tip0 = x0
        x_taper_end = x_tip0 + taper_len
        x_trans_end = x_taper_end + trans_len
        x_end = x0 + L

        r_end = H * 0.5
        x_cap0 = x_end - H
        cap_rect = QRectF(x_cap0, top, H, H)

        c1_top = QPointF(x_taper_end + trans_len * 0.25, tip_top - H * 0.06)
        c2_top = QPointF(x_taper_end + trans_len * 0.75, top + H * 0.02)

        c1_bot = QPointF(x_taper_end + trans_len * 0.75, bot - H * 0.02)
        c2_bot = QPointF(x_taper_end + trans_len * 0.25, tip_bot + H * 0.06)

        outline = QPainterPath()
        r_tip = tip_h * 0.5

        outline.moveTo(QPointF(x_tip0 + r_tip, tip_top))
        outline.lineTo(QPointF(x_taper_end, tip_top))
        outline.cubicTo(c1_top, c2_top, QPointF(x_trans_end, top))
        outline.lineTo(QPointF(x_cap0 + r_end, top))
        outline.arcTo(cap_rect, 90.0, -180.0)
        outline.lineTo(QPointF(x_trans_end, bot))
        outline.cubicTo(c1_bot, c2_bot, QPointF(x_taper_end, tip_bot))
        outline.lineTo(QPointF(x_tip0 + r_tip, tip_bot))
        tip_rect = QRectF(x_tip0, tip_top, tip_h, tip_h)
        outline.arcTo(tip_rect, -90.0, -180.0)
        outline.closeSubpath()

        return {
            "path": outline,
            "x0": x0,
            "x_end": x_end,
            "x_taper_end": x_taper_end,
            "H": H,
            "tip_h": tip_h,
            "r_end": r_end,
            "y_mid": y_mid,
            "taper_len": taper_len,
            "top": top,
            "bot": bot,
        }

    @staticmethod
    def _ease_nonuniform_pingpong_fast_start(t: float) -> float:
        x = max(0.0, min(1.0, float(t)))
        split = 0.55
        tail = 1.0 - split
        if x <= split:
            u = x / split
            return (u ** 3) * split
        v = (x - split) / tail
        e = 1.0 - ((1.0 - v) ** 3)
        return split + e * tail

    def _compute_ab_consistent(self) -> tuple[float, int, int]:
        """
        Vrací (progress_clamped, elapsed_s, remaining_s) pro varianty A+B.

        Samokorekce:
          - pokud progress >= 1 => remaining = 0
          - pokud total známé a elapsed >= total => remaining = 0, progress = 1
          - pokud eta je zadaná, použije se, ale je vždy zklampována na 0 při progress==1
          - pokud total není zadané, ale je zadané eta, inferujeme total = elapsed + eta
        """
        # progress is primary for mercury and for "cechování" na 100 %
        p = max(0.0, min(1.0, float(self._progress)))

        e = max(0, int(self._time.elapsed_s))
        t = max(0, int(self._time.total_s))
        eta = None if self._time.eta_s is None else max(0, int(self._time.eta_s))

        # infer total if missing but we have eta
        if t <= 0 and eta is not None:
            t = e + eta

        # compute remaining baseline
        if t > 0:
            r = max(0, t - e)
            # if ETA exists, take the smaller non-negative value but never negative
            if eta is not None:
                r = max(0, min(r, eta))
        else:
            r = 0 if eta is None else max(0, eta)

        # hard rules at boundaries (this fixes the "100% but 4s remaining" mismatch)
        EPS = 1e-9
        if p >= 1.0 - EPS:
            p = 1.0
            r = 0
            if t > 0:
                e = t
        if t > 0 and e >= t:
            e = t
            r = 0
            p = 1.0

        # also: if remaining already 0 and total known, clamp progress to 100
        if t > 0 and r == 0:
            p = 1.0

        return p, e, r

    # ---------------- Paint ----------------

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setRenderHint(QPainter.TextAntialiasing, True)

        w = float(self.width())
        h = float(self.height())

        p.fillRect(self.rect(), QBrush(Qt.black))
        if w < 10 or h < 10:
            return

        pad = min(w, h) * 0.10
        L = max(140.0, w - 2 * pad)
        H = max(24.0, min(h * 0.22, 68.0))

        x0 = pad
        y_mid = h * 0.57
        geom = self._outline_path_with_taper(x0, y_mid, L, H)

        outline: QPainterPath = geom["path"]
        x_end = float(geom["x_end"])
        x_taper_end = float(geom["x_taper_end"])
        taper_len = float(geom["taper_len"])
        top = float(geom["top"])
        bot = float(geom["bot"])
        r_end = float(geom["r_end"])
        tip_h = float(geom["tip_h"])

        base = max(1.0, min(w, h) * 0.006)
        stroke = max(1.6, base * 2.0)
        gap = max(1.2, stroke * 1.4)

        pen_outline = QPen(Qt.white, stroke)
        pen_outline.setCapStyle(Qt.RoundCap)
        pen_outline.setJoinStyle(Qt.RoundJoin)
        p.setPen(pen_outline)
        p.setBrush(Qt.NoBrush)
        p.drawPath(outline)

        scale_start = x_taper_end + (taper_len / 3.0)
        scale_end = (x_end - H) - (taper_len / 3.0)
        if scale_end < scale_start + 20.0:
            scale_end = scale_start + 20.0
        scale_start = scale_start + (scale_end - scale_start) * 0.05
        if scale_start > scale_end - 10.0:
            scale_start = scale_end - 10.0
        scale_len = scale_end - scale_start

        mercury_h = max(3.0, tip_h - 2.0 * gap)
        mercury_h = min(mercury_h, H * 0.14)
        my = y_mid - mercury_h * 0.5

        guide_w = max(0.7, base * 0.55)
        p.setPen(QPen(QColor(255, 255, 255, 120), guide_w, Qt.SolidLine, Qt.RoundCap))
        p.drawLine(QPointF(scale_start, y_mid), QPointF(scale_end, y_mid))

        tick_w = max(1.0, base * 0.9)
        p.setPen(QPen(Qt.white, tick_w, Qt.SolidLine, Qt.RoundCap))

        minor_len = max(3.0, H * 0.10)
        major_len = max(minor_len + 2.0, H * 0.18)

        up_limit = top + gap * 1.2
        dn_limit = bot - gap * 1.2
        max_up = max(2.0, y_mid - up_limit)
        max_dn = max(2.0, dn_limit - y_mid)

        major_len = min(major_len, max_up, max_dn)
        minor_len = min(minor_len, major_len * 0.7)

        for v in range(0, 101):
            x = scale_start + scale_len * (v / 100.0)
            is_major = (v % 20) == 0
            Ltick = (major_len if is_major else minor_len)
            p.drawLine(QPointF(x, y_mid), QPointF(x, y_mid - Ltick))
            p.drawLine(QPointF(x, y_mid), QPointF(x, y_mid + Ltick))

        # Mercury last
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(255, 0, 0)))

        if self._mode == self.MODE_INDETERMINATE:
            # C unchanged (can travel beyond scale)
            mx0 = x0 + gap * 1.1
            mx1 = x_end - r_end * 0.35 - gap * 1.4
            if mx1 < mx0 + 2.0:
                mx1 = mx0 + 2.0
            mw_full = mx1 - mx0

            seg = max(mw_full * 0.12, mercury_h * 6.0)
            te = self._ease_nonuniform_pingpong_fast_start(self._t)
            x_min = mx0
            x_max = max(x_min, mx1 - seg)
            sx0 = x_min + (x_max - x_min) * te
            p.drawPath(self._capsule_path(sx0, my, seg, mercury_h))
        else:
            p_cons, e_cons, r_cons = self._compute_ab_consistent()
            # align strictly to scale ticks: 0% at first tick, 100% at last tick
            start_x = scale_start
            end_x = scale_start + scale_len * p_cons
            end_x = max(start_x, min(scale_end, end_x))
            p.drawPath(self._capsule_path(start_x, my, end_x - start_x, mercury_h))

        fam = self._font_regular

        # A+B labels + times (computed from consistent state)
        if self._mode in (self.MODE_PERCENT, self.MODE_TIME):
            # recompute consistent values for text (keeps 100% -> 00:00:00 guarantee)
            p_cons, e_cons, r_cons = self._compute_ab_consistent()

            lbl_font = QFont(fam) if fam else p.font()
            lbl_font.setBold(True)
            lbl_font.setItalic(False)
            lbl_font.setPixelSize(int(max(9.0, H * 0.18)))
            p.setFont(lbl_font)
            fm = p.fontMetrics()
            p.setPen(QPen(Qt.white, max(1.0, base * 0.7)))

            txt0 = "0 %"
            txt1 = "100 %"

            inner_top = top + gap * 1.3
            safe_bottom = (y_mid - major_len) - gap * 0.8
            label_y = max(inner_top + fm.ascent(), min(safe_bottom, inner_top + fm.ascent() + H * 0.12))

            x0_lbl = max(x0 + gap * 2.0, scale_start)
            x1_lbl = min((x_end - gap * 2.0) - fm.horizontalAdvance(txt1),
                         scale_end - fm.horizontalAdvance(txt1))

            p.drawText(int(x0_lbl), int(label_y), txt0)
            p.drawText(int(x1_lbl), int(label_y), txt1)

            left_time = self._fmt_hhmmss(e_cons)
            right_time = self._fmt_hhmmss(r_cons)

            time_font = QFont(fam) if fam else p.font()
            time_font.setBold(True)
            time_font.setItalic(False)
            time_font.setPixelSize(int(max(9.0, H * 0.16)))
            p.setFont(time_font)
            t_fm = p.fontMetrics()
            p.setPen(QPen(Qt.white, max(1.0, base * 0.65)))

            inner_bot = bot - gap * 1.2
            after_ticks = y_mid + major_len + gap * 0.6
            time_base_y = min(inner_bot, after_ticks + t_fm.ascent())
            time_base_y = max(after_ticks + t_fm.ascent(), time_base_y)

            left_x = max(x0 + gap * 2.0, scale_start)
            right_x = min((x_end - gap * 2.0) - t_fm.horizontalAdvance(right_time),
                          scale_end - t_fm.horizontalAdvance(right_time))

            p.drawText(int(left_x), int(time_base_y), left_time)
            p.drawText(int(right_x), int(time_base_y), right_time)

        # Signature (unchanged)
        sig_text = "Kájovo"
        sig_col = QColor(255, 0, 0)

        tick_dx = scale_len * 0.01
        sig_shift_x = tick_dx * 2.0
        sig_shift_y = -major_len * 0.50

        target_w = max(10.0, scale_len * 0.03)

        sig_font = QFont(fam) if fam else p.font()
        sig_font.setBold(False)
        sig_font.setItalic(False)
        sig_font.setPixelSize(int(max(7.0, H * 0.14)))
        p.setFont(sig_font)
        sig_fm = p.fontMetrics()
        tw = max(1, sig_fm.horizontalAdvance(sig_text))
        scale_factor = target_w / float(tw)

        new_px = int(max(5, min(sig_font.pixelSize(), sig_font.pixelSize() * scale_factor)))
        sig_font.setPixelSize(new_px)
        p.setFont(sig_font)
        sig_fm = p.fontMetrics()
        tw2 = sig_fm.horizontalAdvance(sig_text)

        right_inner_limit = x_end - gap * 1.6
        sig_center_x = min(scale_end + target_w * 0.9 + sig_shift_x, right_inner_limit - (tw2 * 0.6))
        sig_base_y = (y_mid + (H * 0.5) - gap * 1.9) + sig_shift_y

        p.save()
        p.translate(sig_center_x, sig_base_y)
        p.rotate(-10.0)
        p.setPen(QPen(sig_col, max(0.8, base * 0.5)))
        p.drawText(int(-tw2 * 0.5), 0, sig_text)
        p.restore()


# Compatibility aliases/factory
ProcessThermometerWidget = ProcessThermometer
ThermometerProcess = ProcessThermometer


def create(parent=None) -> ProcessThermometer:
    return ProcessThermometer(parent=parent)
