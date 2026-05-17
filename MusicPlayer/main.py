# pyside6-uic main.ui -o ui_main.py
import base64
import json
import logging
import os.path
import sys
import time
from typing import Callable,Literal
from logging import debug, info, warning, error

import requests
from PySide6.QtCore import Qt, QTimer, QEasingCurve, QEvent, QPropertyAnimation
from PySide6.QtGui import QIcon, QAction, QFont, QMouseEvent, QPixmap, QGuiApplication
from PySide6.QtWidgets import QApplication, QWidget, QMenu, QSystemTrayIcon, QDialog, QGraphicsOpacityEffect

from ui_main import Ui_Form as Main
from ui_settings import Ui_Form as Settings
from ui_playlist import Ui_Form as Playlist

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.FRAME_OPTION_OFFSET_X = -280
        self.FRAME_OPTION_EXPAND_WIDTH = 300
        self.FRAME_OPTION_EXPAND_HEIGHT = 40
        self.FRAME_LOGIN_EXPAND_HEIGHT = 180

        self.main = Main()
        self.main.setupUi(self)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.main.options.hide()
        self.move_main_window()
        self.tray_icon = QSystemTrayIcon(self)
        self.create_tray_icon()
        self.is_busy = False
        self.task_queue: list[dict[str, Callable]] = []
        self.timer = QTimer(self)
        self.base_geo = self.main.frame.geometry()
        self.init_timer()
        self.opacity_effect = QGraphicsOpacityEffect()
        self.anim_speed = 1.0
        self.show_text_anim = QPropertyAnimation(self.main.frame, b"geometry")
        self.options_anim = QPropertyAnimation(self.main.frame, b"geometry")
        self.init_show_anim()
        self.init_options_anim()
        self.main.label.hide()

        self.settings = Settings()
        self.dialog = QDialog(self)
        self.settings.setupUi(self.dialog)
        self._settings_drag_pos = None
        self.customization_theme = True

        self.settings_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.init_settings()
        self.init_settings_anim()

        self.playlist=Playlist()
        self.playlist_dialog = QDialog(self)
        self.playlist.setupUi(self.playlist_dialog)
        self.move_playlist_window()
        self.playlist_dialog.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.playlist_dialog.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.playlist_dialog.show()

        self.cookie=""
        # noinspection SpellCheckingInspection
        if os.path.isfile("settings.json"):
            with open("settings.json", "r") as f:
                try:
                    data=json.load(f)
                    self.cookie = data.get("cookie")
                except json.JSONDecodeError:
                    warning("settings.json 不合法")
        self.login = False
        self.http_prefix = "http://localhost:3000"
        self.last_try_login_time = 0
        self.show_img_anim = QPropertyAnimation(self.main.frame, b"geometry")
        self.hide_img_anim = QPropertyAnimation(self.main.frame, b"geometry")
        self.init_login_img_show_anim()
        self.init_login_img_hide_anim()
        self.open_cloud_music = QAction("启用网易云音乐功能")
        self.init_open_cloud_music()
        self.login_remaining = 90

        self.apply_system_theme()
        QApplication.styleHints().colorSchemeChanged.connect(self.apply_system_theme)

        self.show()

    def apply_system_theme(self, scheme=None):
        if not self.customization_theme:
            return
        if scheme is None:
            scheme = QApplication.styleHints().colorScheme()

        if scheme == Qt.ColorScheme.Dark:
            self.dark()
        else:
            self.light()

    def dark(self):
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
        self.dialog.setStyleSheet("""QWidget{background-color:#2d2d2d; }""")
        self.settings.root.setStyleSheet("""
#root{
	background-color:#2d2d2d;
    border-bottom-left-radius: 15px;
    border-bottom-right-radius: 15px;
    border-top-left-radius: 0px;
    border-top-right-radius: 0px;
}""")
        self.settings.titlebar.setStyleSheet("""
QFrame{
	background-color:#1C1B22; 
 	border-bottom-left-radius: 0px;
    border-bottom-right-radius: 0px;
    border-top-left-radius: 15px;
    border-top-right-radius: 15px;
}""")
        self.settings.treeWidget.setStyleSheet("""
QTreeWidget {
    color: #ffffff;
    background-color: #2d2d2d;
    border: 1px solid #c0c0c0;
    border-radius: 6px;
    padding: 4px;
    outline: none;
}""")
        self.main.frame.setStyleSheet("""QWidget#Form > QFrame#frame{
            border: 2px solid rgb(90, 107, 122);
            background-color:#2d2d2d; 
            border-radius:15px;
        }""")
        for i in [self.settings.comboBox, self.settings.fontComboBox]:
            i.setStyleSheet("""
QComboBox {
    background-color: #2d2d2d;
    border: 1px solid #5a5a5a;
    border-radius: 6px;
    padding: 4px 8px;
    min-height: 24px;
    color: #ffffff;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid #4a4a4a;
    border-top-right-radius: 6px;
    border-bottom-right-radius: 6px;
}

QComboBox::down-arrow {
    width: 8px;
    height: 8px;
}

QComboBox QAbstractItemView {
    background-color: #2d2d2d;
    border: 1px solid #5a5a5a;
    border-radius: 4px;
    selection-background-color: #3c3c3c;
    selection-color: #ffffff;
    padding: 4px;
    outline: none;
}

QComboBox QAbstractItemView::item {
    min-height: 24px;
    padding: 4px 8px;
    border-radius: 3px;
}

QComboBox QAbstractItemView::item:hover {
    background-color: #3c3c3c;
}""")
        for i in [self.main.allow, self.main.refuse]:
            i.setStyleSheet("""QPushButton{
            	background-color:rgb(60, 60, 60); 
            	border-radius:8px;
            }""")
        self.settings.sliderSlider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: #3c3c3c;
                border-radius: 3px;
                margin: 2px 0;
            }

            QSlider::handle:horizontal {
                width: 16px;
                height: 16px;
                margin: -6px 0;
                background: #2d2d2d;
                border: 2px solid #5a5a5a;
                border-radius: 8px;
            }

            QSlider::handle:horizontal:hover {
                border-color: #888888;
            }

            QSlider::handle:horizontal:pressed {
                background: #4a4a4a;
                border-color: #aaaaaa;
            }

            QSlider::sub-page:horizontal {
                background: #448aff;
                border-radius: 3px;
            }

            QSlider::add-page:horizontal {
                background: #3c3c3c;
                border-radius: 3px;
            }""")
        self.settings.checkBox.setStyleSheet("""
