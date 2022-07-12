import logging
from enum import Enum
from typing import *

from PyQt6.QtCore import Qt, QAbstractItemModel, QModelIndex, QVariant
from PyQt6.QtWidgets import QWidget

from printables.printable import Printable
PrintableData = Union[QVariant, Printable]

log = logging.getLogger(__name__)


class PrintablesModel(QAbstractItemModel):
    class Columns(Enum):
        Type = 0
        Data = 1

    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.items: List[Printable] = []

    def rowCount(self, index: QModelIndex = QModelIndex()):
        return len(self.items)

    def index(self, row, column, _parent=None) -> QModelIndex:
        if row < len(self.items):
            return self.createIndex(row, column, self.items[row])
        else:
            return QModelIndex()

    def parent(self, index):
        return QModelIndex()

    def columnCount(self, index: QModelIndex = QModelIndex()) -> int:
        if index.isValid():
            return index.internalPointer().columnCount()
        return 2

    def hasChildren(self, parent: QModelIndex = ...) -> bool:
        return False

    def setData(self, index: QModelIndex, value: PrintableData, role: Qt.ItemDataRole = Qt.ItemDataRole.EditRole) -> bool:
        return False
        # item = self.items[index.row()]

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> Optional[PrintableData]:
        if not index.isValid():
            return None
        item: Printable = index.internalPointer()
        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() == 0:
                return item.get_type()
            else:
                return item.get_name()
        if role == Qt.ItemDataRole.DecorationRole:
            if index.column() == 0:
                return item.get_icon()
            elif index.column() == 1:
                re = item.get_render_error()
                if re is not None:
                    return Printable.get_error_icon()

        if role == Qt.ItemDataRole.EditRole:
            if index.column() == 1:
                return item.get_name()
        return None

    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole) -> QVariant:
        if role == Qt.ItemDataRole.DisplayRole:
            try:
                if orientation == Qt.Orientation.Vertical:
                    return QVariant(str(section))
                else:
                    return PrintablesModel.Columns(section).name
            except Exception as x:
                log.error(
                    f'Could not get header data for section {section}, in orientation {orientation}, with role {role}',
                    exc_info=x)
                return QVariant('')

    def add(self, item: Printable):
        row_index = self.rowCount()
        self.beginInsertRows(QModelIndex(), row_index, row_index)
        self.items.append(item)
        self.endInsertRows()

    def removeRow(self, row: int, parent: QModelIndex = ...) -> bool:
        if row >= len(self.items) or row < 0:
            return False

        self.beginRemoveRows(QModelIndex(), row, row)
        del self.items[row]
        self.endRemoveRows()

    def moveRow(self, _: QModelIndex, src_row: int, __: QModelIndex, dst_row: int) -> bool:
        max_row = len(self.items)
        if src_row >= max_row or dst_row >= max_row or src_row < 0 or dst_row < 0:
            return False

        log.debug(f'Moving row {src_row} to {dst_row}')

        # Still unclear how this makes sense...
        qmodel_dst_row = dst_row + 1 if src_row < dst_row else dst_row

        if self.beginMoveRows(_, src_row, src_row, __, qmodel_dst_row):
            self.items.insert(dst_row, self.items.pop(src_row))
            self.endMoveRows()
            return True

        return False

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        default = super().flags(index)
        return Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled | Qt.ItemFlag(default)

    def supportedDragActions(self) -> Qt.DropAction:
        return Qt.DropAction.MoveAction

    def supportedDropActions(self) -> Qt.DropAction:
        return Qt.DropAction.MoveAction

    def clear(self):
        log.debug(f'Clearing {len(self.items)} items')
        self.beginResetModel()
        self.items.clear()
        self.endResetModel()
