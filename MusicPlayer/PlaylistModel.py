from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, QDataStream, QIODevice
from SongItem import SongItem

class PlaylistModel(QAbstractListModel):
    def __init__(self):
        super().__init__()
        self.songs: list[SongItem] = []

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
        # 利用 default_flags 自身的类型和 | 操作
        new_flags = default_flags | Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled
        return new_flags

    def supportedDropActions(self):
        # ✅ 必须明确告知接受移动
        return Qt.DropAction.MoveAction

    def moveRows(self, sourceParent, sourceRow, count, destinationParent, destinationChild):
        print(f"moveRows called: sourceRow={sourceRow}, dest={destinationChild}")
        if sourceParent != destinationParent or count != 1:
            return False

        # 保存原始目标索引，供 beginMoveRows 使用
        originalDest = destinationChild

        # 计算数据列表中真正的插入位置（考虑移除源行后的偏移）
        if sourceRow < destinationChild:
            insert_pos = destinationChild - 1
        else:
            insert_pos = destinationChild

        # 1️⃣ 先通知视图即将移动
        self.beginMoveRows(sourceParent, sourceRow, sourceRow,destinationParent, originalDest)

        # 2️⃣ 执行实际数据移动

        song = self.songs.pop(sourceRow)
        self.songs.insert(insert_pos, song)

        # 3️⃣ 完成移动
        self.endMoveRows()
        return True

    def supportedDragActions(self):
        print("supportedDropActions called")
        return Qt.DropAction.MoveAction

    def mimeTypes(self):
        return ["application/x-qabstractitemmodeldatalist"]


    def mimeData(self, indexes):
        print("mimeData called, indexes:", [idx.row() for idx in indexes])
        return super().mimeData(indexes)

    def dropMimeData(self, data, action, row, column, parent):
        # 只处理移动操作
        if action != Qt.DropAction.MoveAction:
            return False
        if not data.hasFormat("application/x-qabstractitemmodeldatalist"):
            return False

        # 从 MIME 数据中提取被拖拽的源行索引
        encoded = data.data("application/x-qabstractitemmodeldatalist")
        stream = QDataStream(encoded, QIODevice.OpenModeFlag.ReadOnly)
        source_row = stream.readInt32()

        # 如果目标行无效，则追加到列表末尾
        if row == -1:
            row = self.rowCount()

        # 调用已有的 moveRows 方法执行移动
        return self.moveRows(QModelIndex(), source_row, 1, QModelIndex(), row)

