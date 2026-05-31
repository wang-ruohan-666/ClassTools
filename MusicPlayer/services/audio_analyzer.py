# services/audio_analyzer.py
import sys
import subprocess
import tempfile
import os
import numpy as np
import soundfile as sf
import threading
from PySide6.QtCore import QObject, Signal

class PeakAnalyzer(QObject):
    """在后台线程中分析音频峰值，支持同时分析原始和均衡后版本"""
    finished = Signal(str, list)                # 文件路径, 峰值列表（兼容单线）
    finished_both = Signal(str, list, list)     # 文件路径, 原始峰值列表, 均衡后峰值列表
    error = Signal(str, str)                    # 文件路径, 错误信息

    def __init__(self, frame_ms=100, parent=None):
        super().__init__(parent)
        self.frame_ms = frame_ms

    def analyze_both(self, file_path):
        """同时分析原始和均衡后峰值，通过 finished_both 返回结果"""
        threading.Thread(target=self._run_both_analysis, args=(file_path,), daemon=True).start()

    def _run_both_analysis(self, file_path):
        try:
            orig_peaks = self._analyze_file(file_path, apply_dynaudnorm=False)
            bal_peaks = self._analyze_file(file_path, apply_dynaudnorm=True)
            self.finished_both.emit(file_path, orig_peaks, bal_peaks)
        except Exception as e:
            self.error.emit(file_path, str(e))

    def analyze(self, file_path):
        """分析单个文件（兼容旧接口）"""
        threading.Thread(target=self._run_single_analysis, args=(file_path,), daemon=True).start()

    def _run_single_analysis(self, file_path):
        try:
            peaks = self._analyze_file(file_path, apply_dynaudnorm=False)
            self.finished.emit(file_path, peaks)
        except Exception as e:
            self.error.emit(file_path, str(e))

    def _analyze_file(self, file_path, apply_dynaudnorm):
        analysis_path = file_path
        tmp_file = None
        try:
            if apply_dynaudnorm:
                tmp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                tmp_file.close()
                cmd = [
                    "ffmpeg", "-y", "-i", file_path,
                    "-af", "dynaudnorm=f=100:g=35:p=0.6:m=40:r=0.6",
                    "-f", "wav", tmp_file.name
                ]
                # 关键：隐藏控制台窗口
                creationflags = 0
                if sys.platform == "win32":
                    creationflags = subprocess.CREATE_NO_WINDOW
                subprocess.run(cmd, check=True,
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL,
                               creationflags=creationflags)
                analysis_path = tmp_file.name

            # 读取音频数据
            data, rate = sf.read(analysis_path)
            if data.ndim == 1:
                data = data.reshape(-1, 1)

            # 计算每帧峰值
            frame_samples = int(rate * self.frame_ms / 1000)
            total_frames = len(data) // frame_samples + 1
            peaks = []
            for i in range(total_frames):
                start = i * frame_samples
                end = start + frame_samples
                chunk = data[start:end]
                if len(chunk) == 0:
                    break
                peak = np.max(np.abs(chunk))
                peaks.append(float(peak))
            return peaks
        finally:
            if tmp_file and os.path.exists(tmp_file.name):
                os.unlink(tmp_file.name)