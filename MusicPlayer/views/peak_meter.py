# views/peak_metar.py
from collections import deque
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath

class PeakHistoryMeter(QWidget):
    def __init__(self, max_points=200, parent=None):
        super().__init__(parent)
        self.max_points = max_points
        # 双缓冲区
        self.original_peaks = deque([0.0] * max_points, maxlen=max_points)
        self.balanced_peaks = deque([0.0] * max_points, maxlen=max_points)
        self.setMinimumSize(300, 60)

    def add_compare_peaks(self, original: float, balanced: float):
        """同时添加原始和均衡后的峰值"""
        self.original_peaks.append(max(0.0, min(1.0, original)))
        self.balanced_peaks.append(max(0.0, min(1.0, balanced)))
        self.update()

    def add_peak(self, value: float):
        """兼容旧版：单值加入原始曲线，均衡后值保持不变（或可设为相同）"""
        self.add_compare_peaks(value, value)  # 让两条线重叠

    def clear(self):
        self.original_peaks = deque([0.0] * self.max_points, maxlen=self.max_points)
        self.balanced_peaks = deque([0.0] * self.max_points, maxlen=self.max_points)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        if w <= 0 or h <= 0:
            return

        # 背景
        painter.fillRect(0, 0, w, h, QColor(30, 30, 30))

        # 网格线
        painter.setPen(QPen(QColor(60, 60, 60), 1, Qt.PenStyle.DashLine))
        for level in [0.25, 0.5, 0.75]:
            y = int(h * (1.0 - level))
            painter.drawLine(0, y, w, y)

        # 绘制两条曲线（淡黄色：原始，绿色：均衡后）
        self._draw_line(painter, self.original_peaks, QColor(255, 255, 100), w, h)
        self._draw_line(painter, self.balanced_peaks, QColor(0, 255, 0), w, h)

        painter.end()

    def _draw_line(self, painter, peaks, color, w, h):
        points = list(peaks)
        step_x = w / max(1, self.max_points - 1)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(color, 2))
        path = QPainterPath()
        for i, peak in enumerate(points):
            x = w - i * step_x   # 新数据在右侧，旧数据向左移动
            y = h * (1.0 - peak)
            if i == 0:
                path.moveTo(x, y)
            else:
                path.lineTo(x, y)
        painter.drawPath(path)