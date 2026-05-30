# views/playlist_window.py
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QTimer, QEasingCurve
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtWidgets import QWidget, QApplication, QListView, QAbstractItemView

from MusicPlayer.GetSongInfo import get_song_info
from MusicPlayer.PlaylistDelegate import PlaylistDelegate
from MusicPlayer.PlaylistModel import PlaylistModel
from MusicPlayer.SongItem import SongItem
from MusicPlayer.managers.settings_manager import SettingsManager
from MusicPlayer.managers.theme_manager import ThemeManager
from MusicPlayer.ui_playlist import Ui_Form as Playlist


class PlaylistWindows(QWidget):
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

        self.playlist_model = PlaylistModel()
        self.setAcceptDrops(True)
        self.playlist_delegate = PlaylistDelegate(is_dark=(self.theme_mgr.get_current_theme_name() == "dark"))

        self.playlist_view = QListView()

        self.init_playlist()
        self.init_show_anim()
        self.init_hide_anim()
        self.init_playlist_view()
        self.connect_signals()
        self.theme_mgr.theme_applied.connect(self._on_theme)

        self.show()

    def init_playlist_view(self):
        self.playlist_view.setModel(self.playlist_model)
        self.playlist_view.setItemDelegate(self.playlist_delegate)
        self.playlist_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.playlist_view.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.playlist_view.setDragEnabled(True)
        self.playlist_view.setAcceptDrops(True)
        self.playlist_view.setDropIndicatorShown(True)
        self.playlist_view.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.playlist_view.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.playlist.root.layout().addWidget(self.playlist_view)

    def init_playlist(self):
        self.init_fixed()
        # 自动隐藏定时器
        self.hide_timer.timeout.connect(self._start_hide)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.start(self.playlist_hide_time)

    def connect_signals(self):
        # 动画速度变化 -> 更新动画时长
        self.settings_mgr.anim_speed_changed.connect(self._update_anim_durations)
        # 置顶变化（如果需要）
        self.settings_mgr.stay_on_top_changed.connect(self._update_stay_on_top)

    def _on_theme(self, theme: str):
        if theme == "dark":
            self._dark()
        elif theme == "light":
            self._light()

    def _dark(self):
        self.playlist_delegate.is_dark = True
        self.playlist_view.viewport().update()
        self.setStyleSheet("""
                        QWidget 
                        {
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
                        }""")
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
            border-radius: 0px;
            min-width: 120px;
        }

        QMenu::item:selected {
            background-color: #e0e0e0;
            border-radius: 4px;
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
        }""")
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
                self.playlist.png.setIcon(QIcon(""))
            else:
                self.fixed = True
                self.playlist.png.setIcon(QIcon("data/fixed.png"))

        self.playlist.png.setIcon(QIcon("data/unpin.png"))
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

    def add_to_playlist(self, path):
        info = get_song_info(path)
        item = SongItem(info[0], info[1], info[2], info[3])
        self.playlist_model.add_song(item)

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

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        valid_extensions = ('.mp3', '.flac', '.wav')
        for url in urls:
            file_path = url.toLocalFile()
            if file_path.lower().endswith(valid_extensions):
                self.add_to_playlist(file_path)
        event.acceptProposedAction()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
