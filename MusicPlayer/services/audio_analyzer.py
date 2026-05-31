# services/audio_analyzer.py
import os
import subprocess
import tempfile

import numpy as np
import soundfile as sf
from PySide6.QtCore import QObject, Signal


class PeakAnalyzer(QObject):
    """在子线程中分析音频峰值（支持均衡前后对比）"""
    finished = Signal(str, list)   # 文件路径, 峰值列表
    error = Signal(str, str)

    def __init__(self, apply_dynaudnorm=False, frame_ms=100):
        super().__init__()
        self.apply_dynaudnorm = apply_dynaudnorm
        self.frame_ms = frame_ms   # 每帧时长（毫秒）

    def analyze(self, file_path):
        try:
            # 1. 如果需要均衡，用 ffmpeg 导出处理后的临时 WAV
            if self.apply_dynaudnorm:
                tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                tmp.close()
                cmd = [
                    "ffmpeg", "-y", "-i", file_path,
                    "-af", "dynaudnorm",
                    "-f", "wav", tmp.name
                ]
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                analysis_path = tmp.name
            else:
                analysis_path = file_path

            # 2. 读取音频数据
            data, rate = sf.read(analysis_path)  # data shape: (samples, channels)
            if data.ndim == 1:
                data = data.reshape(-1, 1)

            # 3. 计算每帧的峰值
            frame_samples = int(rate * self.frame_ms / 1000)
            total_frames = len(data) // frame_samples + 1
            peaks = []
            for i in range(total_frames):
                start = i * frame_samples
                end = start + frame_samples
                chunk = data[start:end]
                if len(chunk) == 0:
                    break
                # 取所有声道的最大绝对值作为峰值
                peak = np.max(np.abs(chunk))
                peaks.append(float(peak))

            # 4. 清理临时文件
            if self.apply_dynaudnorm and analysis_path != file_path:
                try:
                    os.unlink(analysis_path)
                except OSError:
                    pass

            self.finished.emit(file_path, peaks)
        except Exception as e:
            self.error.emit(file_path, str(e))