QCheckBox {
    spacing: 8px;
    color: #ffffff;
}

QCheckBox::indicator {
    width: 10px;
    height: 10px;
    border: 2px solid #5a5a5a;
    border-radius: 4px;
    background-color: #2d2d2d;
}

QCheckBox::indicator:checked {
    background-color: #448aff;
    border-color: #448aff;
}

QCheckBox::indicator:checked:hover {
    background-color: #5c9dff;
    border-color: #5c9dff;
}

QCheckBox::indicator:unchecked:hover {
    border-color: #888888;
}

QCheckBox::indicator:disabled {
    border-color: #4a4a4a;
    background-color: #3c3c3c;
}

QCheckBox::indicator:checked:disabled {
    background-color: #2a4a8a;
    border-color: #2a4a8a;
}""")

    def light(self):
        self.dialog.setStyleSheet("")
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
        self.main.frame.setStyleSheet("""QWidget#Form > QFrame#frame{
            border: 2px solid rgb(119, 136, 153);
            background-color:#ebebeb;
            border-radius:15px;
        }""")
        self.settings.root.setStyleSheet("""
#root{
	background-color:#F0F0F0;
    border-bottom-left-radius: 15px;
    border-bottom-right-radius: 15px;
    border-top-left-radius: 0px;
    border-top-right-radius: 0px;
}""")
        self.settings.treeWidget.setStyleSheet("""
QTreeWidget {
    background-color: #ffffff;
    border: 1px solid #c0c0c0;
    border-radius: 6px;
    padding: 4px;
    outline: none;
    color: #000000;
}""")
        self.settings.titlebar.setStyleSheet("""
QFrame{
	background-color:rgb(255, 255, 255); 
 	border-bottom-left-radius: 0px;
    border-bottom-right-radius: 0px;
    border-top-left-radius: 15px;
    border-top-right-radius: 15px;
}""")
        for i in [self.settings.comboBox, self.settings.fontComboBox]:
            i.setStyleSheet("""
QComboBox {
    background-color: #ffffff;
    border: 1px solid #c0c0c0;
    border-radius: 6px;
    padding: 4px 8px;
    min-height: 24px;
    color: #000000;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid #e0e0e0;
    border-top-right-radius: 6px;
    border-bottom-right-radius: 6px;
}

