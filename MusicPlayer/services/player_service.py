# services/player_service.py
import os

# 将项目根目录添加到 PATH，使 mpv 能找到 libmpv-2.dll
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ["PATH"] = project_root + os.pathsep + os.environ["PATH"]

from PySide6.QtCore import QObject, Signal, QTimer
import mpv
from MusicPlayer.SongItem import SongItem
from MusicPlayer.common.logger import get_logger

logger = get_logger(__name__)


class PlayerService(QObject):
    """基于 mpv 的音频播放服务，支持动态响度均衡与峰值监测"""

    # 信号
    position_changed = Signal(int)          # 毫秒
    duration_changed = Signal(int)          # 毫秒
    state_changed = Signal(str)             # "playing", "paused", "stopped"
    current_song_changed = Signal(object)   # SongItem
    peak_changed = Signal(float)            # 音频峰值 (0.0 ~ 1.0)
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_song = None
        self._is_playing = False
        self._peak_supported = False

        # 直接创建正式播放器（不提前调用 _init_peak_support）
        self.player = mpv.MPV(
            video=False,
            audio_display=False,
            input_default_bindings=False,
            input_vo_keyboard=False,
        )

        # 默认启用动态响度均衡
        self._dynaudnorm_enabled = True
        self.player.command('af', 'add', 'dynaudnorm')

        # 尝试启用原生音频峰值（若支持）
        try:
            # 某些构建需要 audio-peak-detection 选项
            self.player['audio-peak-detection'] = True
            self.player.observe_property('audio-peak', self._on_peak)
            self._peak_supported = True
            logger.info("mpv 原生音频峰值检测已启用")
        except Exception:
            logger.warning("mpv 不支持原生音频峰值，将使用预分析数据")

        # 监听暂停状态
        self.player.observe_property('pause', self._on_pause)

        # 通用定时器：更新播放位置与时长
        self._timer = QTimer(self)
        self._timer.setInterval(200)
        self._timer.timeout.connect(self._update_playback_info)

        # 离线峰值同步定时器（当真实峰值不可用时使用）
        self._peak_timer = QTimer(self)
        self._peak_timer.setInterval(100)
        self._peak_timer.timeout.connect(self._emit_current_peak)

    def _init_peak_support(self):
        """尝试启用 mpv 内置的音频峰值回调（一次性）"""
        try:
            # 某些版本需要设置 audio-peak-detection 选项
            self.player = mpv.MPV(video=False)  # 临时测试对象
            self.player['audio-peak-detection'] = True
            self.player.observe_property('audio-peak', self._on_peak)
            self._peak_supported = True
            self.player.terminate()  # 测试完毕销毁
            logger.info("mpv 原生音频峰值检测已启用")
        except Exception:
            self._peak_supported = False
            logger.warning("mpv 不支持原生音频峰值，将使用预分析数据")
        finally:
            # 无论成功与否，重新创建正式的播放器实例
            self.player = mpv.MPV(
                video=False,
                audio_display=False,
                input_default_bindings=False,
                input_vo_keyboard=False,
            )

    # ---------- 公共接口 ----------
    def play_song(self, song: SongItem):
        """播放指定歌曲，并启动峰值同步"""
        if not song or not song.file_path:
            return
        self._current_song = song
        self.player.play(song.file_path)
        self._is_playing = True
        self._timer.start()
        self.current_song_changed.emit(song)

        # 根据真实峰值支持情况决定是否启动离线定时器
        if not self._peak_supported:
            self._peak_timer.start()
        # 如果真实峰值可用，_on_peak 会自动发射信号，无需定时器

    def toggle_play_pause(self):
        """切换播放/暂停"""
        self.player.pause = not self.player.pause

    def stop(self):
        """停止播放，清理定时器"""
        self.player.stop()
        self._timer.stop()
        self._peak_timer.stop()
        self._is_playing = False
        self._current_song = None

    def set_volume(self, volume: int):
        """设置音量 0-100"""
        self.player.volume = max(0, min(100, volume))

    def seek(self, seconds: float):
        """跳转到指定秒数"""
        if self._current_song:
            self.player.seek(seconds, 'absolute')

    def enable_dynaudnorm(self, enabled: bool):
        """启用/禁用动态响度均衡，并可能切换峰值数据源"""
        if enabled and not self._dynaudnorm_enabled:
            self.player.af = ""
            self.player.command('af', 'add', 'dynaudnorm')
            self._dynaudnorm_enabled = True
        elif not enabled and self._dynaudnorm_enabled:
            self.player.af = ""
            self._dynaudnorm_enabled = False

    @property
    def current_song(self):
        return self._current_song

    @property
    def is_playing(self):
        return self._is_playing

    # ---------- 内部槽 ----------
    def _update_playback_info(self):
        """更新播放位置与总时长（由 _timer 调用）"""
        try:
            pos = self.player.time_pos
            dur = self.player.duration
            if pos is not None:
                self.position_changed.emit(int(pos * 1000))
            if dur is not None:
                self.duration_changed.emit(int(dur * 1000))
        except Exception:
            pass

    def _on_peak(self, name, value):
        """mpv 原生音频峰值回调（仅在支持时使用）"""
        if value is None:
            return
        if isinstance(value, list):
            peak = max(value) if value else 0.0
        else:
            peak = float(value)
        self.peak_changed.emit(peak)

    def _emit_current_peak(self):
        """从预分析的峰值数组中取出当前时刻的峰值（离线方式）"""
        if not self._current_song:
            return
        try:
            pos = self.player.time_pos  # 秒
            if pos is None:
                return
            # 根据均衡状态选择数据源
            if self._dynaudnorm_enabled and self._current_song.peaks_balanced:
                peaks = self._current_song.peaks_balanced
            else:
                peaks = self._current_song.peaks_normal
            if not peaks:
                return
            frame_ms = 100
            idx = int(pos * 1000 / frame_ms)
            if 0 <= idx < len(peaks):
                self.peak_changed.emit(peaks[idx])
        except Exception:
            pass

    def _on_pause(self, name, value):
        """监听暂停状态变化，同步播放状态信号和定时器"""
        if value is True:
            self.state_changed.emit("paused")
            self._is_playing = False
            self._timer.stop()
            self._peak_timer.stop()
        elif value is False:
            self.state_changed.emit("playing")
            self._is_playing = True
            self._timer.start()
            # 仅当使用离线峰值时恢复定时器
            if not self._peak_supported:
                self._peak_timer.start()
        else:  # None 表示停止
            self.state_changed.emit("stopped")
            self._is_playing = False
            self._timer.stop()
            self._peak_timer.stop()