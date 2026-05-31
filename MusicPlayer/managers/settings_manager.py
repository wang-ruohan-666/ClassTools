# managers/settings_manager.py
import json
from pathlib import Path

from PySide6.QtCore import QObject, Signal, QTimer
from PySide6.QtGui import QFont

from MusicPlayer.common.logger import get_logger

logger = get_logger(__name__)


class SettingsManager(QObject):
    """全局用户设置管理器，在修改时发射信号。"""
    theme_changed = Signal(str)  # 主题 参数: "深色"/"浅色"/"跟随系统"
    font_changed = Signal(QFont)  # 字体
    font_size_changed = Signal(int)  # 字体大小
    anim_speed_changed = Signal(float)  # 动画速度
    stay_on_top_changed = Signal(bool)  # 保持指定

    def __init__(self):
        super().__init__()
        self._loading = False
        self._theme = "跟随系统"
        self._font = QFont()
        self._font_size = 9
        self._anim_speed = 1.0
        self._stay_on_top = False
        self.config_dir = Path.home() / "MusicPlayer"
        self.config_dir.mkdir(exist_ok=True)
        self.file = self.config_dir / "settings.json"
        self._save_timer = QTimer()
        self._save_timer.setSingleShot(True)
        self._save_timer.timeout.connect(self._save)
        self._save_debounce_ms = 300

        self._load()

    def _schedule_save(self):
        """延迟保存，避免频繁 I/O"""
        if getattr(self, '_loading', False):
            return
        self._save_timer.start(self._save_debounce_ms)

    def _load(self):
        """从 settings.json 加载配置，文件不存在或损坏时保持默认值。"""
        if not self.file.exists():
            self._save()
            return
        data = {}
        try:
            with open(self.file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            logger.exception("读取配置文件失败")
        self._loading = True
        try:
            if "theme" in data:
                self._theme = data["theme"]
            if "font" in data:
                font = QFont()
                self._font = font
            if "font_size" in data:
                self._font_size = data["font_size"]
            if "anim_speed" in data:
                self._anim_speed = data["anim_speed"]
            if "stay_on_top" in data:
                self._stay_on_top = data["stay_on_top"]
        finally:
            self._loading = False
        self._save()

    def _save(self):
        """将当前所有配置保存到 settings.json。"""
        if getattr(self, "_loading", False):
            return

        data = {
            "theme": self._theme,
            "font": self._font.toString(),
            "font_size": self._font_size,
            "anim_speed": self._anim_speed,
            "stay_on_top": self._stay_on_top,
        }
        tmp_file = self.file.with_suffix(".tmp")
        try:
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            tmp_file.replace(self.file)
        except OSError:
            logger.exception("保存配置文件失败")

    @property
    def theme(self) -> str:
        return self._theme

    @theme.setter
    def theme(self, value: str) -> None:
        if self._theme != value:
            self._theme = value
            self.theme_changed.emit(value)
            self._schedule_save()

    @property
    def font(self) -> QFont:
        return self._font

    @font.setter
    def font(self, value: QFont) -> None:
        if self._font != value:
            self._font = value
            self.font_changed.emit(value)
            self._schedule_save()

    @property
    def font_size(self) -> int:
        return self._font_size

    @font_size.setter
    def font_size(self, value: int) -> None:
        if self._font_size != value:
            self._font_size = value
            self.font_size_changed.emit(value)
            self._schedule_save()

    @property
    def anim_speed(self) -> float:
        return self._anim_speed

    @anim_speed.setter
    def anim_speed(self, value: float) -> None:
        if self._anim_speed != value:
            self._anim_speed = value
            self.anim_speed_changed.emit(value)
            self._schedule_save()

    @property
    def stay_on_top(self) -> bool:
        return self._stay_on_top

    @stay_on_top.setter
    def stay_on_top(self, value: bool) -> None:
        if self._stay_on_top != value:
            self._stay_on_top = value
            self.stay_on_top_changed.emit(value)
            self._schedule_save()
