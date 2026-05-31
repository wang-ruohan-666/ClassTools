# views/peak_window.py
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from MusicPlayer.views.peak_meter import PeakHistoryMeter

class PeakWindow(QWidget):
    """独立的峰值历史曲线窗口"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("音频峰值")
        # 无边框 + 工具窗口 + 置顶
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # 标题
        self.title_label = QLabel("音量峰值曲线")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # 峰值曲线控件
        self.meter = PeakHistoryMeter(max_points=200)
        self.meter.setMinimumSize(350, 80)
        layout.addWidget(self.meter)

        self.setMinimumSize(370, 120)

        # 初始位置（屏幕右上角）
        from PySide6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.move(screen.right() - self.width() - 20, screen.top() + 60)

    def add_compare_peaks(self, orig, bal):
        self.meter.add_compare_peaks(orig, bal)

    def add_peak(self, value: float):
        self.meter.add_peak(value)

    def apply_theme(self, is_dark: bool):
        """响应主题切换"""
        if is_dark:
            self.setStyleSheet("""
                QWidget {
                    background-color: rgba(30, 30, 30, 200);
                    border-radius: 10px;
                    color: #ffffff;
                }
                QLabel {
                    background: transparent;
                    font-size: 12px;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: rgba(240, 240, 240, 200);
                    border-radius: 10px;
                    color: #000000;
                }
                QLabel {
                    background: transparent;
                    font-size: 12px;
                }
            """)