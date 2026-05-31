# views/search_window.py
from PySide6.QtCore import Qt, QPropertyAnimation, QEvent
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QWidget, QGraphicsOpacityEffect

from MusicPlayer.managers.settings_manager import SettingsManager
from MusicPlayer.managers.theme_manager import ThemeManager
from MusicPlayer.ui_search import Ui_Form as Search


class SearchWindow(QWidget):
    def __init__(self, settings_mgr: SettingsManager, theme_mgr: ThemeManager):
        super().__init__()
        self.search = Search()
        self.search.setupUi(self)
        self.settings_mgr = settings_mgr
        self.theme_mgr = theme_mgr
        self.anim_speed = settings_mgr.anim_speed
        self._search_drag_pos = None
        self.opacity_effect = QGraphicsOpacityEffect()
        self.search_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_effect.setOpacity(0.0)
        self.init_search()
        self.init_settings_anim()
        self.connect_global_signals()

    def init_search(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.search.titlebar.installEventFilter(self)
        self.search.quit.clicked.connect(self.close)

    def init_settings_anim(self):
        self.search_anim.setDuration(int(300 / self.anim_speed))
        self.search_anim.setStartValue(0.0)
        self.search_anim.setEndValue(1.0)
        self.setGraphicsEffect(self.opacity_effect)

    def connect_global_signals(self):
        def anim_speed_changed(speed: float):
            self.search_anim.setDuration(int(250 / speed))

        def stay_on_top_changed(checked):
            if self.isVisible():
                if checked:
                    self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
                else:
                    self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
                self.show()
            else:
                if checked:
                    self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
                else:
                    self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)

        self.settings_mgr.anim_speed_changed.connect(anim_speed_changed)
        self.settings_mgr.stay_on_top_changed.connect(stay_on_top_changed)
        self.theme_mgr.theme_applied.connect(self._on_theme)

    def eventFilter(self, watched, event: QEvent | QMouseEvent, /):
        if watched == self.search.titlebar:
            if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
                self._search_drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                return True
            elif event.type() == QEvent.Type.MouseMove and self._search_drag_pos is not None:
                new_pos = event.globalPosition().toPoint() - self._search_drag_pos
                self.move(new_pos)
                return True
            elif event.type() == QEvent.Type.MouseButtonRelease:
                self._search_drag_pos = None
                return True
        return super().eventFilter(watched, event)

    def _on_theme(self, theme: str):
        if theme == "dark":
            self._dark()
        elif theme == "light":
            self._light()

    def _dark(self):
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
        self.search.frame.setStyleSheet("""QWidget#Form > QFrame#frame{
                               border: 2px solid rgb(90, 107, 122);
                               background-color:#1E1E1E; 
                               border-radius:15px;
                           }""")
        self.search.inputFrame.setStyleSheet("""QWidget#frame > QFrame#inputFrame{
                               border: 2px solid rgb(90, 107, 122);
                               background-color:#1E1E1E; 
                               border-radius:15px;
                           }""")
        self.search.titlebar.setStyleSheet("""
    QFrame{
    background-color:#1C1B22; 
    border-bottom-left-radius: 0px;
    border-bottom-right-radius: 0px;
    border-top-left-radius: 15px;
    border-top-right-radius: 15px;
    }""")
        self.search.searchLineEdit.setStyleSheet("""QLineEdit{
        	background-color:#1E1E1E;
        }""")

    def _light(self):
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
        self.search.frame.setStyleSheet("""QWidget#Form > QFrame#frame{
                               border: 2px solid rgb(159, 159, 159);
                               background-color:#ebebeb;
                               border-radius:15px;
                           }""")
        self.search.inputFrame.setStyleSheet("""QWidget#frame > QFrame#inputFrame{
                               border: 2px solid rgb(159, 159, 159);
                               background-color:#ebebeb;
                               border-radius:15px;
                           }""")
        self.search.titlebar.setStyleSheet("""
QFrame{
    background-color:rgb(255, 255, 255); 
    border-bottom-left-radius: 0px;
    border-bottom-right-radius: 0px;
    border-top-left-radius: 15px;
    border-top-right-radius: 15px;
}""")
        self.search.searchLineEdit.setStyleSheet("""QLineEdit{
	background-color:#ebebeb; 
}""")

    def showEvent(self, event):
        super().showEvent(event)
        # 确保动画时长与当前动画速度同步
        self.search_anim.setDuration(int(300 / self.anim_speed))
        self.search_anim.start()
