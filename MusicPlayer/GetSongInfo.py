import mutagen
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from mutagen import mp3, wave
from mutagen.flac import FLAC
from mutagen.id3 import APIC


def get_song_info(file_path):
    """返回 (title, artist, cover_pixmap ,duration_seconds)"""
    title = "未知歌曲"
    artist = "未知艺术家"
    duration = 0
    cover_pixmap = None

    try:
        audio = mutagen.File(file_path)
        if audio is None:
            return title, artist, cover_pixmap, duration

        # 时长（秒）
        if hasattr(audio.info, 'length'):
            duration = int(audio.info.length)

        # MP3 文件
        if isinstance(audio, mutagen.mp3.MP3) and audio.tags:
            title = audio.tags.get('TIT2', [title])[0]
            artist = audio.tags.get('TPE1', [artist])[0]
            for tag in audio.tags.values():
                if isinstance(tag, APIC):
                    cover_pixmap = QPixmap()
                    cover_pixmap.loadFromData(tag.data)
                    break

        # FLAC 文件
        elif isinstance(audio, mutagen.flac.FLAC):
            title = audio.get('title', [title])[0]
            artist = audio.get('artist', [artist])[0]
            if audio.pictures:
                cover_pixmap = QPixmap()
                cover_pixmap.loadFromData(audio.pictures[0].data)

        elif isinstance(audio, mutagen.wave.WAVE):
            title = audio.tags.get('TIT2', [title])[0] if 'TIT2' in audio.tags else title
            artist = audio.tags.get('TPE1', [artist])[0] if 'TPE1' in audio.tags else artist

        if cover_pixmap and not cover_pixmap.isNull():
            cover_pixmap = cover_pixmap.scaled(50, 50,
                                               Qt.AspectRatioMode.KeepAspectRatio,
                                               Qt.TransformationMode.SmoothTransformation)
    except Exception as e:
        print(f"解析文件失败：{file_path}，{e}")

    return title, artist, cover_pixmap, duration
