# views/playlist_window.py
import json
from pathlib import Path

from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QTimer, QEasingCurve, QIODevice, QDataStream, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QDrag, QPainter, QColor, QPixmap
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtWidgets import QWidget, QApplication, QListView, QAbstractItemView, QMenu, QFileDialog

from MusicPlayer.GetSongInfo import get_song_info
from MusicPlayer.PlaylistDelegate import PlaylistDelegate
from MusicPlayer.PlaylistModel import PlaylistModel
from MusicPlayer.SongItem import SongItem
from MusicPlayer.managers.settings_manager import SettingsManager
from MusicPlayer.managers.theme_manager import ThemeManager
from MusicPlayer.ui_playlist import Ui_Form as Playlist
from MusicPlayer.common.logger import get_logger

logger=get_logger(__name__)


class DraggableListView(QListView):
    """支持内部拖拽排序的 QListView（手动实现拖拽逻辑）"""
    delete_item_requested = Signal(int)  # row
    clear_list_requested = Signal()
    open_settings_requested = Signal()
    import_playlist_requested = Signal()
    export_playlist_requested = Signal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self._drag_start_pos = None
        self._drop_target_row = -1

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton) or self._drag_start_pos is None:
            return
        if (event.pos() - self._drag_start_pos).manhattanLength() < QApplication.startDragDistance():
            return
        index = self.indexAt(self._drag_start_pos)
        if not index.isValid():
            return

        # 创建半透明拖拽图标
        rect = self.visualRect(index)
        pixmap = self.viewport().grab(rect)  # 截取该项的截图
        # 半透明处理
        pixmap.setDevicePixelRatio(1)
        image = pixmap.toImage()
        painter = QPainter(image)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
        painter.fillRect(image.rect(), QColor(255, 255, 255, 128))  # 透明度 50%
        painter.end()
        pixmap = QPixmap.fromImage(image)

        drag = QDrag(self)
        mime_data = self.model().mimeData([index])
        drag.setMimeData(mime_data)
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos() - rect.topLeft())  # 保持鼠标相对位置
        drag.exec(Qt.DropAction.MoveAction)
        self._drag_start_pos = None

    def dropEvent(self, event):
        mime_data = event.mimeData()
        if mime_data.hasFormat("application/x-playlist-row"):
            encoded = mime_data.data("application/x-playlist-row")
            stream = QDataStream(encoded, QIODevice.OpenModeFlag.ReadOnly)
            source_row = stream.readInt32()

            drop_index = self.indexAt(event.pos())
            if drop_index.isValid():
                target_row = drop_index.row()
                if source_row != target_row:
                    # 安全调用自定义方法，消除类型检查警告
                    model = self.model()
                    if isinstance(model, PlaylistModel):
                        model.swapRows(source_row, target_row)

            self.selectionModel().clearSelection()
            self.viewport().update()
            event.accept()
        else:
            event.ignore()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        index = self.indexAt(event.pos())
        if index.isValid():
            remove_action = menu.addAction("从列表中删除")
            remove_action.triggered.connect(lambda: self.delete_item_requested.emit(index.row()))
        menu.addSeparator()
        menu.addAction("清空列表").triggered.connect(self.clear_list_requested.emit)
        menu.addSeparator()
        menu.addAction("导入歌单").triggered.connect(self.import_playlist_requested.emit)
        menu.addAction("导出歌单").triggered.connect(self.export_playlist_requested.emit)
        menu.addSeparator()
        menu.addAction("打开设置").triggered.connect(self.open_settings_requested.emit)
        menu.exec(event.globalPos())


