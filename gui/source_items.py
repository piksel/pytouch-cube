import logging

from PyQt6.QtCore import pyqtSignal, QModelIndex
from PyQt6.QtWidgets import QGroupBox, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QMenu

from printables.printable import Printable
from .item_view import ItemView
from printables import Barcode, Image, QrCode, Spacing, Text

log = logging.getLogger(__name__)


class SourceItems(QGroupBox):
    item_selected = pyqtSignal(Printable, name='item_selected')
    items_changed = pyqtSignal(name='item_selected')

    def __init__(self, parent: QWidget):
        super().__init__('Source items:', parent)

        self.table = ItemView(self)
        self.items = self.table.items
        self.items.rowsMoved.connect(self.tree_view_reorder)

        self.table.clicked.connect(self.tree_view_clicked)
        self.table.rowMoved.connect(self.tree_view_reorder)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        buttons = QHBoxLayout()

        add_menu = QMenu(self)
        add_menu.addAction(Text.get_add_add_action(self))
        add_menu.addAction(Image.get_add_add_action(self))
        add_menu.addAction(Barcode.get_add_add_action(self))
        add_menu.addAction(QrCode.get_add_add_action(self))

        add_menu.addSeparator()
        add_menu.addAction(Spacing.get_add_add_action(self))

        add_button = QPushButton('Add')
        add_button.setMenu(add_menu)
        buttons.addWidget(add_button)

        # buttons.addWidget(add_text_button)
        # buttons.addWidget(add_barcode_button)
        buttons.addStretch()
        buttons.setSpacing(1)

        b_down = QPushButton('Move down')
        # b_down = QPushButton('⬇︎')
        b_down.clicked.connect(lambda _: self.move_item(1))
        b_up = QPushButton('Move up')
        # b_up = QPushButton('⬆︎')
        b_up.clicked.connect(lambda _: self.move_item(-1))
        b_delete = QPushButton('Delete')
        b_delete.clicked.connect(self.delete_item)

        b_clone = QPushButton('Copy')
        b_clone.clicked.connect(self.on_clone)

        buttons.addWidget(b_clone)
        buttons.addSpacing(10)
        buttons.addWidget(b_up)
        buttons.addWidget(b_down)
        buttons.addSpacing(10)
        buttons.addWidget(b_delete)

        layout.addLayout(buttons)
        self.setLayout(layout)

    def add_item(self, item: Printable):
        self.items.add(item)
        self.table.selectRow(len(self.items.items) - 1)
        self.item_selected.emit(item)
        self.items_changed.emit()

    def move_item(self, direction):

        current = self.table.currentIndex()
        old = current.row()
        new = current.row() + direction
        if new < 0 or new >= self.items.rowCount():
            log.warning('cannot move from', old, 'to', new)
            return
        log.debug(f'Moving {old} to {new}')
        if not self.items.moveRow(QModelIndex(), old, QModelIndex(), new):
            log.warning('Failed to move row')

    def on_clone(self):
        current = self.table.currentIndex()
        if not current.isValid() or current.row() < 0:
            return
        original = current.internalPointer()
        copy = original.__class__(original.data.clone())
        self.add_item(copy)

    def delete_item(self):
        current = self.table.currentIndex()
        if not current.isValid() or current.row() < 0:
            return
        self.items.removeRow(current.row())
        self.items_changed.emit()

    def tree_view_reorder(self, old, new):
        self.items_changed.emit()

    def tree_view_clicked(self, index):
        row = index.row()
        if row < 0 or row > len(self.items.items):
            item = None
        else:
            item = self.items.items[row]
        self.item_selected.emit(item)

    def update_current_item(self):
        index = self.table.currentIndex()
        self.items.dataChanged.emit(index, index)