QComboBox::down-arrow {
    width: 8px;
    height: 8px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    border: 1px solid #c0c0c0;
    border-radius: 4px;
    selection-background-color: #e0e0e0;
    selection-color: #000000;
    padding: 4px;
    outline: none;
}

QComboBox QAbstractItemView::item {
    min-height: 24px;
    padding: 4px 8px;
    border-radius: 3px;
}

QComboBox QAbstractItemView::item:hover {
    background-color: #f0f0f0;
}""")
        for i in [self.main.allow, self.main.refuse]:
            i.setStyleSheet("""QPushButton{
            	background-color:rgb(255, 255, 255); 
            	border-radius:8px;
            }""")
        self.settings.sliderSlider.setStyleSheet("""
        QSlider::groove:horizontal {
            height: 6px;
            background: #e0e0e0;
            border-radius: 3px;
            margin: 2px 0;
        }

        QSlider::handle:horizontal {
            width: 16px;
            height: 16px;
            margin: -6px 0;
            background: #ffffff;
            border: 2px solid #c0c0c0;
            border-radius: 8px;
        }

        QSlider::handle:horizontal:hover {
            border-color: #888888;
        }

        QSlider::handle:horizontal:pressed {
            background: #f0f0f0;
            border-color: #555555;
        }

        QSlider::sub-page:horizontal {
            background: #448aff;
            border-radius: 3px;
        }

        QSlider::add-page:horizontal {
            background: #e0e0e0;
            border-radius: 3px;
        }

        /* 可选：刻度线 */
        QSlider::tick:horizontal {
            background: #c0c0c0;
            width: 1px;
        }""")
        self.settings.checkBox.setStyleSheet("""
QCheckBox {
    spacing: 8px;
    color: #000000;
}

QCheckBox::indicator {
    width: 10px;
    height: 10px;
    border: 2px solid #c0c0c0;
    border-radius: 4px;
    background-color: #ffffff;
}

QCheckBox::indicator:checked {
    background-color: #448aff;
    border-color: #448aff;
}

QCheckBox::indicator:checked:hover {
    background-color: #5c9dff;
    border-color: #5c9dff;
}

QCheckBox::indicator:unchecked:hover {
    border-color: #888888;
}

QCheckBox::indicator:disabled {
    border-color: #d0d0d0;
    background-color: #f5f5f5;
}

