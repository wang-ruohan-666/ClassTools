# services/player_service.py
import os

# DLL 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ["PATH"] = project_root + os.pathsep + os.environ["PATH"]

from PySide6.QtCore import QObject, Signal, QTimer
import mpv
from MusicPlayer.SongItem import SongItem
from MusicPlayer.common.logger import get_logger

logger = get_logger(__name__)


class PlayerService(QObject):
    """基于 mpv 的音频播放服务，支持动态响度均衡与峰值监测"""

    position_changed = Signal(int)
    duration_changed = Signal(int)
    state_changed = Signal(str)
    current_song_changed = Signal(object)
    peak_changed = Signal(float)                     # 单峰值（兼容）
    compare_peaks_changed = Signal(float, float)     # 双峰值：原始, 均衡后

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_song = None
        self._is_playing = False
        self._peak_supported = False

        # 创建播放器
        self.player = mpv.MPV(
            video=False,
            audio_display=False,
            input_default_bindings=False,
            input_vo_keyboard=False,
        )

        # ★ 先创建所有定时器，以防后续回调立即触发
        self._timer = QTimer(self)
        self._timer.setInterval(200)
        self._timer.timeout.connect(self._update_playback_info)

        self._peak_timer = QTimer(self)
        self._peak_timer.setInterval(100)
        self._peak_timer.timeout.connect(self._emit_current_peak)

        # 动态响度均衡
        self._dynaudnorm_enabled = True
        self.player.command(
            'af', 'add',
            'dynaudnorm=f=100:g=35:p=0.6:m=40:r=0.6'
        )
        # 尝试启用原生音频峰值（若 DLL 支持）
        try:
            self.player['audio-peak-detection'] = True
            self.player.observe_property('audio-peak', self._on_peak)
            self._peak_supported = True
            logger.info("mpv 原生音频峰值检测已启用")
        except Exception:
            logger.warning("mpv 不支持原生音频峰值，将使用预分析数据")

        # 最后监听暂停状态（此时定时器已存在，回调安全）
        self.player.observe_property('pause', self._on_pause)

    # ---------- 公共接口 ----------
    def play_song(self, song: SongItem):
        if not song or not song.file_path:
            return
        self._current_song = song
        self.player.play(song.file_path)
        self._is_playing = True
        self._timer.start()
        self.current_song_changed.emit(song)

        if not self._peak_supported:
            self._peak_timer.start()

    def toggle_play_pause(self):
        self.player.pause = not self.player.pause

    def stop(self):
        self.player.stop()
        self._timer.stop()
        self._peak_timer.stop()
        self._is_playing = False
        self._current_song = None

    def set_volume(self, volume: int):
        self.player.volume = max(0, min(100, volume))

    def seek(self, seconds: float):
        if self._current_song:
            self.player.seek(seconds, 'absolute')

    def enable_dynaudnorm(self, enabled: bool):
        if enabled and not self._dynaudnorm_enabled:
            self.player.af = ""
            self.player.command(
                'af', 'add',
                'dynaudnorm=f=100:g=35:p=0.6:m=40:r=0.6'
            )
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
        if value is None:
            return
        peak = max(value) if isinstance(value, list) else float(value)
        self.peak_changed.emit(peak)

    def _emit_current_peak(self):
        if not self._current_song:
            return
        try:
            pos = self.player.time_pos
            if pos is None:
                return
            frame_ms = 100
            idx = int(pos * 1000 / frame_ms)
            orig = 0.0
            bal = 0.0
            if self._current_song.peaks_normal and 0 <= idx < len(self._current_song.peaks_normal):
                orig = self._current_song.peaks_normal[idx]
            if self._current_song.peaks_balanced and 0 <= idx < len(self._current_song.peaks_balanced):
                bal = self._current_song.peaks_balanced[idx]

            # 发射两个信号
            self.peak_changed.emit(bal if self._dynaudnorm_enabled else orig)
            self.compare_peaks_changed.emit(orig, bal)
        except Exception:
            pass


    def _on_pause(self, name, value):
        if value is True:
            self.state_changed.emit("paused")
            self._is_playing = False
            self._timer.stop()
            self._peak_timer.stop()
        elif value is False:
            self.state_changed.emit("playing")
            self._is_playing = True
            self._timer.start()
            if not self._peak_supported:
                self._peak_timer.start()
        else:  # None = stopped
            self.state_changed.emit("stopped")
            self._is_playing = False
            self._timer.stop()
            self._peak_timer.stop()