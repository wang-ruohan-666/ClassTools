from PySide6.QtCore import Qt, QSize, QRect
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QStyledItemDelegate, QStyle


class PlaylistDelegate(QStyledItemDelegate):
    def __init__(self, is_dark=True):
        super().__init__()
        self.is_dark = is_dark

    def paint(self, painter: QPainter, option, index):
        painter.save()

        # 1. 背景（选中/普通）
        if option.state & QStyle.StateFlag.State_Selected:
            bg_color = QColor("#3c3c3c") if self.is_dark else QColor("#e0e0e0")
        else:
            bg_color = QColor("#2d2d2d") if self.is_dark else QColor("#ffffff")
        painter.fillRect(option.rect, bg_color)

        # 2. 获取数据（使用完整 ItemDataRole）
        title = index.data(Qt.ItemDataRole.DisplayRole)
        author = index.data(Qt.ItemDataRole.UserRole)
        cover = index.data(Qt.ItemDataRole.UserRole + 1)  # QPixmap
        duration = index.data(Qt.ItemDataRole.UserRole + 2)  # 秒

        # 3. 绘制封面（左侧 50x50）
        if cover and not cover.isNull():
            cover_rect = QRect(option.rect.left() + 5, option.rect.top() + 5, 50, 50)
            scaled_cover = cover.scaled(50, 50,
                                        Qt.AspectRatioMode.KeepAspectRatio,
                                        Qt.TransformationMode.SmoothTransformation)
            painter.drawPixmap(cover_rect, scaled_cover)

        # 4. 文字区域（封面右侧）
        text_rect = option.rect.adjusted(60, 5, -10, -5)

        # 歌名（左上方）
        painter.setPen(QColor("#ffffff") if self.is_dark else QColor("#000000"))
        font = QFont()
        font.setPointSize(10)
        painter.setFont(font)
        title_rect = QRect(text_rect.left(), text_rect.top(),
                           text_rect.width(), text_rect.height() // 2)
        painter.drawText(title_rect,
                         Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                         title)

        # 作者（歌名下方，颜色较淡）
        if author:
            painter.setPen(QColor("#aaaaaa") if self.is_dark else QColor("#888888"))
            font.setPointSize(8)
            painter.setFont(font)
            author_rect = QRect(text_rect.left(), title_rect.bottom(),
                                text_rect.width(), text_rect.height() // 2)
            painter.drawText(author_rect,
                             Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                             author)

        # 时长（右下角）
        if duration:
            mins, secs = divmod(duration, 60)
            time_str = f"{int(mins)}:{int(secs):02d}"
            painter.setPen(QColor("#aaaaaa") if self.is_dark else QColor("#888888"))
            font.setPointSize(8)
            painter.setFont(font)
            duration_rect = QRect(text_rect.left(), text_rect.top(),
                                  text_rect.width(), text_rect.height())
            painter.drawText(duration_rect,
                             Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom,
                             time_str)

        painter.restore()

    def sizeHint(self, option, index):
        return QSize(200, 60)
