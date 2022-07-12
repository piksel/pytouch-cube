from PyQt6.QtCore import pyqtSignal, Qt, QModelIndex
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QStandardItemModel
from PyQt6.QtWidgets import QTreeView, QWidget, QTableView, QAbstractItemView, QHeaderView
from typing import *

from .printables_model import PrintablesModel


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
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.setDragDropOverwriteMode(False)
        self.verticalHeader().hide()
        self.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)
        # self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        # self.row

        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

    def item_from_index(self, index):
        return self.model().data(index)

    def dragEnterEvent(self, e: QDragEnterEvent) -> None:
        self.draggedItem = self.indexAt(e.position().toPoint())
        e.setDropAction(Qt.DropAction.MoveAction)
        super().dragEnterEvent(e)

    def dropEvent(self, e: QDropEvent) -> None:
        dropped_index = self.indexAt(e.position().toPoint())
        if not dropped_index.isValid():
            return

        old_row = self.draggedItem.row()
        self.model().moveRow(QModelIndex(), old_row, QModelIndex(), dropped_index.row())
