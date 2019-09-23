from typing import List

from PyQt5.QtCore import QMargins, pyqtSignal
from PyQt5.QtWidgets import QGridLayout, QVBoxLayout, QHBoxLayout, QSpinBox, QLabel, QWidget

from margins import Margins


class QMarginsEdit(QWidget):
    valueChanged = pyqtSignal(Margins, name='valueChanged')

    def __init__(self, parent):
        super(QMarginsEdit, self).__init__(parent)
        self.boxes = []
        layout_x = QVBoxLayout()

        for x in range(0, 3):
            layout_y = QHBoxLayout()
            for y in range(0, 3):
                if (x ^ y) & 1:
                    spin_box = QSpinBox(self)
                    spin_box.setMaximum(255)
                    spin_box.setMinimum(-255)
                    spin_box.valueChanged.connect(lambda _: self.valueChanged.emit(self.margins()))
                    layout_y.addWidget(spin_box)
                    self.boxes.append(spin_box)
                else:
                    layout_y.addWidget(QLabel(self))
            layout_x.addLayout(layout_y)
        self.setLayout(layout_x)

    def margins(self) -> Margins:
        if len(self.boxes) < 4:
            return Margins()
        return Margins(self.boxes[0].value(),
                       self.boxes[1].value(),
                       self.boxes[2].value(),
                       self.boxes[3].value())

    def setMargins(self, margins: Margins):
        self.boxes[0].setValue(margins.top)
        self.boxes[1].setValue(margins.left)
        self.boxes[2].setValue(margins.right)
        self.boxes[3].setValue(margins.bottom)