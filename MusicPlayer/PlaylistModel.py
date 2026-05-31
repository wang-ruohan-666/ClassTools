#PlaylistModel.py
from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, QByteArray, QDataStream, QIODevice, QVariantAnimation

from SongItem import SongItem


class PlaylistModel(QAbstractListModel):
    def __init__(self):
        super().__init__()
        self.songs: list[SongItem] = []
        # 交换动画相关（保留原动画代码）
        self.anim_source = -1
        self.anim_target = -1
        self.anim_progress = 0.0
        self._anim = None

    def remove_song(self, row: int):
        """删除指定行并通知视图"""
        if row < 0 or row >= len(self.songs):
            return
        self.beginRemoveRows(QModelIndex(), row, row)
        self.songs.pop(row)
        self.endRemoveRows()

    def clear(self):
        """清空列表"""
        if not self.songs:
            return
        self.beginRemoveRows(QModelIndex(), 0, len(self.songs) - 1)
        self.songs.clear()
        self.endRemoveRows()

    def to_export_data(self) -> list[dict]:
        """导出为可序列化的字典列表"""
        data = []
        for song in self.songs:
            data.append({
                "title": song.title,
                "author": song.author,
                "duration": song.duration,
                "file_path": song.file_path
            })
        return data

    def import_data(self, data: list[dict]):
        """从字典列表导入歌曲（需有 file_path）"""
        from MusicPlayer.GetSongInfo import get_song_info  # 避免循环导入，局部导入
        for item in data:
            path = item.get("file_path", "")
            if path:
                # 尝试从文件重新读取信息，如果失败则用导入数据填充
                try:
                    title, author, cover, duration = get_song_info(path)
                except Exception:
                    title = item.get("title", "")
                    author = item.get("author", "")
                    duration = item.get("duration", 0)
                    cover = None  # 无封面
                song = SongItem(title, author, cover, duration, path)
                self.add_song(song)

    def add_song(self, song: SongItem):
        row = len(self.songs)
        self.beginInsertRows(QModelIndex(), row, row)
        self.songs.append(song)
        self.endInsertRows()

    def rowCount(self, parent=QModelIndex()):
        return len(self.songs)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        song = self.songs[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            return song.title
        elif role == Qt.ItemDataRole.UserRole:
            return song.author
        elif role == Qt.ItemDataRole.UserRole + 1:
            return song.cover
        elif role == Qt.ItemDataRole.UserRole + 2:
            return song.duration
        return None

    def flags(self, index):
        default_flags = super().flags(index)
        if not index.isValid():
            return default_flags
        return default_flags | Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled

    def supportedDropActions(self):
        return Qt.DropAction.MoveAction

    def mimeTypes(self):
        return ["application/x-playlist-row"]  # 改为自定义格式

    def mimeData(self, indexes):
        """只编码第一个索引的行号到自定义 MIME 类型"""
        mime = super().mimeData(indexes)  # 保留父类处理（可为空）
        if not indexes:
            return mime
        data = QByteArray()
        stream = QDataStream(data, QIODevice.OpenModeFlag.WriteOnly)
        stream.writeInt32(indexes[0].row())
        mime.setData("application/x-playlist-row", data)
        return mime

    def moveRows(self, sourceParent, sourceRow, count, destinationParent, destinationChild):
        if sourceParent != destinationParent or count != 1:
            return False
        if sourceRow < 0 or sourceRow >= len(self.songs):
            return False
        # destinationChild 是源行被移除后，数据列表中的插入索引（已在 dropEvent 中正确计算）
        if destinationChild < 0 or destinationChild > len(self.songs):
            return False

        # 1. 移除源行
        self.beginRemoveRows(sourceParent, sourceRow, sourceRow)
        song = self.songs.pop(sourceRow)
        self.endRemoveRows()

        # 2. 插入到目标位置（此时数据列表已缩短，destinationChild 无需再调整）
        insert_row = destinationChild
        self.beginInsertRows(destinationParent, insert_row, insert_row)
        self.songs.insert(insert_row, song)
        self.endInsertRows()
        return True

    def swapRows(self, row1: int, row2: int):
        """启动交换动画，动画结束后真正交换数据"""
        if row1 == row2 or row1 < 0 or row2 < 0 or row1 >= len(self.songs) or row2 >= len(self.songs):
            return
        # 停止之前的动画（如果有）
        if self._anim and self._anim.state() == QVariantAnimation.State.Running:
            self._anim.stop()

        self.anim_source = row1
        self.anim_target = row2
        self.anim_progress = 0.0

        self._anim = QVariantAnimation()
        self._anim.setDuration(200)  # 动画时长 200ms
        self._anim.setStartValue(0.0)
        self._anim.setEndValue(1.0)
        self._anim.valueChanged.connect(self._on_anim_value_changed)
        self._anim.finished.connect(self._on_anim_finished)
        self._anim.start()  # 启动动画

    def _on_anim_value_changed(self, value):
        self.anim_progress = value
        # 通知视图刷新（只更新涉及的两个索引区域）
        if self.anim_source >= 0:
            top_left = self.index(min(self.anim_source, self.anim_target))
            bottom_right = self.index(max(self.anim_source, self.anim_target))
            self.dataChanged.emit(top_left, bottom_right, [Qt.ItemDataRole.DisplayRole])

    def _on_anim_finished(self):
        # 动画结束，真正交换数据
        if self.anim_source >= 0 and self.anim_target >= 0:
            self.songs[self.anim_source], self.songs[self.anim_target] = self.songs[self.anim_target], self.songs[self.anim_source]
            self.beginResetModel()
            self.endResetModel()
        # 清除动画状态
        self.anim_source = -1
        self.anim_target = -1
        self.anim_progress = 0.0