from enum import Enum, auto
from typing import *

from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QWidget

Color = Tuple[int, int, int]


class PrinterDevicesModel(QStandardItemModel):
    class Columns(Enum):
        Name = 0
        Source = 1

    def __init__(self, parent: QWidget):
        super().__init__(0, 2, parent)
        self.setHorizontalHeaderLabels([it.name for it in PrinterDevicesModel.Columns])

    def add(self, name: str, source: str = '') -> Tuple[QStandardItem, QStandardItem]:
        row = (QStandardItem(name), QStandardItem(source))
        self.appendRow(row)
        return row


class ItemType(Enum):
    Image = auto()
    Text = auto()
    Barcode = auto()

