from collections import deque
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath

class PeakHistoryMeter(QWidget):
    """显示峰值历史曲线的控件（类似专业电平表）"""
    def __init__(self, max_points=200, parent=None):
        super().__init__(parent)
        self.max_points = max_points
        self.peaks = deque([0.0] * max_points, maxlen=max_points)
        self.setMinimumSize(300, 60)

    def add_peak(self, value: float):
        """添加一个新的峰值数据点"""
        self.peaks.append(max(0.0, min(1.0, value)))
        self.update()

    def clear(self):
        """清空历史数据"""
        self.peaks = deque([0.0] * self.max_points, maxlen=self.max_points)
        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # 修复

        w = self.width()
        h = self.height()
        if w <= 0 or h <= 0:
            return

        # 背景
        painter.fillRect(0, 0, w, h, QColor(30, 30, 30))

        # 绘制网格线
        painter.setPen(QPen(QColor(60, 60, 60), 1, Qt.PenStyle.DashLine))  # 修复
        for level in [0.25, 0.5, 0.75]:
            y = int(h * (1.0 - level))
            painter.drawLine(0, y, w, y)

        # 获取数据点列表
        points = list(self.peaks)
        step_x = w / max(1, self.max_points - 1)


        # 绘制折线
        painter.setBrush(Qt.BrushStyle.NoBrush) # 修复
        painter.setPen(QPen(QColor(0, 255, 0), 2))
        line_path = QPainterPath()
        for i, peak in enumerate(points):
            x = w - i * step_x
            y = h * (1.0 - peak)
            if i == 0:
                line_path.moveTo(x, y)
            else:
                line_path.lineTo(x, y)
        painter.drawPath(line_path)

        painter.end()