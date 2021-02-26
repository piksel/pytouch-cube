from PyQt5.QtCore import pyqtSignal, Qt, QModelIndex
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QStandardItemModel
from PyQt5.QtWidgets import QTreeView, QWidget, QTableView, QAbstractItemView, QHeaderView
from typing import *

from .types import PrintablesModel


class ItemView(QTableView):
    rowMoved = pyqtSignal(int, int, name='rowMoved')

    def __init__(self, parent: Optional[QWidget]):
        super().__init__(parent)
        self.draggedItem = QModelIndex()

        self.items = PrintablesModel(self)
        self.setModel(self.items)

        # self.setRootIsDecorated(False)
        # self.tree_view.setAlternatingRowColors(True)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        # self.setDefaultDropAction(Qt.MoveAction)
        # self.setDragDropMode(QTreeView.InternalMove)
        # self.setItemsExpandable(False)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.setDragDropOverwriteMode(False)
        # self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.DoubleClicked)
        # self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        # self.row

        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)

    def item_from_index(self, index):
        return self.model().data(index)

    def dragEnterEvent(self, e: QDragEnterEvent) -> None:
        print('DRAAAAAAAAAAG')
        self.draggedItem = self.indexAt(e.pos())
        e.setDropAction(Qt.MoveAction)
        super().dragEnterEvent(e)

    def dropEvent(self, e: QDropEvent) -> None:
        dropped_index = self.indexAt(e.pos())
        if not dropped_index.isValid():
            return

        old_row = self.draggedItem.row()
        self.model().moveRow(QModelIndex(), old_row, QModelIndex(), dropped_index.row())
