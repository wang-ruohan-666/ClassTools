# views/main_window.py
import base64
import json
import os.path
import time
from typing import Callable, Literal

import requests
from PySide6.QtCore import Qt, QTimer, QEasingCurve, QPropertyAnimation
from PySide6.QtGui import QIcon, QAction, QPixmap, QFont
from PySide6.QtWidgets import QApplication, QWidget, QMenu, QSystemTrayIcon

from MusicPlayer.common.logger import get_logger
from MusicPlayer.managers.settings_manager import SettingsManager
from MusicPlayer.managers.theme_manager import ThemeManager
from MusicPlayer.views.playlist_window import PlaylistWindows
from MusicPlayer.views.settings_window import SettingsWindow
from MusicPlayer.ui_main import Ui_Form as Main

logger = get_logger(__name__)
class MainWindow(QWidget):
    def __init__(self,settings_mgr: SettingsManager, theme_mgr: ThemeManager):
        super().__init__()

        self.FRAME_OPTION_OFFSET_X = -280
        self.FRAME_OPTION_EXPAND_WIDTH = 300
        self.FRAME_OPTION_EXPAND_HEIGHT = 40
        self.FRAME_LOGIN_EXPAND_HEIGHT = 180

        self.settings_mgr = settings_mgr
        self.theme_mgr = theme_mgr

        self.main = Main()
        self.main.setupUi(self)
        self.settings_win = SettingsWindow(settings_mgr, theme_mgr)
        self.playlist_win = PlaylistWindows(settings_mgr, theme_mgr)
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

        self.show_text_anim = QPropertyAnimation(self.main.frame, b"geometry")
        self.options_anim = QPropertyAnimation(self.main.frame, b"geometry")
        self.init_show_anim()
        self.init_options_anim()
        self.main.label.hide()

        self.cookie = ""
        # noinspection SpellCheckingInspection
        if os.path.isfile("data/settings.json"):
            with open("data/settings.json", "r") as f:
                try:
                    data = json.load(f)
                    self.cookie = data.get("cookie")
                except json.JSONDecodeError:
                    logger.warning("settings.json 不合法")
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

        self.connect_global_signals()
        self.theme_mgr.theme_applied.connect(self._on_theme)

        self.show()

    def connect_global_signals(self):
        def change_font(font: QFont):
            new_font = QFont(font.family())
            new_font.setPointSize(QApplication.font().pointSize())
            QApplication.setFont(font)

        def font_size_changed(value: int):
            new_font = QFont(self.settings_mgr.font.family())
            new_font.setPointSize(value)
            QApplication.setFont(new_font)
            if value > 17:
                self.main.label.setMinimumHeight(26)
            else:
                self.main.label.setMinimumHeight(0)

        def anim_speed_changed():
            self.options_anim.setDuration(int(250 / self.settings_mgr.anim_speed))
            self.show_text_anim.setDuration(int(500 / self.settings_mgr.anim_speed))
            self.show_img_anim.setDuration(int(300 / self.settings_mgr.anim_speed))
            self.hide_img_anim.setDuration(int(300 / self.settings_mgr.anim_speed))

        def stay_on_top_changed(checked):
            if checked:
                self.setWindowFlags(
                    Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
            else:
                self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
            self.show()

        self.settings_mgr.font_changed.connect(change_font)
        self.settings_mgr.font_size_changed.connect(font_size_changed)
        self.settings_mgr.anim_speed_changed.connect(anim_speed_changed)
        self.settings_mgr.stay_on_top_changed.connect(stay_on_top_changed)


    def init_timer(self):
        self.timer.timeout.connect(self.check_selection_status)

    def init_show_anim(self):
        self.show_text_anim.setDuration(int(500 / self.settings_win.anim_speed))
        curve = QEasingCurve(QEasingCurve.Type.OutBack)
        curve.setPeriod(1)
        self.show_text_anim.setEasingCurve(curve)

    def init_login_img_show_anim(self):
        def show_login():
            self.main.img.show()
            self.main.labelLogin.show()
            self.main.labelLoginTimeout.show()

        self.show_img_anim.setDuration(int(300 / self.settings_win.anim_speed))
        self.show_img_anim.setStartValue(self.main.frame.geometry())
        self.show_img_anim.setEndValue(self.base_geo.adjusted(0, 0, 0, self.FRAME_LOGIN_EXPAND_HEIGHT))
        self.show_img_anim.finished.connect(show_login)

    def init_login_img_hide_anim(self):
        self.main.img.hide()
        self.main.labelLogin.hide()
        self.main.labelLoginTimeout.hide()
        self.hide_img_anim.setDuration(int(300 / self.settings_win.anim_speed))
        self.hide_img_anim.setStartValue(self.base_geo.adjusted(0, 0, 0, self.FRAME_LOGIN_EXPAND_HEIGHT))
        self.hide_img_anim.setEndValue(self.base_geo)

    def init_options_anim(self):
        self.options_anim.setDuration(int(250 / self.settings_win.anim_speed))
        curve = QEasingCurve(QEasingCurve.Type.OutBack)
        curve.setPeriod(0.1)
        self.options_anim.setEasingCurve(curve)

    def init_open_cloud_music(self):
        def check_cloud_music():
            if self.open_cloud_music.text() == "启用网易云音乐功能":
                logger.info("网易云音乐功能已开启")
                self.open_cloud_music.setText("关闭网易云音乐功能")
                self.check_cookie()
            else:
                logger.info("网易云音乐功能已关闭")
                self.open_cloud_music.setText("启用网易云音乐功能")

        self.open_cloud_music.triggered.connect(check_cloud_music)

    def check_selection_status(self):
        if not self.is_busy and self.task_queue:
            first = self.task_queue[0]
            self.task_queue.pop(0)
            self.show_options(first["allow"], first["refuse"])
        if not self.is_busy and not self.task_queue:
            self.timer.stop()
            logger.debug("Qtimer空闲自动停止")

    def add_task(self, allow: Callable, refuse: Callable):
        self.task_queue.append({"allow": allow, "refuse": refuse})
        if not self.timer.isActive():
            self.timer.start(100)
            logger.debug("Qtimer启动")

    def _on_theme(self,theme: str):
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
        self.main.frame.setStyleSheet("""QWidget#Form > QFrame#frame{
                       border: 2px solid rgb(90, 107, 122);
                       background-color:#2d2d2d; 
                       border-radius:15px;
                   }""")
        for i in [self.main.allow, self.main.refuse]:
            i.setStyleSheet("""QPushButton{
                   background-color:rgb(60, 60, 60); 
                   border-radius:8px;
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
        self.main.frame.setStyleSheet("""QWidget#Form > QFrame#frame{
                       border: 2px solid rgb(119, 136, 153);
                       background-color:#ebebeb;
                       border-radius:15px;
                   }""")
        for i in [self.main.allow, self.main.refuse]:
            i.setStyleSheet("""QPushButton{
                   background-color:rgb(255, 255, 255); 
                   border-radius:8px;
               }""")

    def start_anim(self, show: bool):
        self.options_anim.setStartValue(self.main.frame.geometry())
        if show:
            self.options_anim.setEndValue(
                self.base_geo.adjusted(self.FRAME_OPTION_OFFSET_X, 0, self.FRAME_OPTION_EXPAND_WIDTH,
                                       self.FRAME_OPTION_EXPAND_HEIGHT))
        else:
            self.options_anim.setEndValue(
                self.base_geo.adjusted(self.FRAME_OPTION_OFFSET_X, 0, self.FRAME_OPTION_EXPAND_WIDTH, 0))
        self.options_anim.start()

    def show_text(self, text: str, expand=True, direction: Literal["right", "center", "Left"] = "right",
                  auto_hide_time: int | str = "auto"):
        if auto_hide_time == "auto":
            auto_hide_time = int(len(text) / 6 * 1000 + 3000)
        self.show_text_anim.setStartValue(self.main.frame.geometry())
        self.show_text_anim.setEndValue(
            self.base_geo.adjusted(self.FRAME_OPTION_OFFSET_X, 0, self.FRAME_OPTION_EXPAND_WIDTH, 0))
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
            logger.debug("无法隐藏文字,未显示文字")
            return
        if self.is_busy:
            logger.debug("无法隐藏文字,正在显示选项")
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
        self.settings_win.opacity_effect.setOpacity(0.0)
        self.settings_win.settings_anim.setDuration(int(300 / self.settings_win.anim_speed))
        self.settings_win.settings_anim.start()
        self.settings_win.show()

    def contextMenuEvent(self, event):
        menu = QMenu(self)

        options = QAction("选项")
        app_exit = QAction("退出")
        options.triggered.connect(self.open_settings)
        app_exit.triggered.connect(QApplication.quit)

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
        action_exit.triggered.connect(QApplication.quit)
        tray_menu.addAction(action_show)
        tray_menu.addAction(action_exit)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def post(self, url, no_caching=False, data: dict = None) -> dict:
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
            logger.error(f"请求{get_url}失败")
            raise

    def go_login(self):
        if time.time() - self.last_try_login_time > 90:
            self.last_try_login_time = time.time()
            qr = None
            unikey = None
            try:
                unikey = self.post("/login/qr/key", True).get("data").get("unikey")
                qr = self.post(f"/login/qr/create", True, {"key": unikey, "qrimg": True}).get("data").get("qrimg")
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
                        login_time_reduce.deleteLater()
                        file={}
                        with open("data/settings.json", "r") as f:
                            file=json.load(f)
                        file["cookie"] = self.cookie
                        with open("data/settings.json", "w") as f:
                            f.write(json.dumps(file))
                        self.main.labelLoginTimeout.setText("登录成功")

                        def hide():
                            self.main.img.hide()
                            self.main.labelLogin.hide()
                            self.main.labelLoginTimeout.hide()
                            self.hide_img_anim.start()

                        QTimer.singleShot(3000, hide)
                        logger.info(f"登录成功{self.cookie}")
                    elif data['code'] == 802:
                        if login_time_reduce.isActive():
                            login_time_reduce.stop()
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
            logger.info("距离上次请求二维码时间过短")

    def check_cookie(self):
        try:
            data = self.post("/login/status", True)["data"]
            if data["profile"] is not None:
                self.show_text("已登录", False, "center")
                logger.info("已登录")
                self.login = True
                return
            else:
                logger.warning("cookie无效")
                self.cookie = ""
                self.go_login()
        except requests.exceptions.ConnectionError:
            self.show_text("检查登录失败无法连接服务器")
            logger.error("检查更新失败无法连接服务器")
        except Exception as e:
            self.show_text("检查登录失败")
            logger.error(f"检查更新失败{e}")