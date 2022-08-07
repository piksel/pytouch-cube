from enum import Enum, auto
from typing import *

from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QWidget

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