class PlaylistWindows(QWidget):
    open_settings_signal = Signal()
    def __init__(self, settings_mgr: SettingsManager, theme_mgr: ThemeManager):
        super().__init__()
        self.settings_mgr = settings_mgr
        self.theme_mgr = theme_mgr

        self.playlist = Playlist()
        self.playlist.setupUi(self)
        self.move_playlist_window()

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.hide_anim = QPropertyAnimation(self, b"geometry")
        self.show_anim = QPropertyAnimation(self, b"geometry")
        self.hide_timer = QTimer(self)
        self.fixed = False
        self.playlist_hide_time = 3000
        self.is_hide = False
        self.path = Path(__file__).parent.parent

        self.playlist_model = PlaylistModel()
        self.setAcceptDrops(True)
        self.playlist_delegate = PlaylistDelegate(is_dark=(self.theme_mgr.get_current_theme_name() == "dark"))

        self.playlist_view = DraggableListView()

        self.init_playlist()
        self.init_show_anim()
        self.init_hide_anim()
        self.init_playlist_view()
        self.connect_signals()

        # 连接信号
        self.playlist_view.delete_item_requested.connect(self._on_delete_item)
        self.playlist_view.clear_list_requested.connect(self._on_clear_list)
        self.playlist_view.open_settings_requested.connect(self.open_settings_signal.emit)
        self.playlist_view.import_playlist_requested.connect(self._on_import_playlist)
        self.playlist_view.export_playlist_requested.connect(self._on_export_playlist)
        self.theme_mgr.theme_applied.connect(self._on_theme)

        self.show()

    def init_playlist_view(self):
        self.playlist_view.setModel(self.playlist_model)
        self.playlist_view.setItemDelegate(self.playlist_delegate)
        self.playlist_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.playlist_view.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.playlist.root.layout().addWidget(self.playlist_view)

    def init_playlist(self):
        self.init_fixed()
        self.hide_timer.timeout.connect(self._start_hide)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.start(self.playlist_hide_time)

    def connect_signals(self):
        self.settings_mgr.anim_speed_changed.connect(self._update_anim_durations)
        self.settings_mgr.stay_on_top_changed.connect(self._update_stay_on_top)

    def _on_delete_item(self, row: int):
        self.playlist_model.remove_song(row)

    def _on_clear_list(self):
        self.playlist_model.clear()

    def _on_import_playlist(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "导入歌单", "", "JSON 文件 (*.json)")
        if not file_path:
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.playlist_model.import_data(data)
        except Exception as e:
            logger.error(f"导入歌单失败: {e}")

    def _on_export_playlist(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "导出歌单", "", "JSON 文件 (*.json)")
        if not file_path:
            return
        try:
            data = self.playlist_model.to_export_data()
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"导出歌单失败: {e}")

    # 注意：add_to_playlist 方法中需要传递 file_path
    def add_to_playlist(self, path):
        info = get_song_info(path)
        item = SongItem(info[0], info[1], info[2], info[3], file_path=path)  # 添加 file_path
        self.playlist_model.add_song(item)

    def _on_theme(self, theme: str):
        # print(theme)
        if theme == "dark":
            self._dark()
        elif theme == "light":
            self._light()

    def _dark(self):
        self.playlist_delegate.is_dark = True
        self.playlist_view.viewport().update()
        self.setStyleSheet("""
            QWidget {
                color: #ffffff;
            }
            QMenu {
                background-color: #2d2d2d;
                border: 1px solid #5a5a5a;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                background-color: transparent;
                color: #ffffff;
                padding: 6px 24px 6px 12px;
                border-radius: 4px;
                min-width: 120px;
            }
            QMenu::item:selected {
                background-color: #3c3c3c;
            }
            QMenu::item:disabled {
                color: #6c6c6c;
                background-color: transparent;
            }
            QMenu::separator {
                height: 1px;
                background: #5a5a5a;
                margin: 4px 8px;
            }
            QMenu::indicator {
                width: 14px;
                height: 14px;
                margin-left: 4px;
            }
            QMenu::indicator:checked {
                background-color: #448aff;
                border-radius: 3px;
            }
        """)
        self.playlist_view.setStyleSheet("""
QScrollBar:vertical {
    background: #2d2d2d;
    width: 8px;
    margin: 0;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #5a5a5a;
    min-height: 30px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #888888;
}

QScrollBar::handle:vertical:pressed {
    background: #aaaaaa;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
    border: none;
}

QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: none;
}""")
        self.playlist.root.setStyleSheet("""
#root{
    background-color:#1e1e1e;
    border-bottom-left-radius: 15px;
    border-bottom-right-radius: 15px;
    border-top-left-radius: 0px;
    border-top-right-radius: 0px;
}""")
        self.playlist.titlebar.setStyleSheet("""
        QFrame{
            background-color:#1C1B22; 
            border-bottom-left-radius: 0px;
            border-bottom-right-radius: 0px;
            border-top-left-radius: 15px;
            border-top-right-radius: 15px;
        }""")
        self.playlist_view.setStyleSheet("""/* 播放列表 QListView 基本样式 */
QListView {
    background-color: #1e1e1e;      /* 与窗口背景一致 */
    border: none;
    outline: none;                   /* 移除焦点虚线框 */
    padding: 4px;
}

/* 列表项样式（委托未覆盖的部分） */
QListView::item {
    background-color: transparent;
    border: none;
    margin: 0;
    padding: 0;
}

/* 列表项悬停效果（若委托未完全覆盖，可提供视觉反馈） */
QListView::item:hover {
    background-color: #2d2d2d;
}

/* 列表项选中效果 */
QListView::item:selected {
    background-color: #3c3c3c;
}

/* 滚动条（垂直） */
QScrollBar:vertical {
    background: #2d2d2d;
    width: 8px;
    margin: 0;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #5a5a5a;
    min-height: 30px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #888888;
}

QScrollBar::handle:vertical:pressed {
    background: #aaaaaa;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
    border: none;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}""")

    def _light(self):
        self.playlist_delegate.is_dark = False
        self.playlist_view.viewport().update()
        self.setStyleSheet("""
            QMenu {
                background-color: #ffffff;
                border: 1px solid #c0c0c0;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                background-color: transparent;
                color: #000000;
                padding: 6px 24px 6px 12px;
                border-radius: 4px;
                min-width: 120px;
            }
            QMenu::item:selected {
                background-color: #e0e0e0;
            }
            QMenu::item:disabled {
                color: #a0a0a0;
                background-color: transparent;
            }
            QMenu::separator {
                height: 1px;
                background: #c0c0c0;
                margin: 4px 8px;
            }
            QMenu::indicator {
                width: 14px;
                height: 14px;
                margin-left: 4px;
            }
            QMenu::indicator:checked {
                background-color: #448aff;
                border-radius: 3px;
            }
        """)
        self.playlist_view.setStyleSheet("""
        QScrollBar:vertical {
            background: #f0f0f0;
            width: 8px;
            margin: 0;
            border-radius: 4px;
        }

        QScrollBar::handle:vertical {
            background: #c0c0c0;
            min-height: 30px;
            border-radius: 4px;
        }

        QScrollBar::handle:vertical:hover {
            background: #a0a0a0;
        }

        QScrollBar::handle:vertical:pressed {
            background: #808080;
        }

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0;
            border: none;
        }

        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical {
            background: none;
        }""")
        self.playlist.root.setStyleSheet("""#root{
    background-color:#e8e8e8;
    border-bottom-left-radius: 15px;
    border-bottom-right-radius: 15px;
    border-top-left-radius: 0px;
    border-top-right-radius: 0px;
}""")
        self.playlist.titlebar.setStyleSheet("""
        QFrame{
            background-color:rgb(255, 255, 255); 
            border-bottom-left-radius: 0px;
            border-bottom-right-radius: 0px;
            border-top-left-radius: 15px;
            border-top-right-radius: 15px;
        }""")
        self.playlist_view.setStyleSheet("""/* 播放列表 QListView 基本样式 */
QListView {
    background-color: #e8e8e8;      /* 与窗口背景一致 */
    border: none;
    outline: none;
    padding: 4px;
}

/* 列表项样式 */
QListView::item {
    background-color: transparent;
    border: none;
    margin: 0;
    padding: 0;
}

/* 悬停效果 */
QListView::item:hover {
    background-color: #d0d0d0;
}

/* 选中效果 */
QListView::item:selected {
    background-color: #c0c0c0;
}

/* 滚动条（垂直） */
QScrollBar:vertical {
    background: #f0f0f0;
    width: 8px;
    margin: 0;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #c0c0c0;
    min-height: 30px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #a0a0a0;
}

QScrollBar::handle:vertical:pressed {
    background: #808080;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
    border: none;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}""")

    def _update_anim_durations(self, speed: float):
        self.show_anim.setDuration(int(600 / speed))
        self.hide_anim.setDuration(int(300 / speed))

    def _update_stay_on_top(self, checked: bool):
        if checked:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
        self.show()

    def init_fixed(self):
        def fixed_clicked():
            if self.fixed:
                self.fixed = False
                self.playlist.png.setIcon(QIcon(str(self.path / "resources" / "icons" / "unpin.png")))
            else:
                self.fixed = True
                self.playlist.png.setIcon(QIcon(str(self.path / "resources" / "icons" / "fixed.png")))

        self.playlist.png.setIcon(QIcon(str(self.path / "resources" / "icons" / "unpin.png")))
        self.playlist.png.setIconSize(QSize(25, 25))
        self.playlist.png.clicked.connect(fixed_clicked)

    def init_show_anim(self):
        self.show_anim.setDuration(int(600 / self.settings_mgr.anim_speed))
        start_geo = self.geometry()
        self.show_anim.setEasingCurve(QEasingCurve.Type.InBack)
        screen_rect = QApplication.primaryScreen().availableGeometry()
        end_geo = start_geo.translated(screen_rect.right() - start_geo.left(), 0)
        self.show_anim.setStartValue(end_geo)
        self.show_anim.setEndValue(start_geo)

    def init_hide_anim(self):
        self.hide_anim.setDuration(int(300 / self.settings_mgr.anim_speed))
        start_geo = self.geometry()
        self.hide_anim.setEasingCurve(QEasingCurve.Type.InCubic)
        screen_rect = QApplication.primaryScreen().availableGeometry()
        end_geo = start_geo.translated(screen_rect.right() - start_geo.left(), 0)
        self.hide_anim.setStartValue(start_geo)
        self.hide_anim.setEndValue(end_geo)

    def move_playlist_window(self):
        screen = QGuiApplication.primaryScreen().size()
        screen_rect = QApplication.primaryScreen().availableGeometry()
        win_rect = self.frameGeometry()
        win_rect.moveRight(screen_rect.right() - 10)
        win_rect.moveTop(int((screen.height() - self.frameGeometry().height()) / 2))
        self.move(win_rect.topLeft())

    def _start_hide(self):
        if not self.fixed:
            self.is_hide = True
            self.hide_anim.start()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        if not self.fixed:
            self.hide_timer.start(self.playlist_hide_time)

    def enterEvent(self, event):
        super().enterEvent(event)
        if self.is_hide:
            self.is_hide = False
            self.show_anim.start()
        else:
            if self.hide_timer.isActive():
                self.hide_timer.stop()

    def dragEnterEvent(self, event: QDragEnterEvent):
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            for url in mime_data.urls():
                if url.isLocalFile():
                    if url.toLocalFile().lower().endswith(('.mp3', '.flac', '.wav')):
                        event.acceptProposedAction()
                        return
        elif mime_data.hasFormat('application/x-playlist-row'):  # ✅ 修改这里
            event.acceptProposedAction()
            return
        event.ignore()

    def dropEvent(self, event: QDropEvent):
        """处理外部文件放下"""
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            added = False
            for url in mime_data.urls():
                if url.isLocalFile():
                    path = url.toLocalFile()
                    if path.lower().endswith(('.mp3', '.flac', '.wav')):
                        self.add_to_playlist(path)
                        added = True
            if added:
                event.acceptProposedAction()
            else:
                event.ignore()
            return
        # 内部拖拽已由 DraggableListView 处理，这里不再重复
        if not event.isAccepted():
            event.acceptProposedAction()
