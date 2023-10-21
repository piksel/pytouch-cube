from pprint import pprint

from PyQt6.QtCore import QDir, Qt
from PyQt6.QtWidgets import QComboBox
from qasync import asyncSlot

from labels import tapes
from util import *
from .types import *


class TapeModel(QStandardItemModel):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.colors: List[Tuple[Color, Color]] = []

    def add_tape(self, label, fg, bg):
        self.colors.append((fg, bg))
        self.appendRow(QStandardItem(label))


class TapeSelect(QComboBox):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        if hasattr(self, 'setPlaceholderText'):
            self.setPlaceholderText('Select tape type')
        self.model = TapeModel(self)
        for label, fg, bg in tapes:
            self.model.add_tape(label, fg, bg)
        self.setModel(self.model)

        index = self.findText('TZe-231,', Qt.MatchFlag.MatchStartsWith)
        if index > 0:
            self.setCurrentIndex(index)

    def get_colors(self, index: int):
        return self.model.colors[index]

