from PySide6.QtGui import QPixmap


class SongItem:
    def __init__(self, title, author, cover, duration, file_path=""):
        self.title = title
        self.author = author
        self.cover = cover          # QPixmap
        self.duration = duration    # 秒
        self.file_path = file_path  # 原始音频文件路径
