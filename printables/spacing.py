from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import QLabel, QSpinBox

from labelmaker import USABLE_HEIGHT
from typing import Optional
from margins import Margins
from printables.printable import Printable, PrintableData
from printables.propsedit import PropsEdit


class SpacingData(PrintableData):

    def __init__(self, width=10):
        super().__init__(Margins())
        self.width = width

    def clone(self):
        return SpacingData(self.width)

    def set_from(self, source):
        self.width = source.width

    def __str__(self):
        return '<SpacingData [{0}]>'


class SpacingPropsEdit(PropsEdit):

    data: SpacingData

    def __init__(self, data: SpacingData, parent, printable):
        super().__init__(data, parent, printable, default_props=False)
        self.setMinimumWidth(256)

        self.edit_width = QSpinBox(self)
        self.edit_width.setValue(self.data.width)
        self.layout.addWidget(QLabel('Width:'))
        self.layout.addWidget(self.edit_width)
        self.edit_width.valueChanged.connect(self.on_width_changed)

        self.layout.addStretch()

    def on_width_changed(self):
        self.save()

    def serialize(self, clone=False):
        data = self.data
        if clone:
            data = SpacingData()
        data.width = self.edit_width.value()


class Spacing(Printable):

    def __init__(self, data: Optional[SpacingData] = None):
        if data is None:
            data = SpacingData()
        self.data = data

    def get_name(self):
        return 'Spacing ({0}px)'.format(self.data.width)

    def get_props_editor(self, parent):
        return SpacingPropsEdit(self.data, parent, self)

    def render(self):
        d = self.data

        width = d.width
        print(width)
        img = QImage(width, USABLE_HEIGHT, QImage.Format.Format_ARGB32)
        img.fill(0xffffffff)
        return img
