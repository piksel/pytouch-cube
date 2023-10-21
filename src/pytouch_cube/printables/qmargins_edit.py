from typing import Type, TypeVar, Optional

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QSpinBox, QLabel, QWidget, QLayout, \
    QAbstractSpinBox, QDoubleSpinBox

from pytouch_cube.margins import Margins


class QPercentSpinBox(QDoubleSpinBox):
    def __init__(self, parent: Optional[QWidget]):
        super(QPercentSpinBox, self).__init__(parent)

    def textFromValue(self, v: float) -> str:
        return f'{v * 100:.0f}%'

    def valueFromText(self, text: str) -> float:
        v = float(text.strip('% '))
        return 0 if v == 0 else v / 100


TBox = TypeVar('TBox', QSpinBox, QPercentSpinBox)


class QMarginsEdit(QWidget):
    valueChanged = pyqtSignal(Margins, name='valueChanged')

    def __init__(self, parent, legacy_layout=False):
        super(QMarginsEdit, self).__init__(parent)
        self.boxes = []

        if legacy_layout:
            self.create_direction_box_layout()
        else:
            rows_layout = QVBoxLayout()

            margins_layout = QHBoxLayout()
            self.margin_left = self.create_box(margins_layout, 'Left:')
            self.margin_top = self.create_box(margins_layout, 'Top:')
            self.margin_right = self.create_box(margins_layout, 'Right:')
            rows_layout.addLayout(margins_layout)
            
            self.scale = self.create_box(rows_layout, 'Scale:', QPercentSpinBox)
            self.scale.setStepType(QAbstractSpinBox.StepType.AdaptiveDecimalStepType)
            self.setLayout(rows_layout)

            self.boxes = [self.margin_top, self.margin_left, self.margin_right]

    def on_box_value_changed(self):
        self.valueChanged.emit(self.margins())

    def create_box(self, col_layout: QLayout, label: str,
                   box_factory: Type[TBox] = QSpinBox) -> TBox:
        layout = QVBoxLayout()
        box = box_factory(self)
        box.setMaximum(512)
        box.setMinimum(-512)
        layout.addWidget(QLabel(label, self))
        layout.addWidget(box)
        col_layout.addLayout(layout)
        box.setMinimumWidth(50)
        box.valueChanged.connect(self.on_box_value_changed)
        return box

    def create_direction_box_layout(self):
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

        vert_main = self.boxes[0]
        vert_flwr = self.boxes[3]
        vert_flwr.setDisabled(True)
        vert_flwr.valueChanged.disconnect()
        vert_main.valueChanged.connect(lambda v: vert_flwr.setValue(0 - v))

    def margins(self) -> Margins:
        if len(self.boxes) < 3:
            return Margins()

        # scale_percent = self.scale.value()
        # scale = .0 if scale_percent == 0 else scale_percent / 100

        return Margins(self.boxes[0].value(),
                       self.boxes[1].value(),
                       self.boxes[2].value(),
                       self.scale.value())

    def setMargins(self, margins: Margins):
        self.boxes[0].setValue(margins.vert)
        self.boxes[1].setValue(margins.left)
        self.boxes[2].setValue(margins.right)
        self.scale.setValue(margins.scale)
        # self.boxes[3].setValue(margins.bottom)
