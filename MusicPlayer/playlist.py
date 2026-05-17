from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QWidget, QApplication

from ui_playlist import Ui_Form as Playlist


class PlaylistWindows(QWidget):
    def __init__(self):
        super().__init__()
        self.playlist = Playlist()
        self.playlist.setupUi(self)
        self.move_playlist_window()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.show()

    def move_playlist_window(self):
        screen = QGuiApplication.primaryScreen().size()
        screen_rect = QApplication.primaryScreen().availableGeometry()
        win_rect = self.frameGeometry()
        win_rect.moveRight(screen_rect.right() - 10)
        win_rect.moveTop(int((screen.height() - self.frameGeometry().height()) / 2))
        self.move(win_rect.topLeft())
