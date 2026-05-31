# PlaylistDelegate.py
from PySide6.QtCore import Qt, QSize, QRect
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QStyledItemDelegate, QStyle, QStyleOptionViewItem

from MusicPlayer.PlaylistModel import PlaylistModel  # 新增导入

class PlaylistDelegate(QStyledItemDelegate):
    def __init__(self, is_dark=True):
        super().__init__()
        self.is_dark = is_dark

    def paint(self, painter: QPainter, option, index):
        painter.save()

        # 获取 model 检查交换动画状态
        model = index.model()
        adjusted_option = QStyleOptionViewItem(option)  # 复制 option，以便修改矩形

        if isinstance(model, PlaylistModel) and model.anim_source >= 0 and model.anim_target >= 0:
            row = index.row()
            if row == model.anim_source or row == model.anim_target:
                # 计算垂直偏移量：源行向目标行移动，目标行向源行移动
                item_height = option.rect.height()
                if row == model.anim_source:
                    offset_y = (model.anim_target - model.anim_source) * item_height * model.anim_progress
                else:
                    offset_y = (model.anim_source - model.anim_target) * item_height * model.anim_progress
                adjusted_option.rect.translate(0, int(offset_y))

        # 使用调整后的矩形进行绘制
        rect = adjusted_option.rect

        # 1. 背景（选中/普通）
        if option.state & QStyle.StateFlag.State_Selected:
            bg_color = QColor("#3c3c3c") if self.is_dark else QColor("#e0e0e0")
        else:
            bg_color = QColor("#2d2d2d") if self.is_dark else QColor("#ffffff")
        painter.fillRect(rect, bg_color)

        # 2. 获取数据
        title = index.data(Qt.ItemDataRole.DisplayRole)
        author = index.data(Qt.ItemDataRole.UserRole)
        cover = index.data(Qt.ItemDataRole.UserRole + 1)
        duration = index.data(Qt.ItemDataRole.UserRole + 2)

        # 3. 绘制封面
        if cover and not cover.isNull():
            cover_rect = QRect(rect.left() + 5, rect.top() + 5, 50, 50)
            scaled_cover = cover.scaled(50, 50,
                                        Qt.AspectRatioMode.KeepAspectRatio,
                                        Qt.TransformationMode.SmoothTransformation)
            painter.drawPixmap(cover_rect, scaled_cover)

        # 4. 文字区域
        text_rect = rect.adjusted(60, 5, -10, -5)

        # 歌名
        painter.setPen(QColor("#ffffff") if self.is_dark else QColor("#000000"))
        font = QFont()
        font.setPointSize(10)
        painter.setFont(font)
        title_rect = QRect(text_rect.left(), text_rect.top(),
                           text_rect.width(), text_rect.height() // 2)
        painter.drawText(title_rect,
                         Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                         title)

        # 作者
        if author:
            painter.setPen(QColor("#aaaaaa") if self.is_dark else QColor("#888888"))
            font.setPointSize(8)
            painter.setFont(font)
            author_rect = QRect(text_rect.left(), title_rect.bottom(),
                                text_rect.width(), text_rect.height() // 2)
            painter.drawText(author_rect,
                             Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                             author)

        # 时长
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