from PySide6.QtGui import QPixmap


class SongItem:
    def __init__(self, title: str, author: str, cover: QPixmap, duration: int):
        self.title = title
        self.author = author
        self.duration = duration
        self.cover = cover
