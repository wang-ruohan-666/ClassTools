# managers/theme_manager.py
from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QApplication

from MusicPlayer.common.logger import get_logger
from MusicPlayer.managers.settings_manager import SettingsManager

logger = get_logger(__name__)


class ThemeManager(QObject):
    """主题管理器：负责根据当前主题设置应用程序样式。"""

    # 主题常量
    THEME_DARK = "dark"
    THEME_LIGHT = "light"
    # 自定义信号：通知其他组件主题已具体应用到 dark / light
    theme_applied = Signal(str)
    def __init__(self, settings_manager: SettingsManager):
        """
        :param settings_manager: SettingsManager 实例，用于监听主题变化
        """
        super().__init__()
        self._settings_mgr = settings_manager
        self._current_theme = self.THEME_LIGHT  # 实际应用的主题（dark/light）
        self._pending_theme = None  # 用于延迟刷新的标志

        # 连接设置管理器的信号
        self._settings_mgr.theme_changed.connect(self._on_theme_setting_changed)

    def _on_theme_setting_changed(self, setting: str):
        """
        当 SettingsManager.theme 改变时调用。
        setting 取值: "深色", "浅色", "跟随系统"
        """
        # 确定实际要应用的主题名称（dark / light）
        if setting == "深色":
            actual_theme = self.THEME_DARK
        elif setting == "浅色":
            actual_theme = self.THEME_LIGHT
        else:  # 跟随系统
            scheme = QApplication.styleHints().colorScheme()
            actual_theme = self.THEME_DARK if scheme == Qt.ColorScheme.Dark else self.THEME_LIGHT

        if self._current_theme == actual_theme:
            return

        self._current_theme = actual_theme
        # 延迟一点应用，避免在信号链中频繁重绘
        self._pending_theme = actual_theme
        QTimer.singleShot(100, self._apply_theme)

    def _apply_theme(self):
        """实际执行样式表应用（延迟调用）"""
        if self._pending_theme is None:
            return
        theme = self._pending_theme
        self._pending_theme = None

        logger.info("应用主题: %s", theme)
        # 通知所有控件
        self.theme_applied.emit(theme)

    def get_current_theme_name(self) -> str:
        """返回当前实际应用的主题名称 ('dark' 或 'light')"""
        return self._current_theme