QCheckBox::indicator:checked:disabled {
    background-color: #a0c4ff;
    border-color: #a0c4ff;
}""")

    def init_settings(self):
        self.settings.settingsFrame.hide()
        self.settings.animSpeedFrame.hide()
        self.dialog.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.dialog.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.settings.treeWidget.itemClicked.connect(self.tree_item_change)
        self.dialog.finished.connect(lambda: self.settings.fontComboBox.lineEdit().removeEventFilter(self))
        self.settings.comboBox.currentTextChanged.connect(self.current_text_changed)
        self.settings.quit.clicked.connect(self.dialog.close)
        self.settings.titlebar.installEventFilter(self)
        self.settings.fontComboBox.currentFontChanged.connect(self.current_font_changed)
        self.settings.sliderSlider.valueChanged.connect(self.font_size_slider_value_changed)
        self.settings.sliderSliderSpeed.valueChanged.connect(self.anim_speed_slider_value_changed)
        self.settings.checkBox.toggled.connect(self.stay_on_top_check_box_changed)

    def init_timer(self):
        self.timer.timeout.connect(self.check_selection_status)

    def init_show_anim(self):
        self.show_text_anim.setDuration(int(500 / self.anim_speed))
        curve = QEasingCurve(QEasingCurve.Type.OutBack)
        curve.setPeriod(1)
        self.show_text_anim.setEasingCurve(curve)

    def init_login_img_show_anim(self):
        def show_login():
            self.main.img.show()
            self.main.labelLogin.show()
            self.main.labelLoginTimeout.show()

        self.show_img_anim.setDuration(int(300 / self.anim_speed))
        self.show_img_anim.setStartValue(self.main.frame.geometry())
        self.show_img_anim.setEndValue(self.base_geo.adjusted(0, 0, 0, self.FRAME_LOGIN_EXPAND_HEIGHT))
        self.show_img_anim.finished.connect(show_login)

    def init_login_img_hide_anim(self):
        self.main.img.hide()
        self.main.labelLogin.hide()
        self.main.labelLoginTimeout.hide()
        self.hide_img_anim.setDuration(int(300 / self.anim_speed))
        self.hide_img_anim.setStartValue(self.base_geo.adjusted(0, 0, 0, self.FRAME_LOGIN_EXPAND_HEIGHT))
        self.hide_img_anim.setEndValue(self.base_geo)

    def init_options_anim(self):
        self.options_anim.setDuration(int(250 / self.anim_speed))
        curve = QEasingCurve(QEasingCurve.Type.OutBack)
        curve.setPeriod(0.1)
        self.options_anim.setEasingCurve(curve)

    def init_settings_anim(self):
        self.settings_anim.setDuration(int(300 / self.anim_speed))
        self.opacity_effect.setOpacity(0.0)
        self.settings_anim.setStartValue(0.0)
        self.settings_anim.setEndValue(1.0)

    def init_open_cloud_music(self):
        def check_cloud_music():
            if self.open_cloud_music.text() == "启用网易云音乐功能":
                info("网易云音乐功能已开启")
                self.open_cloud_music.setText("关闭网易云音乐功能")
                self.check_cookie()
            else:
                info("网易云音乐功能已关闭")
                self.open_cloud_music.setText("启用网易云音乐功能")

        self.open_cloud_music.triggered.connect(check_cloud_music)

    def update_theme(self):
        if self.customization_theme:
            scheme = QApplication.styleHints().colorScheme()
            if scheme == Qt.ColorScheme.Dark:
                self.dark()
            else:
                self.light()
        else:
            if self.settings.comboBox.currentText() == "浅色":
                self.light()
            else:
                self.dark()

    def eventFilter(self, watched, event: QEvent | QMouseEvent, /):
        if watched == self.settings.fontComboBox.lineEdit() and event.type() == QEvent.Type.MouseButtonPress:
            self.settings.fontComboBox.showPopup()
            return True
        if watched == self.settings.titlebar:
            if event.type() == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
                self._settings_drag_pos = event.globalPosition().toPoint() - self.dialog.frameGeometry().topLeft()
                return True
            elif event.type() == QEvent.Type.MouseMove and self._settings_drag_pos is not None:
                new_pos = event.globalPosition().toPoint() - self._settings_drag_pos
                self.dialog.move(new_pos)
                return True
            elif event.type() == QEvent.Type.MouseButtonRelease:
                self._settings_drag_pos = None
                return True

        return super().eventFilter(watched, event)

    def stay_on_top_check_box_changed(self, checked: bool):
        if checked:
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.show()

    def font_size_slider_value_changed(self, value):
        self.settings.labelSize.setText(str(round(value / 5.0)))
        font = self.settings.fontComboBox.font()
        new_font = QFont(font.family())
        new_font.setPointSize(round(value / 5.0))
        app.setFont(new_font)
        if round(value / 5.0) > 17:
            self.main.label.setMinimumHeight(26)
        else:
            self.main.label.setMinimumHeight(0)
        self.update_theme()

    def anim_speed_slider_value_changed(self, value):
        self.settings.labelSpeed.setText(str(value / 10))
        self.anim_speed = value / 10
        self.options_anim.setDuration(int(250 / self.anim_speed))
        self.settings_anim.setDuration(int(300 / self.anim_speed))
        self.show_text_anim.setDuration(int(500 / self.anim_speed))
        self.show_img_anim.setDuration(int(300 / self.anim_speed))
        self.hide_img_anim.setDuration(int(300 / self.anim_speed))

    def current_font_changed(self, font: QFont):
        new_font = QFont(font.family())
        new_font.setPointSize(app.font().pointSize())
        app.setFont(new_font)
        self.apply_system_theme()
        self.update_theme()

    def current_text_changed(self, text):
        if self.customization_theme:
            QApplication.styleHints().colorSchemeChanged.disconnect(self.apply_system_theme)
        self.customization_theme = False
        if text == "深色":
            self.dark()
        elif text == "浅色":
            self.light()
        elif text == "跟随系统":
            self.customization_theme = True
            QApplication.styleHints().colorSchemeChanged.connect(self.apply_system_theme)
            self.apply_system_theme()

    def tree_item_change(self, item, column):
        self.settings.settingsFrame.hide()
        self.settings.animSpeedFrame.hide()
        text = item.text(column)
        if text == "外观":
            self.settings.settingsFrame.show()
        elif text == "动画":
            self.settings.animSpeedFrame.show()

    def check_selection_status(self):
        if not self.is_busy and self.task_queue:
            first = self.task_queue[0]
            self.task_queue.pop(0)
            self.show_options(first["allow"], first["refuse"])
        if not self.is_busy and not self.task_queue:
            self.timer.stop()
            debug("Qtimer空闲自动停止")

    def add_task(self, allow: Callable, refuse: Callable):
        self.task_queue.append({"allow": allow, "refuse": refuse})
        if not self.timer.isActive():
            self.timer.start(100)
            debug("Qtimer启动")

    def start_anim(self, show: bool):
        self.options_anim.setStartValue(self.main.frame.geometry())
        if show:
            self.options_anim.setEndValue(self.base_geo.adjusted(self.FRAME_OPTION_OFFSET_X, 0, self.FRAME_OPTION_EXPAND_WIDTH, self.FRAME_OPTION_EXPAND_HEIGHT))
        else:
            self.options_anim.setEndValue(self.base_geo.adjusted(self.FRAME_OPTION_OFFSET_X, 0, self.FRAME_OPTION_EXPAND_WIDTH, 0))
        self.options_anim.start()

    def show_text(self, text: str,expand=True,direction:Literal["right","center","Left"]="right",auto_hide_time:int|str="auto"):
        if auto_hide_time == "auto":
            auto_hide_time=int(len(text)/6*1000+3000)
        self.show_text_anim.setStartValue(self.main.frame.geometry())
        self.show_text_anim.setEndValue(self.base_geo.adjusted(self.FRAME_OPTION_OFFSET_X, 0, self.FRAME_OPTION_EXPAND_WIDTH, 0))
        if direction == "center":
            self.main.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        elif direction == "left":
            self.main.label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        else:
            self.main.label.setAlignment(Qt.AlignmentFlag.AlignRight)
        if expand:
            self.show_text_anim.start()
            def finished_anim():
                self.main.label.setText(text)
                self.main.label.show()
                self.show_text_anim.finished.disconnect(finished_anim)
            self.show_text_anim.finished.connect(finished_anim)
            QTimer.singleShot(auto_hide_time, self.hide_text)
        else:
            def finished_anim():
                self.main.label.hide()
                self.main.label.setMaximumWidth(16777215)
            self.main.label.setMaximumWidth(370)
            self.main.label.setText(text)
            self.main.label.show()
            QTimer.singleShot(auto_hide_time, finished_anim)


    def hide_text(self):
        if not self.main.label.isVisible():
            debug("无法隐藏文字,未显示文字")
            return
        if self.is_busy:
            debug("无法隐藏文字,正在显示选项")
            return
        self.main.label.hide()
        self.show_text_anim.setStartValue(self.main.frame.geometry())
        self.show_text_anim.setEndValue(self.base_geo)
        self.show_text_anim.start()

    def show_options(self, allow: Callable, refuse: Callable):
        if self.is_busy:
            self.add_task(allow, refuse)
            return
        self.is_busy = True

        def restore():
            def after():
                self.is_busy = False

            self.main.options.hide()
            self.start_anim(False)
            self.main.allow.clicked.disconnect()
            self.main.refuse.clicked.disconnect()
            self.options_anim.finished.connect(after, Qt.ConnectionType.SingleShotConnection)

        def click_allow():
            allow()
            restore()

        def click_refuse():
            refuse()
            restore()

        self.main.options.show()
        self.start_anim(True)
        self.main.allow.clicked.connect(click_allow)
        self.main.refuse.clicked.connect(click_refuse)

    def open_settings(self):
        self.dialog.winId()
        self.dialog.setGraphicsEffect(self.opacity_effect)
        self.settings_anim.setDuration(int(300 / self.anim_speed))
        self.settings.fontComboBox.lineEdit().installEventFilter(self)
        self.settings_anim.start()
        self.dialog.exec()

    def contextMenuEvent(self, event):
        menu = QMenu(self)

        options = QAction("选项")
        app_exit = QAction("退出")
        options.triggered.connect(self.open_settings)
        app_exit.triggered.connect(app.quit)

        menu.addAction(self.open_cloud_music)
        menu.addAction(options)
        menu.addAction(app_exit)
        menu.exec(event.globalPos())

    def move_main_window(self):
        screen_rect = QApplication.primaryScreen().availableGeometry()
        win_rect = self.frameGeometry()
        win_rect.moveCenter(screen_rect.center())
        win_rect.setTop(screen_rect.top() + 10)
        self.move(win_rect.topLeft())

    def move_playlist_window(self):
        screen = QGuiApplication.primaryScreen().size()
        screen_rect = QApplication.primaryScreen().availableGeometry()
        win_rect = self.playlist_dialog.frameGeometry()
        win_rect.moveRight(screen_rect.right()-10)
        win_rect.moveTop(int((screen.height()-self.playlist_dialog.frameGeometry().height())/2))
        self.playlist_dialog.move(win_rect.topLeft())

    def create_tray_icon(self):
        # self.tray_icon.setIcon(QIcon("任务进程.png"))
        def show():
            self.show()
            self.raise_()
            self.activateWindow()

        tray_menu = QMenu(self)
        self.tray_icon.setIcon(QIcon.fromTheme("computer"))
        action_show = QAction("显示窗口", self)
        action_show.triggered.connect(show)
        action_exit = QAction("退出", self)
        action_exit.triggered.connect(app.quit)
        tray_menu.addAction(action_show)
        tray_menu.addAction(action_exit)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def post(self, url, no_caching=False, data: dict = None)->dict:
        if data is None:
            data = {}
        if self.cookie:
            data["cookie"] = self.cookie
        get_url = f"{self.http_prefix}{url}"
        try:
            if no_caching:
                return requests.post(f"{get_url}?timestamp={int(time.time())}", data=data).json()
            else:
                return requests.post(get_url, data=data).json()
        except requests.exceptions.ConnectionError:
            error(f"请求{get_url}失败")
            raise

    def go_login(self):
        if time.time() - self.last_try_login_time > 90:
            self.last_try_login_time = time.time()
            qr = None
            unikey = None
            try:
                unikey = self.post("/login/qr/key", True).get("data").get("unikey")
                qr = self.post(f"/login/qr/create", False, {"key": unikey, "qrimg": True}).get("data").get("qrimg")
            except requests.exceptions.ConnectionError:
                self.show_text("生成二维码登录失败")
            if qr:
                if ',' in qr and qr.startswith('data:'):
                    qr = qr.split(',', 1)[1]
                img_bytes = base64.b64decode(qr)
                pixmap = QPixmap()
                pixmap.loadFromData(img_bytes)
                self.main.img.setPixmap(pixmap)
                self.main.img.setScaledContents(True)
                self.show_img_anim.start()
                login_check = QTimer(self)
                login_time_reduce = QTimer(self)

                def check_login():
                    data = self.post(f"/login/qr/check", True, {"key": unikey})
                    if data.get("code") == 803:
                        self.cookie = data["cookie"]
                        login_time_reduce.stop()
                        login_time_reduce.deleteLater()
                        self.main.labelLoginTimeout.setText("登录成功")

                        def hide():
                            self.main.img.hide()
                            self.main.labelLogin.hide()
                            self.main.labelLoginTimeout.hide()
                            self.hide_img_anim.start()

                        QTimer.singleShot(3000, hide)
                        info(f"登录成功{self.cookie}")
                    elif data['code'] == 802:
                        login_time_reduce.stop()
                        login_time_reduce.deleteLater()
                        self.main.labelLoginTimeout.setText("等待确认")

                self.login_remaining = 90
                def time_reduce():
                    self.login_remaining -= 1
                    self.main.labelLoginTimeout.setText(f"{self.login_remaining}S")
                    if self.login_remaining <= 0:
                        login_check.stop()
                        login_check.deleteLater()

                login_time_reduce.timeout.connect(time_reduce)
                login_time_reduce.setInterval(1000)
                login_time_reduce.start()

                login_check.timeout.connect(check_login)
                login_check.setInterval(3000)
                login_check.start()

                def stop_login_check():
                    if login_check.isActive():
                        login_check.stop()
                        self.go_login()

                QTimer.singleShot(90000, stop_login_check)


        else:
            info("距离上次请求二维码时间过短")

    def check_cookie(self):
        try:
            data = self.post("/login/status", True)["data"]
            if data["profile"] is not None:
                self.show_text("已登录",False,"center")
                info("已登录")
                self.login = True
                return
            else:
                warning("cookie无效")
                self.cookie = ""
                self.go_login()
        except requests.exceptions.ConnectionError:
            self.show_text("检查登录失败无法连接服务器")
            error("检查更新失败无法连接服务器")
        except Exception as e:
            self.show_text("检查登录失败")
            error(f"检查更新失败{e}")


app = QApplication(sys.argv)
app.setWindowIcon(QIcon.fromTheme("computer"))
window = MainWindow()
window.show()
sys.exit(app.exec())
